PLAN_CREATION_PROMPT_TEMPLATE = """Create an executable plan for this request using ReAct reasoning.

AVAILABLE CAPABILITIES:
{graph_capabilities}

USER REQUEST: {user_request}

Remember to:
1. Start with <brainstorm> to analyze the request
2. Follow with <reasoning> to synthesize strategy  
3. End with <plan> containing the executable task list
4. Include specific parameters in tasks
5. Map tasks to available capabilities""" 