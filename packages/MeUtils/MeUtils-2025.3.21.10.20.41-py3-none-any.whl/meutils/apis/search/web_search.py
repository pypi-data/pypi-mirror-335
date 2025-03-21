#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : web_search
# @Time         : 2025/3/18 20:15
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from aiostream import stream
from meutils.pipe import *
from meutils.async_utils import sync_to_async

from meutils.llm.clients import zhipuai_sdk_client
from meutils.schemas.openai_types import chat_completion, chat_completion_chunk, CompletionRequest, ChatCompletionChunk


def convert_citations(text):
    """
    # 示例使用
    text = "这是一段包含【1†source】和【2†source】的文本"
    result = convert_citations(text)
    print(result)  # 输出: 这是一段包含[^1]和[^2]的文本
    :param text:
    :return:
    """
    # 匹配【数字†source】格式的引用
    pattern = r'【(\d+)†source】'

    # 替换为[^数字]格式
    converted = re.sub(pattern, r'[^\1]', text)

    return converted


class Completions(object):

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @sync_to_async(thread_sensitive=False)
    def create(self, request: CompletionRequest):
        _ = self._create(request)
        for i in _:
            print(i)
        # return _

    async def search(self, q: str):
        return list(self._create(q))

    def _create(self, request: Union[CompletionRequest, str]):
        chunks = zhipuai_sdk_client.assistant.conversation(

            assistant_id="659e54b1b8006379b4b2abd6",  # 搜索智能体
            conversation_id=None,
            model="glm-4-assistant",  # assistant-ppt
            messages=[
                {
                    "role": "user",
                    "content": [{
                        "type": "text",
                        # "text": "北京未来七天气温，做个折线图",
                        # "text": "画条狗"
                        "text": request.last_user_content if isinstance(request, CompletionRequest) else request,

                    }]
                }
            ],
            stream=True,
            attachments=None,
            metadata=None
        )

        references = []
        buffer = []
        for chunk in chunks:
            delta = chunk.choices[0].delta
            if hasattr(delta, "tool_calls") and delta.tool_calls:
                tool_call = delta.tool_calls[0].model_dump()
                # logger.debug(tool_call)
                tool_type = tool_call.get("type", "")  # web_browser
                references += tool_call.get(tool_type, {}).get("outputs") or []  # title link content
                continue

            if isinstance(request, CompletionRequest):
                if references:
                    urls = [f"[^{i}]: [{ref['title']}]({ref['link']})\n" for i, ref in enumerate(references, 1)]
                    yield from urls
                    references = []

                # logger.debug(delta)
                # if delta.content.startswith('【') or buffer: # hasattr(delta, "content")
                #     buffer.append(delta.content)
                #     if len(buffer) < 20:
                #         continue
                #
                # if delta.content.endswith('】'):
                #     delta.content = convert_citations(''.join(buffer))
                #     if len(buffer) > 25: buffer = []

                delta = chat_completion_chunk.choices[0].delta.model_construct(**delta.model_dump())
                chat_completion_chunk.choices[0].delta = delta
                yield chat_completion_chunk

            else:
                yield references
                break


if __name__ == '__main__':
    model = "web-search-pro"
    # model = "tencent-search"

    request = CompletionRequest(
        # model="baichuan4-turbo",
        # model="xx",
        # model="deepseek-r1",
        # model="deepseek-r1:1.5b",
        model=model,

        # model="moonshot-v1-8k",
        # model="doubao",

        messages=[
            {"role": "user", "content": "《哪吒之魔童闹海》现在的票房是多少"}
        ],

        stream=True
    )
    # arun(Completions().search('周杰伦'))
    arun(Completions().create(request))
