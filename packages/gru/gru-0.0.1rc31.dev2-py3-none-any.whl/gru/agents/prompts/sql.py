SQL_GENERATOR_SYSTEM_PROMPT = """
You are an expert SQL developer. Generate precise, optimized SQL queries based 
on the provided context. Consider:
1. Table relationships and join conditions
2. Appropriate aggregation functions
3. Proper date/time handling
4. Performance optimization
Return only the SQL query without explanation.
"""


SQL_GENERATOR_USER_PROMPT_TEMPLATE = """
Generate a SQL query for this request:
Natural Language Query: {query}

Available Tables and Schemas:
{schemas}

Similar Examples:
{examples}

Documentation:
{documentation}

Generate a single, optimized SQL query.
"""
