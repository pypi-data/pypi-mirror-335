from typing import Type

from openai import AsyncOpenAI
from pydantic import BaseModel


class OpenaiInference:
    def __init__(self):
        self.openai_client = AsyncOpenAI()

    async def infer(self,
                    model_name: str,
                    system_prompt: str,
                    user_prompt: str,
                    reasoning_effort: str) -> str:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        completion = await self.openai_client.chat.completions.create(
            messages=messages,
            model=model_name,
            reasoning_effort=reasoning_effort
        )
        return completion.choices[0].message.content

    async def infer_json(self,
                         model_name: str,
                         system_prompt: str,
                         user_prompt: str,
                         reasoning_effort: str,
                         response_format: Type[BaseModel]) -> BaseModel:
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        completion = await self.openai_client.beta.chat.completions.parse(
            response_format=response_format,
            messages=messages,
            model=model_name,
            reasoning_effort=reasoning_effort
        )
        return completion.choices[0].message.parsed
