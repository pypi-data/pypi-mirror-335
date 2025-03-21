from datetime import datetime, timedelta
import redis.asyncio as redis
from fastapi import Request, HTTPException
from starlette.responses import JSONResponse
import functools
from redis.exceptions import ConnectionError
from apilimity.logs import logger
import hmac
import hashlib
import base64
import secrets
import string
import time


class RateLimiter:
    def __init__(self):
        self.redis_client = None
        self.secret_key = None
        self.id_counter_key = "api_key:id_counter"

    async def init_redis(self, host, port, db, secret_key):
        try:
            self.redis_client = redis.Redis(host=host, port=port, db=db)
            self.secret_key = secret_key.encode()
        except ConnectionError as e:
            self.redis_client = None
            logger.error(f"APIlimity: Failed to connect to Redis: {e}")

    def _hash_key(self, key: str) -> str:
        hashed = hmac.new(self.secret_key, key.encode(), hashlib.sha256).digest()
        return base64.urlsafe_b64encode(hashed).decode()

    async def create_api_key(self, user: str, ttl: int = 60 * 60 * 24 * 30) -> str:
        if not self.redis_client or not self.secret_key:
            raise RuntimeError("Redis client is not initialized or secret key is missing")

        api_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        hashed_key = self._hash_key(api_key)

        key_id = await self.redis_client.incr(self.id_counter_key)
        created_at = int(time.time())
        expires_at = created_at + ttl

        key_data = {
            "id": key_id,
            "user": user,
            "created_at": created_at,
            "expires_at": expires_at
        }
        await self.redis_client.hset(f"api_key:{hashed_key}", mapping=key_data)
        await self.redis_client.expire(f"api_key:{hashed_key}", ttl)
        return api_key

    async def validate_api_key(self, api_key: str) -> bool:
        if not self.redis_client or not self.secret_key:
            return False

        hashed_key = self._hash_key(api_key)
        key_data = await self.redis_client.hgetall(f"api_key:{hashed_key}")
        return bool(key_data)

    async def get_all_api_keys(self):
        if not self.redis_client:
            raise RuntimeError("Redis client is not initialized")

        keys = []
        async for key in self.redis_client.scan_iter("api_key:*"):
            key_type = await self.redis_client.type(key)
            if key_type != b'hash':
                continue

            key_data = await self.redis_client.hgetall(key)
            if key_data:
                created_at = int(key_data[b'created_at'])
                expires_at = int(key_data[b'expires_at'])

                keys.append({
                    "id": int(key_data[b'id']),
                    "user": key_data[b'user'].decode(),
                    "created_at": datetime.fromtimestamp(created_at).isoformat(),
                    "expires_at": datetime.fromtimestamp(expires_at).isoformat()
                })

        return keys

    async def get_api_key_by_id(self, key_id: int):
        if not self.redis_client:
            raise RuntimeError("Redis client is not initialized")

        async for key in self.redis_client.scan_iter("api_key:*"):
            key_type = await self.redis_client.type(key)
            if key_type != b'hash':
                continue

            key_data = await self.redis_client.hgetall(key)
            if key_data and int(key_data.get(b'id')) == key_id:
                created_at = int(key_data[b'created_at'])
                expires_at = int(key_data[b'expires_at'])

                return {
                    "id": int(key_data[b'id']),
                    "user": key_data[b'user'].decode(),
                    "created_at": datetime.fromtimestamp(created_at).isoformat(),
                    "expires_at": datetime.fromtimestamp(expires_at).isoformat()
                }

        return {"key_id": key_id, "status": "API key not found or expired"}

    async def delete_api_key_by_id(self, key_id: int):
        if not self.redis_client:
            raise RuntimeError("Redis client is not initialized")

        async for key in self.redis_client.scan_iter("api_key:*"):
            key_type = await self.redis_client.type(key)
            if key_type != b'hash':
                continue

            key_data = await self.redis_client.hgetall(key)
            if key_data and int(key_data.get(b'id')) == key_id:
                await self.redis_client.delete(key)
                logger.info(f"API key with ID {key_id} deleted")
                return True

        return False

    async def update_api_key_ttl_by_id(self, key_id: int, new_ttl: int):
        if not self.redis_client:
            raise RuntimeError("Redis client is not initialized")

        async for key in self.redis_client.scan_iter("api_key:*"):
            key_type = await self.redis_client.type(key)
            if key_type != b'hash':
                continue

            key_data = await self.redis_client.hgetall(key)
            if key_data and int(key_data.get(b'id')) == key_id:
                await self.redis_client.expire(key, new_ttl)
                await self.redis_client.hset(key, "ttl", new_ttl)
                logger.info(f"API key with ID {key_id} TTL updated to {new_ttl}")
                return True

        return False

    def control(self, limit=None, period=None):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                if not self.redis_client:
                    logger.warning("APIlimity: Rate limiting disabled (Redis unavailable)")
                    return await func(request, *args, **kwargs)

                api_key = request.headers.get("Authorization")
                if not api_key or not api_key.startswith("Bearer "):
                    return JSONResponse(
                        content={"error": "API key is required"},
                        status_code=401
                    )

                api_key = api_key.split(" ")[1]
                valid = await self.validate_api_key(api_key)
                if not valid:
                    return JSONResponse(
                        content={"error": "Invalid API key"},
                        status_code=401
                    )

                if limit is None or period is None:
                    return await func(request, *args, **kwargs)

                # Лімітування запитів по ключу
                key = f"rate_limit:{self._hash_key(api_key)}"
                current = await self.redis_client.get(key)

                if current is None:
                    await self.redis_client.set(key, 1, ex=period)
                else:
                    current = int(current)
                    if current >= limit:
                        ttl = await self.redis_client.ttl(key)
                        logger.warning(f"Rate limit exceeded for key: {key}")
                        return JSONResponse(
                            content={
                                "error": "Rate limit exceeded",
                                "retry_after": ttl
                            },
                            status_code=429
                        )
                    await self.redis_client.incr(key)

                return await func(request, *args, **kwargs)

            return wrapper

        return decorator
