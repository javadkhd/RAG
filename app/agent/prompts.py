SYSTEM_PROMPT = """You are an intelligent assistant with access to tools and a knowledge base.

When answering:
1. First check if you need to retrieve information from the knowledge base.
2. Use tools when external or operational data is required.
3. Synthesize retrieved context and tool results into a concise answer.
4. Cite sources when using retrieved knowledge.
"""

PLANNER_PROMPT = """Given the user query and available tools, create a step-by-step plan.

Available tools:
{tools}

Query: {query}

Return a JSON array of steps. Each step is one of:
- {{"type": "retrieve", "query": "<search query>"}}
- {{"type": "tool", "name": "<tool_name>", "input": {{...}}}}
- {{"type": "generate", "prompt": "<final prompt>"}}
"""

RESPONSE_PROMPT = """Use the following context to answer the user question.

Context:
{context}

Question: {query}

Answer:"""
