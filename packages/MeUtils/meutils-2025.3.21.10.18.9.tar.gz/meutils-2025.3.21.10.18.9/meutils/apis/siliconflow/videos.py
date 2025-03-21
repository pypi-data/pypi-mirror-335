#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : videos
# @Time         : 2024/12/12 08:53
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import asyncio

from meutils.pipe import *
from meutils.caches.redis_cache import cache
from meutils.io.files_utils import to_url, to_url_fal
from meutils.llm.check_utils import check_token_for_siliconflow
from meutils.schemas.task_types import TaskResponse
from meutils.schemas.siliconflow_types import BASE_URL, VideoRequest
from meutils.config_utils.lark_utils import get_next_token_for_polling
from meutils.apis.translator import deeplx

from openai import OpenAI, AsyncOpenAI

FEISHU_URL_FREE = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=ICzCsC"

check_token = partial(check_token_for_siliconflow, threshold=0.01)

MODELS_MAP = {
    "hunyuan-video": "tencent/HunyuanVideo",
    "hunyuanvideo": "tencent/HunyuanVideo",
    "mochi-1-preview": "genmo/mochi-1-preview",
    "ltx-video": "Lightricks/LTX-Video",
}


@cache(ttl=7 * 24 * 3600)
async def create_task(request: VideoRequest, token: Optional[str] = None):
    token = token or await get_next_token_for_polling(FEISHU_URL_FREE, check_token=check_token, from_redis=True)

    payload = request.model_dump(exclude_none=True)
    payload["model"] = MODELS_MAP.get(request.model, "Lightricks/LTX-Video")

    if payload["model"] in {"genmo/mochi-1-preview", "Lightricks/LTX-Video"}:  # 中文不友好
        payload['prompt'] = (
            await deeplx.translate(deeplx.DeeplxRequest(text=request.prompt, target_lang="EN"))).get("data")

    client = AsyncOpenAI(
        base_url=BASE_URL,
        api_key=token
    )

    response = await client.post("/video/submit", body=payload, cast_to=object)
    logger.debug(response)

    task_id = response.get('requestId')
    return TaskResponse(task_id=task_id, system_fingerprint=token)


async def get_task(task_id, token: str):
    client = AsyncOpenAI(
        base_url=BASE_URL,
        api_key=token
    )
    payload = {"requestId": task_id}
    response = await client.post(f"/video/status", cast_to=object, body=payload)
    logger.debug(response)

    data = response.get("results") or {}

    for video in data.get("videos", []):
        video["url"] = await to_url_fal(video.get("url"))  # 异步执行

    return TaskResponse(
        task_id=task_id,
        data=data,
        status=response.get("status"),
        message=response.get("reason"),
    )


if __name__ == '__main__':
    token = None
    token = "sk-raapiguffsnsxgkfiwfusjmbpcyqoxhcohhxaybflrnvpqjw"

    request = VideoRequest(
        model="Lightricks/LTX-Video",
        prompt="这个女人笑起来",
        image='https://oss.ffire.cc/files/kling_watermark.png'  # 1148f2e4-0a62-4208-84de-0bf2c88f740d
    )
    # tokens = config_manager.text.split()

    # tokens_ = arun(check_token_for_siliconflow(tokens, threshold=0.01))

    # arun(create_task(request, token=token))

    # arun(get_task("fa248aac-00ec-4b00-a2f8-3d6bf1cea6d3", token))
    # arun(get_task("c716a328-438e-4612-aff2-a669034499cb", token))
    arun(get_task("1148f2e4-0a62-4208-84de-0bf2c88f740d", token))

    # token = "sk-oeptckzkhfzeidbtsqvbrvyrfdtyaaehubfwsxjytszbgohd"
    # arun(get_task("5ea22f57-45f0-425c-9d1e-bf3dae7e1e81", token))

    # arun(create_task(VideoRequest(model="tencent/HunyuanVideo", prompt="a dog in the forest."), token=token))
