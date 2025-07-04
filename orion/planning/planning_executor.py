import logging
from typing import Optional

from orion.graph_core.compiled_graph import CompiledGraph
from orion.planning.graph_inspector import GraphInspector
from orion.planning.planning_agent import PlanningAgent
from orion.planning.task_validation_agent import TaskValidationAgent

logger = logging.getLogger(__name__)


class PlanningExecutor:
    """
    Executor that uses dynamic planning with ReAct-style reasoning and plan revision.
    Plans are revised based on execution memory observations and task validation.
    """

    def __init__(self, compiled_graph: "CompiledGraph", max_revisions: int = 10):
        """
        Initialize the dynamic planning executor

        Args:
            compiled_graph: The compiled graph to execute
            max_revisions: Maximum number of plan revisions allowed (default: 10)
        """
        self.compiled_graph = compiled_graph
        self.graph_inspector = GraphInspector(compiled_graph)
        self.planning_agent: Optional[PlanningAgent] = None
        self.task_validation_agent: Optional[TaskValidationAgent] = None
        self.max_revisions = max_revisions

        # Track planning state
        self.current_plan = None
        self.original_request = None
        self.plan_file = "PLAN.md"

    @classmethod
    async def create(
        cls,
        compiled_graph: "CompiledGraph",
        revision_frequency: int = 1,
        optimize_prompt: bool = False,
        user_instructions: Optional[str] = None,
        max_revisions: int = 10,
    ) -> "PlanningExecutor":
        """
        Create a new instance of the planning executor.

        Args:
            compiled_graph: The compiled graph to execute
            revision_frequency: Number of tasks to complete before revising plan
            optimize_prompt: Whether to optimize the planning system prompt
            user_instructions: User-supplied instructions for optimizing the planning system prompt
            max_revisions: Maximum number of plan revisions allowed (default: 10)
        """
        executor = cls(compiled_graph, max_revisions)
        executor.planning_agent = await PlanningAgent.create(
            graph_inspector=executor.graph_inspector,
            revision_frequency=revision_frequency,
            optimize_prompt=optimize_prompt,
            user_instructions=user_instructions,
        )
        executor.task_validation_agent = await TaskValidationAgent.create()

        return executor

    async def execute_with_dynamic_planning(self, user_request: str, save_plan_history: bool = True) -> str:
        """
        Execute request with dynamic planning and plan revision

        Args:
            user_request: The user's request
            save_plan_history: Whether to save plan revision history

        Returns:
            Final response to the user
        """
        print(f"🎯 Starting dynamic planning execution for: {user_request}")

        # Create initial plan with ReAct reasoning
        print("🧠 Brainstorming and creating initial execution plan...")
        if not self.planning_agent:
            raise RuntimeError("Planning agent not initialized. Call create() to instantiate.")

        if not self.task_validation_agent:
            raise RuntimeError("Task validation agent not initialized. Call create() to instantiate.")

        self.original_request = user_request
        self.current_plan = await self.planning_agent.create_executable_plan(user_request)

        # Save initial plan and reasoning
        await self._save_plan(self.current_plan, version=0)
        print("✅ Initial plan created (see PLAN.md and REASONING.md)")

        # Extract tasks
        tasks = self.planning_agent.get_pending_tasks(self.current_plan)
        if not tasks:
            print("⚠️ No tasks found in plan")
            return "Unable to create an execution plan for this request."

        print(f"📊 Found {len(tasks)} tasks to execute")

        # Execute tasks with dynamic revision
        completed_count = 0
        revision_count = 0

        while tasks:
            current_task = tasks[0]
            print(f"\n🔧 Task {current_task}")

            try:
                # Execute the task through the graph
                result = await self._execute_task(current_task)

                validation_result = await self.task_validation_agent.validate_task(
                    current_task, result, remaining_tasks_in_plan=tasks[1:], original_user_request=self.original_request
                )

                if validation_result.validation_status == "COMPLETE":
                    print(f"✅ Task validated as complete")
                    # Update plan status only if validated as complete
                    self.current_plan = self.planning_agent.update_plan_status(self.current_plan, current_task)
                    completed_count += 1
                else:
                    print(f"❌ Task validation failed")
                    if self.compiled_graph.execution_state._exec_steps[-1].node_output == result:
                        self.compiled_graph.execution_state._exec_steps = self.compiled_graph.execution_state._exec_steps[:-1]

                    # Force plan revision due to task validation failure
                    print("🔄 Forcing plan revision due to task validation failure...")
                    execution_memory = self.compiled_graph.execution_state

                    # Add validation information for revision context
                    # This helps the revision agent understand why the task failed
                    validation_context = f"""**task_validator** (Assessment)**:
<current_task>
{current_task}
</current_task>

<status>
{validation_result.validation_status}
</status>

<reasoning>
{validation_result.completion_reasoning}
</reasoning>

{f"<issues>{validation_result.remaining_issues}</issues>" if validation_result.validation_status == "INCOMPLETE" else ""}

{f"<workflow_impact>{validation_result.workflow_impact}</workflow_impact>" if validation_result.validation_status == "INCOMPLETE" else ""}

{f"<resolution_guidance>{validation_result.resolution_guidance}</resolution_guidance>" if validation_result.validation_status == "INCOMPLETE" else ""}

<current_task_output>
{result[:300] + "..." if len(result) > 300 else result}
</current_task_output>"""

                    revised_plan = await self.planning_agent.revise_plan(
                        self.current_plan,
                        execution_memory,
                        self.original_request,
                        force=True,
                        validation_context=validation_context,
                    )

                    if revised_plan != self.current_plan:
                        revision_count += 1
                        self.current_plan = revised_plan
                        await self._save_plan(self.current_plan, version=revision_count)

                        # Check if we've reached the maximum number of revisions
                        if revision_count >= self.max_revisions:
                            print(f"⚠️ Maximum revisions ({self.max_revisions}) reached. Stopping execution.")
                            print(f"📊 Final status: {completed_count} tasks completed, {revision_count} revisions")
                            return (
                                result if "result" in locals() else "Execution stopped due to maximum revisions limit."
                            )

                    # Update remaining tasks
                    tasks = self.planning_agent.get_pending_tasks(self.current_plan)
                    continue

                if self.planning_agent:
                    self.planning_agent.tasks_since_revision += 1

                if len(self.planning_agent.get_pending_tasks(self.current_plan)) == 0:
                    break

                # Get execution memory from the compiled graph
                execution_memory = self.compiled_graph.execution_state

                # Revise the plan
                revised_plan = await self.planning_agent.revise_plan(
                    self.current_plan, execution_memory, self.original_request
                )

                if revised_plan != self.current_plan:
                    revision_count += 1
                    self.current_plan = revised_plan

                    # Check if we've reached the maximum number of revisions
                    if revision_count >= self.max_revisions:
                        print(f"⚠️ Maximum revisions ({self.max_revisions}) reached. Stopping execution.")
                        print(f"📊 Final status: {completed_count} tasks completed, {revision_count} revisions")
                        return result if "result" in locals() else "Execution stopped due to maximum revisions limit."

                # Save revised plan and reasoning
                if save_plan_history:
                    await self._save_plan(self.current_plan, version=revision_count)

                # Re-extract remaining tasks from revised plan
                tasks = self.planning_agent.get_pending_tasks(self.current_plan)

            except Exception as e:
                print(f"❌ Task failed: {str(e)}")
                logger.error(f"Task execution failed: {e}", exc_info=True)

                # Force plan revision on failure
                print("🔄 Forcing plan revision due to task failure...")
                execution_memory = self.compiled_graph.execution_state

                revised_plan = await self.planning_agent.revise_plan(
                    self.current_plan, execution_memory, self.original_request, force=True
                )

                if revised_plan != self.current_plan:
                    revision_count += 1
                    self.current_plan = revised_plan
                    await self._save_plan(self.current_plan, version=revision_count)

                    # Check if we've reached the maximum number of revisions
                    if revision_count >= self.max_revisions:
                        print(f"⚠️ Maximum revisions ({self.max_revisions}) reached. Stopping execution.")
                        print(f"📊 Final status: {completed_count} tasks completed, {revision_count} revisions")
                        return result if "result" in locals() else "Execution stopped due to maximum revisions limit."

                # Update remaining tasks
                tasks = self.planning_agent.get_pending_tasks(self.current_plan)

        # Generate final response
        print(f"\n📊 Execution complete: {completed_count} tasks completed, {revision_count} revisions")
        self.compiled_graph.execution_state.clear_execution_traces()
        return result

    async def _execute_task(self, task: str) -> str:
        """Execute a single task through the graph"""
        try:
            # Execute through the graph's orchestrator
            result = await self.compiled_graph.execute(
                initial_input=task, max_iterations=10  # Limit iterations for safety
            )
            return result
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise

    async def _save_plan(self, plan_content: str, version):
        """Save plan to file with version tracking"""
        try:
            # Save current version
            filename = f"{self.plan_file}" if version == "final" else f"PLAN_v{version}.md"

            with open(filename, "w") as f:
                f.write(plan_content)

            # Always update the main PLAN.md with latest
            if version != 0:
                with open(self.plan_file, "w") as f:
                    f.write(plan_content)

        except Exception as e:
            logger.error(f"Failed to save plan: {e}")
