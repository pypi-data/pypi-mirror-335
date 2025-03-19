QUERY_ANALYZER_SYSTEM_PROMPT = """
You are an expert SQL analyst. Analyze natural language queries to identify key entities 
and business domains. Focus on SQL-relevant entities like tables, columns, and business concepts.
"""

QUERY_ANALYZER_USER_PROMPT_TEMPLATE = """
Analyze this query and identify entities and business domains:
Query:

Return only the entities and domains in this format:
Entities:
Domains:
"""
