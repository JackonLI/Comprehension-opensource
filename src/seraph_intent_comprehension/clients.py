from __future__ import annotations

import asyncio
import itertools
import json
from dataclasses import dataclass

import websockets
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from seraph_intent_comprehension.config import RuntimeConfig


MODEL_NAME_ALIASES = {
    "qwen2.5-7b": "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4",
    "qwen2.5-32b": "Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4",
    "qwen2.5-72b": "Qwen/Qwen2.5-72B-Instruct-GPTQ-Int4",
    "llama3.1-8b": "meta-llama/Llama-3.1-8B-Instruct",
    "llama3.1-70b": "neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8",
}


@dataclass(frozen=True)
class LLMResponse:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class BaseLLMClient:
    def request(self, messages: list[dict[str, str]], model: str) -> LLMResponse:
        raise NotImplementedError


class OpenAICompatibleClient(BaseLLMClient):
    def __init__(self, config: RuntimeConfig) -> None:
        if not config.api_base_url:
            raise ValueError(
                "OpenAI-compatible provider requires SERAPH_API_BASE_URL "
                "or the --api-base-url argument."
            )
        keys = config.api_keys or ["EMPTY"]
        self._clients = [
            OpenAI(
                api_key=api_key,
                base_url=config.api_base_url,
                timeout=config.timeout_seconds,
            )
            for api_key in keys
        ]
        self._client_cycle = itertools.cycle(self._clients)

    @retry(
        wait=wait_random_exponential(min=1, max=10),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def request(self, messages: list[dict[str, str]], model: str) -> LLMResponse:
        client = next(self._client_cycle)
        completion = client.chat.completions.create(
            model=MODEL_NAME_ALIASES.get(model, model),
            messages=messages,
        )
        usage = completion.usage
        return LLMResponse(
            content=(completion.choices[0].message.content or "").strip(),
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
        )


class WebSocketGatewayClient(BaseLLMClient):
    def __init__(self, config: RuntimeConfig) -> None:
        if not config.ws_url:
            raise ValueError(
                "WebSocket provider requires SERAPH_WS_URL or the --ws-url argument."
            )
        self._ws_url = config.ws_url
        self._timeout_seconds = config.timeout_seconds

    async def _request_async(
        self, messages: list[dict[str, str]], model: str
    ) -> LLMResponse:
        payload = {"messages": messages, "model": model}
        async with websockets.connect(
            self._ws_url,
            open_timeout=self._timeout_seconds,
        ) as websocket:
            await websocket.send(json.dumps(payload))
            raw_response = await websocket.recv()
        response = json.loads(raw_response)
        usage = response.get("usage", {})
        return LLMResponse(
            content=response["choices"][0]["message"]["content"].strip(),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
        )

    @retry(
        wait=wait_random_exponential(min=1, max=10),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def request(self, messages: list[dict[str, str]], model: str) -> LLMResponse:
        return asyncio.run(self._request_async(messages, model))


def build_client(config: RuntimeConfig) -> BaseLLMClient:
    if config.provider == "openai":
        return OpenAICompatibleClient(config)
    if config.provider == "ws":
        return WebSocketGatewayClient(config)
    raise ValueError(f"Unsupported provider: {config.provider}")
