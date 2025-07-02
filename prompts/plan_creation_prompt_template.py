PLAN_CREATION_PROMPT_TEMPLATE = """Create an executable plan for this request using ReAct reasoning.

AVAILABLE CAPABILITIES:
{graph_capabilities}

COMPLETED WORK (can be referenced):
{execution_summary}

USER REQUEST: {user_request}

Remember to:
1. Start with <brainstorm> to analyze the request
2. Follow with <reasoning> to synthesize strategy  
3. End with <plan> containing the executable task list
4. Use {{ref:node_name}} to reference completed work instead of copying content
5. Use {{ref:node_name.summary}} for brief references
6. Map tasks to available capabilities
7. Build on existing work when possible

REFERENCE EXAMPLES:
- "Analyze {{ref:data_processor}} for trends" 
- "Create report using {{ref:financial_analyzer}} and {{ref:market_data}}"
- "Summarize {{ref:analysis_node.summary}} in plain language" """ 