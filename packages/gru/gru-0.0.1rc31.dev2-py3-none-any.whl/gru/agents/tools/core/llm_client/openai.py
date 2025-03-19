from gru.agents.tools.core.llm_client.base import LLMClient
from openai import OpenAI
from typing import Optional
import os


class OpenAILLMClient(LLMClient):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0,
    ):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.temperature = temperature

    async def generate(self, system_prompt: str, user_prompt: str) -> Optional[str]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating LLM response: {str(e)}")
