# arpakit

import asyncio
import logging
from typing import Optional

from openai import OpenAI, AsyncOpenAI

_ARPAKIT_LIB_MODULE_VERSION = "3.0"

"""
https://platform.openai.com/docs/
"""


class OpenAIAPIClient:
    def __init__(
            self,
            *,
            open_ai: Optional[OpenAI] = None,
            async_open_ai: Optional[AsyncOpenAI] = None
    ):
        self._logger = logging.getLogger(self.__class__.__name__)

        self.open_ai = open_ai
        self.async_open_ai = async_open_ai

    def check_conn(self):
        self.open_ai.models.list()

    def is_conn_good(self) -> bool:
        try:
            self.check_conn()
            return True
        except Exception as e:
            self._logger.error(e)
        return False

    async def async_check_conn(self):
        await self.async_open_ai.models.list()

    async def async_is_conn_good(self) -> bool:
        try:
            await self.async_check_conn()
            return True
        except Exception as e:
            self._logger.error(e)
        return False


def __example():
    open_ai = OpenAI(api_key="your-api-key")
    client = OpenAIAPIClient(open_ai=open_ai)

    print("Checking OpenAI API connection...")
    if client.is_conn_good():
        print("Connection to OpenAI API is good")
    else:
        print("Failed to connect to OpenAI API")


async def __async_example():
    async_open_ai = AsyncOpenAI(api_key="your-api-key")
    client = OpenAIAPIClient(async_open_ai=async_open_ai)

    print("Checking OpenAI API async connection...")
    if await client.async_is_conn_good():
        print("Async connection to OpenAI API is good")
    else:
        print("Failed to async connect to OpenAI API")


if __name__ == '__main__':
    __example()
    asyncio.run(__async_example())
