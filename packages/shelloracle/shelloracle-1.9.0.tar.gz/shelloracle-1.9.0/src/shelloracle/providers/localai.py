from __future__ import annotations

from typing import TYPE_CHECKING

from openai import APIError, AsyncOpenAI

from shelloracle.providers import Provider, ProviderError, Setting, system_prompt

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class LocalAI(Provider):
    name = "LocalAI"

    host = Setting(default="localhost")
    port = Setting(default=8080)
    model = Setting(default="mistral-openorca")

    @property
    def endpoint(self) -> str:
        return f"http://{self.host}:{self.port}"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Use a placeholder API key so the client will work
        self.client = AsyncOpenAI(api_key="sk-xxx", base_url=self.endpoint)

    async def generate(self, prompt: str) -> AsyncIterator[str]:
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except APIError as e:
            msg = f"Something went wrong while querying LocalAI: {e}"
            raise ProviderError(msg) from e
