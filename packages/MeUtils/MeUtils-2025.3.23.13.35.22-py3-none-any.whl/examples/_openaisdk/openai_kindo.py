#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_siliconflow
# @Time         : 2024/6/26 10:42
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import os

from meutils.pipe import *
from openai import OpenAI
from openai import OpenAI, APIStatusError


client = OpenAI(
    # base_url="https://free.chatfire.cn/v1",
    api_key="d17beace-2d47-432a-8d2e-89a03237b7d4-4c228b83994398b9",
    base_url="https://all.chatfire.cc/kindo/v1"

)

try:
    client.chat.completions.create(
        messages=[
            {"role": "user", "content": "你是谁"}
        ],
        model="azure/gpt-4o-mini",
    )
except Exception as e:
    print(e)