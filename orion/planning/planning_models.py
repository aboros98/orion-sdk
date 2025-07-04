from pydantic import BaseModel, Field
from typing import Optional, Literal


class OutputPlan(BaseModel):
    thinking: str = Field(
        description="The brainstorming and analysis of the user's request. Use this as internal working mechanism to make the best possible plan to acomplish the user's request."
    )
    plan: str = Field(
        description="The plan to acomplish the user's request. This is the final plan that will be executed by the orchestrator."
    )


class OutputPlanRevision(BaseModel):
    thinking: str = Field(
        description="The analysis of the execution results and the user's request. Use this as internal working mechanism to make the best possible plan to acomplish the user's request. You should brainstorm also if the plan is on track or not and should propose a revised plan if the plan is not on track."
    )
    should_revise: bool = Field(
        description="Whether the plan should be revised or not. If the plan is not on track, this should be True. If the plan is on track, this should be False."
    )
    revised_plan: Optional[str] = Field(
        description="The revised plan to acomplish the user's request. This is the final plan that will be executed by the orchestrator."
    )


class ImprovedSystemPrompt(BaseModel):
    system_prompt: str = Field(description="The improved system prompt that will be used to create the planning agent.")


class TaskValidationResult(BaseModel):
    reasoning: str = Field(
        description="Detailed explanation of the assessment, including what was expected vs what was achieved"
    )
    status: Literal["COMPLETE", "INCOMPLETE"] = Field(description="Whether the task was completed successfully or not")
    justification: Optional[str] = Field(
        description="How this task status affects subsequent tasks in the workflow. Use 'N/A' if task is completed successfully"
    )
