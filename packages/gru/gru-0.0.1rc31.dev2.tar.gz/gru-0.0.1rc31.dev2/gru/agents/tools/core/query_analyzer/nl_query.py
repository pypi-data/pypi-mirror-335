from gru.agents.tools.core.query_analyzer.base import QueryAnalyzer
from gru.agents.tools.core.code_generator.models import QueryIntent


class NLQueryAnalyzer(QueryAnalyzer):

    async def analyze_query(self, query: str) -> QueryIntent:
        pass
