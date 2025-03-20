import json
import traceback
from functools import partial
from httpx import HTTPStatusError
from openai import APIStatusError

from fastapi import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastapi.exceptions import RequestValidationError, HTTPException

from meutils.notice.feishu import send_message as _send_message

send_message = partial(
    _send_message,
    title=__name__,
    url="https://open.feishu.cn/open-apis/bot/v2/hook/d1c7b67d-b0f8-4067-a2f5-109f20eeb696"
)


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    # print(exc)
    content = {
        "error":
            {
                "message": f"{exc.detail}",
                "type": "http-error",
            }
    }
    return JSONResponse(
        content=content,
        status_code=exc.status_code
    )


async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={"message": str(exc)},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def chatfire_api_exception_handler(request: Request, exc: Exception):

    content = {
        "error":
            {
                "message": f"{exc}",
                "type": "cf-api-error",
            },

        "code": status.HTTP_500_INTERNAL_SERVER_ERROR
    }

    # 默认值
    reps = None
    if isinstance(exc, (HTTPStatusError, APIStatusError)):
        status_code = exc.response.status_code or 500

        content['code'] = status_code
        content['error']['message'] = f"{exc.response.text}"

        reps = JSONResponse(
            content=content,
            status_code=status_code,
        )

    # send_message
    content_detail = f"{traceback.format_exc()}"
    if any(code in content_detail for code in {'451', }):
        content_detail = ""

    send_message([content, content_detail])

    return reps or JSONResponse(
        content=content,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


if __name__ == '__main__':
    pass
