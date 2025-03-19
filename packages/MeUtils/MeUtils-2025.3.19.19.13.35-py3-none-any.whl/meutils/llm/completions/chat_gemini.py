#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : gemini
# @Time         : 2025/2/14 17:36
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


from meutils.pipe import *
from meutils.llm.openai_utils import to_openai_params
from meutils.llm.clients import AsyncOpenAI

from meutils.schemas.openai_types import chat_completion, chat_completion_chunk, CompletionRequest, CompletionUsage

"""
image => file

      "type": "image_url",
      "image_url": {
          

"""


class Completions(object):

    def __init__(self,
                 base_url: Optional[str] = None,
                 api_key: Optional[str] = None
                 ):
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    async def create(self, request: CompletionRequest):
        urls = sum(request.last_urls.values(), [])
        for url in urls:
            request.messages[-1]["content"].append({"type": "image_url", "image_url": {"url": url}})

        data = to_openai_params(request)
        return await self.client.chat.completions.create(**data)


if __name__ == '__main__':
    url = "https://oss.ffire.cc/files/lipsync.mp3"
    url = "https://lmdbk.com/5.mp4"
    content = [
        {"type": "text", "text": "总结下"},
        # {"type": "image_url", "image_url": {"url": url}},

        {"type": "video_url", "video_url": {"url": url}}

    ]
    request = CompletionRequest(
        # model="qwen-turbo-2024-11-01",
        model="gemini-all",
        # model="qwen-plus-latest",

        messages=[
            {
                'role': 'user',

                'content': content
            },

        ],
        stream=False,
    )
    arun(Completions().create(request))
