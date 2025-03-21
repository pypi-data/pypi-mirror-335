import json
from gru.agents.tools.core.code_generator.base import CodeGenerator
from gru.agents.tools.core.code_generator.models import (
    QueryIntent,
    RetrievalResult,
    SQLQueryResult,
)
from gru.agents.prompts.sql import (
    SQL_GENERATOR_USER_PROMPT_TEMPLATE,
    SQL_GENERATOR_SYSTEM_PROMPT,
)
from gru.agents.tools.core.llm_client.base import LLMClient


class SQLCodeGenerator(CodeGenerator):
    def __init__(
        self, 
        llm_client: LLMClient, 
        system_prompt=None, 
        user_prompt_template=None
    ):
        """
        Initializes the SQL Code Generator with optional custom prompts.

        :param llm_client: The LLM client to use for generation.
        :param system_prompt: Optional custom system prompt (default: SQL_GENERATOR_SYSTEM_PROMPT).
        :param user_prompt_template: Optional custom user prompt template (default: SQL_GENERATOR_USER_PROMPT_TEMPLATE).
        """
        self.llm_client = llm_client
        self.system_prompt = system_prompt or SQL_GENERATOR_SYSTEM_PROMPT
        self.user_prompt_template = user_prompt_template or SQL_GENERATOR_USER_PROMPT_TEMPLATE

    async def generate_code(
        self, 
        query: str, 
        intent: QueryIntent, 
        context: RetrievalResult
    ) -> SQLQueryResult:
        user_prompt = self.user_prompt_template.format(
            query=query,
            schemas=context.schemas,
            examples=context.examples,
            documentation=context.documentation,
        )
        response = await self.llm_client.generate(
            self.system_prompt, user_prompt
        )

        try:
            response_json = json.loads(response)
            return SQLQueryResult(**response_json)
        except json.JSONDecodeError:
            return SQLQueryResult(sql_query=response)
