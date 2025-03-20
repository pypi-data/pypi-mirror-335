#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : common
# @Time         : 2025/3/3 16:54
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

import os

from aiocache.serializers import PickleSerializer
from aiocache import cached, Cache, RedisCache, caches

cache = memory_cache = cached


def rcache(**kwargs):
    """serializer="pickle"
    :param endpoint: str with the endpoint to connect to. Default is "127.0.0.1".
    :param port: int with the port to connect to. Default is 6379.
    :param db: int indicating database to use. Default is 0.
    :param password: str indicating password to use. Default is None.
    """
    if kwargs.get("serializer") == 'pickle':
        kwargs['serializer'] = PickleSerializer()

    connection_kwargs = {}
    if REDIS_URL := os.getenv("REDIS_URL"):
        user_password, base_url = REDIS_URL.split("@")
        endpoint, port = base_url.split(':')
        password = user_password.split(":")[-1]

        connection_kwargs['endpoint'] = endpoint
        connection_kwargs['port'] = port
        connection_kwargs['password'] = password

        # logger.debug(f"redis: {connection_kwargs}")

    return cached(
        cache=RedisCache,
        **connection_kwargs,
        **kwargs
    )


if __name__ == '__main__':
    from meutils.pipe import *


    @cache(ttl=10)
    async def fn(a):
        logger.debug(a)
        return a


    @cache(ttl=3)
    @rcache(ttl=2)
    async def mfn(a):
        logger.debug(a)
        return a


    async def main():
        for i in range(10):
            # await fn(11111)
            await mfn(11111)

            await asyncio.sleep(1)


    arun(main())
