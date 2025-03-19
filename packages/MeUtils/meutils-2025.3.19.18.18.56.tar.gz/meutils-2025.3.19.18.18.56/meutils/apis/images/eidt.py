#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : eidt
# @Time         : 2025/1/7 13:27
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *


from meutils.pipe import *

from openai import OpenAI

client = OpenAI(
    base_url="https://ai.gitee.com/v1",
    api_key="WPCSA3ZYD8KBQQ2ZKTAPVUA059J2Q47TLWGB2ZMQ",
    default_headers={"X-Failover-Enabled": "true", "X-Package": "1910"},
)

response = client.images.edit(
    model="Kolors",
    prompt="笑起来",
    size="1024x1024",
    extra_body={
        "steps": 25,
        "guidance_scale": 6,
    },

    mask=open("test.png", "rb"),

    image=open("test.png", "rb"),
)