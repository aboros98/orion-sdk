# Prompts module for Orion framework 

# Import all prompts from individual files

# Planning system prompts
from .planning_system_prompt import PLANNING_SYSTEM_PROMPT
from .revision_system_prompt import REVISION_SYSTEM_PROMPT
from .prompt_optimizer_system_prompt import PROMPT_OPTIMIZER_SYSTEM_PROMPT

# Planning templates
from .plan_creation_prompt_template import PLAN_CREATION_PROMPT_TEMPLATE
from .plan_revision_prompt_template import PLAN_REVISION_PROMPT_TEMPLATE

# Orchestrator template
from .orchestrator_system_prompt_template import ORCHESTRATOR_SYSTEM_PROMPT_TEMPLATE

# Agent system prompts
from .description_enhancer_system_prompt import DESCRIPTION_ENHANCER_SYSTEM_PROMPT

# Export all prompts
__all__ = [
    # Planning system prompts
    'PLANNING_SYSTEM_PROMPT',
    'REVISION_SYSTEM_PROMPT',
    'PROMPT_OPTIMIZER_SYSTEM_PROMPT',
    
    # Planning templates
    'PLAN_CREATION_PROMPT_TEMPLATE',
    'PLAN_REVISION_PROMPT_TEMPLATE',
    
    # Orchestrator template
    'ORCHESTRATOR_SYSTEM_PROMPT_TEMPLATE',
    
    # Agent system prompts
    'DESCRIPTION_ENHANCER_SYSTEM_PROMPT'
] 