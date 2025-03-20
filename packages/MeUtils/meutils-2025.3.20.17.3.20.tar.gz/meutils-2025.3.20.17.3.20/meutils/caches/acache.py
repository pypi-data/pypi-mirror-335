#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : acache
# @Time         : 2025/1/14 09:45
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import os

from meutils.pipe import *
from meutils.db.redis_db import async_pool

from aiocache import cached, Cache, RedisCache, caches
from aiocache import multi_cached
from meutils.schemas.image_types import ImageRequest

# logger.debug(async_pool.connection_kwargs)

REDIS_URL = "redis://:chatfirechatfire@110.42.51.143:6379"


def rcache(**kwargs):  # todo
    """
    :param endpoint: str with the endpoint to connect to. Default is "127.0.0.1".
    :param port: int with the port to connect to. Default is 6379.
    :param db: int indicating database to use. Default is 0.
    :param password: str indicating password to use. Default is None.
    """

    connection_kwargs = {}
    if REDIS_URL := os.getenv("REDIS_URL"):
        user_password, base_url = REDIS_URL.split("@")
        endpoint, port = base_url.split(':')
        password = user_password.split(":")[-1]

        connection_kwargs['endpoint'] = endpoint
        connection_kwargs['port'] = port
        connection_kwargs['password'] = password

    return cached(
        cache=RedisCache,
        **connection_kwargs,
        **kwargs
    )


@cached(ttl=60)
@cached(ttl=60)
async def cached_fc(user_id, **kwargs):
    logger.debug(user_id)
    return False


# global x
#
# key_builder = lambda *args, **kwargs: "key"
# key_builder = lambda *args, **kwargs: args[0].prompt
key_builder = lambda *args, **kwargs: args[1].prompt

def key_builder(*args, **kwargs):
    # print(args)
    return args[1].prompt


@rcache(ttl=11, key_builder=key_builder)
async def redis_fcc(user_id, **kwargs):
    logger.debug(user_id)
    # 1 / 0
    return False


# @multi_cached(ttl=60) # 多key缓存
# async def complex_function(user_id, **kwargs):
#     logger.debug(user_id)
#     return False


# Cache.MEMORY

# Cache.REDIS
# mcache = cached(ttl=60, cache=Cache.REDIS)(cached)
# from aiocache import Cache
#
# Cache(Cache.REDIS)
#
# rcache = Cache.from_url("redis://:chatfirechatfire@110.42.51.201:6379/11")
# print(rcache)


# @cached(ttl=60)
# @cached(ttl=15, cache=rcache)
# async def complex_function(user_id, **kwargs):
#     logger.debug(user_id)
#     return False
#

class A(BaseModel):
    a: Any = 111


import asyncio
from aiocache import cached
from aiocache.backends.redis import RedisCache
from aiocache.serializers import PickleSerializer


# 使用 @cached 装饰器缓存函数结果
@cached(cache=RedisCache, endpoint="127.0.0.1", port=6379, namespace="main",
        # serializer=PickleSerializer(),
        key="my_key", ttl=60)
async def expensive_operation():
    print("Performing expensive operation...")
    await asyncio.sleep(2)  # 模拟耗时操作
    return {"result": "data"}


if __name__ == '__main__':

    from aiocache import cached, Cache, RedisCache, caches


    async def main():
        for i in range(10):
            # logger.debug(i)

            await redis_fcc(ImageRequest(prompt=f'a cat {i}'))
            await asyncio.sleep(1)


    arun(main())
