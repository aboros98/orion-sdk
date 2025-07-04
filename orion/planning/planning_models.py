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
    thinking: str = Field(
        description="Detailed explanation of the assessment, including what was expected vs what was achieved"
    )
    validation_status: Literal["COMPLETE", "INCOMPLETE", "PARTIAL"] = Field(description="Whether the task was completed successfully or not")
    completion_reasoning: str = Field(description="Specific evidence of successful objective accomplishment")
    usable_components: Optional[str] = Field(description="Which parts of output can support downstream work")
    remaining_issues: Optional[str] = Field(description="Specific problems that need resolution")
    workflow_impact: Optional[str] = Field(description="How issues prevent downstream task progression")
    resolution_guidance: Optional[str] = Field(description="Targeted improvements needed for full completion")