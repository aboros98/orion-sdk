# Prompts module for Orion framework 

# Import all prompts from individual files

# Planning system prompts
from .planning_system_prompt import PLANNING_SYSTEM_PROMPT
from .revision_system_prompt import REVISION_SYSTEM_PROMPT
from .orchestrator_system_prompt_template import ORCHESTRATOR_SYSTEM_PROMPT_TEMPLATE
from .description_enhancer_system_prompt import DESCRIPTION_ENHANCER_SYSTEM_PROMPT
from .prompt_optimizer_system_prompt import PROMPT_OPTIMIZER_SYSTEM_PROMPT

# Export all prompts
__all__ = [
    'PLANNING_SYSTEM_PROMPT',
    'REVISION_SYSTEM_PROMPT',
    'ORCHESTRATOR_SYSTEM_PROMPT_TEMPLATE',
    'DESCRIPTION_ENHANCER_SYSTEM_PROMPT',
    'PROMPT_OPTIMIZER_SYSTEM_PROMPT',
] 