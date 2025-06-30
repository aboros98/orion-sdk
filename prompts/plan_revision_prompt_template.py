PLAN_REVISION_PROMPT_TEMPLATE = """Revise this plan based on execution progress using ReAct reasoning.

ORIGINAL REQUEST: {original_request}

CURRENT PLAN:
{current_plan}

EXECUTION MEMORY:
{execution_history}

AVAILABLE CAPABILITIES:
{graph_capabilities}

Remember to:
1. Start with <observation> analyzing the execution memory
2. Follow with <reflection> on needed changes
3. End with <revised_plan> containing the updated task list
4. Keep completed tasks marked [x]
5. Base revisions on actual outputs in memory""" 