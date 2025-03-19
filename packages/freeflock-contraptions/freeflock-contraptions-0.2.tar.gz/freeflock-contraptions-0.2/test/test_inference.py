import pytest
from pydantic import BaseModel

from packages.freeflock_contraptions.inference import OpenaiInference


@pytest.mark.asyncio
async def test_infer():
    inference_client = OpenaiInference()
    model_name = "o3-mini"
    system_prompt = "You are a helpful assistant."
    user_prompt = "What is the capital of France?"
    reasoning_effort = "low"
    result = await inference_client.infer(model_name, system_prompt, user_prompt, reasoning_effort)
    assert "paris" in result.lower()
    print(result)


@pytest.mark.asyncio
async def test_infer_json():
    inference_client = OpenaiInference()
    model_name = "o3-mini"
    system_prompt = "You are a helpful assistant."
    user_prompt = "What is the capital of France?"
    reasoning_effort = "low"
    result = await inference_client.infer_json(model_name, system_prompt, user_prompt, reasoning_effort, Capital)
    assert "paris" in result.capital.lower()
    print(result)


class Capital(BaseModel):
    capital: str
