#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : utils
# @Time         : 2024/12/25 18:13
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

from meutils.caches.redis_cache import cache, cache_inmemory
from meutils.db.orm import select_first
from meutils.schemas.db.oneapi_types import OneapiTask, OneapiUser, OneapiToken


@cache(ttl=15 * 24 * 3600)
async def token2user(api_key: str):
    filter_kwargs = {
        "key": api_key.removeprefix("sk-"),
    }
    # logger.debug(filter_kwargs)
    return await select_first(OneapiToken, filter_kwargs)


@alru_cache(ttl=60)
async def get_user_quota(api_key: Optional[str] = None, user_id: Optional[int] = None):
    assert any([api_key, user_id]), "api_key or user_id must be provided."

    if not user_id:
        token_object = await token2user(api_key)
        user_id = token_object.user_id

    filter_kwargs = {
        "id": user_id
    }
    user_object = await select_first(OneapiUser, filter_kwargs)
    # logger.debug(user_object)
    return user_object.quota / 500000


if __name__ == '__main__':
    with timer():
        # arun(token2user('sk-m7hnpyLWVSqQN1NUjj9I50RQqmROGF80t0aq8l1yVwekKNCA'))
        arun(get_user_quota('sk-m7hnpyLWVSqQN1NUjj9I50RQqmROGF80t0aq8l1yVwekKNCA'))
        # arun(get_user_quota(user_id=1))
