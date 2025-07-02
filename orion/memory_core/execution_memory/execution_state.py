from typing import List, Union, Dict, Optional, Any
import uuid
import logging
import re

from orion.persistence.event_store import EventStore
from orion.agent_core.models import ToolCall
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExecutionStep:
    node_name: str
    node_input: Union[str, ToolCall]
    node_output: str
    node_type: Optional[str] = None


class ExecutionMemory:
    def __init__(
        self, 
        event_store: Optional["EventStore"] = None,
        workflow_id: Optional[str] = None,
        name: str = "execution_memory"
    ) -> None:
        self.name = name  # Add name attribute for node behavior
        self._exec_steps: List[ExecutionStep] = []
        
        # Event sourcing integration
        self.event_store = event_store
        self.workflow_id = workflow_id or str(uuid.uuid4())
        
        # Summary tracking for completed work and solved tasks
        self.summary = {
            "solved_tasks": [],
            "completed_nodes": [],
            "available_outputs": {},
            "total_completed": 0
        }
        
        logger.debug(f"Initialized ExecutionMemory with workflow_id: {self.workflow_id}")

    # Memory node behavior - stores information by adding exec steps
    async def compute(self, input_data, *args, **kwargs) -> str:
        """
        Store information in execution memory by adding an exec step.
        This is the compute method for the memory node - it stores data instead of processing it.
        """
        if input_data is None:
            raise ValueError(f"ExecutionMemory memory node '{self.name}' received None input - input is required")
        
        try:
            # Convert input to string for storage
            input_str = str(input_data)
            
            # Create a memory storage confirmation
            result = f"Stored in execution memory: {input_str}"
            
            # Add execution step (this IS the memory storage)
            # For memory node, we don't need source nodes since it just stores data
            self.add_exec_step(
                node_name=self.name,
                node_input=input_str,
                node_output=result,
                node_type="execution_memory"
            )
            
            logger.debug(f"ExecutionMemory memory node '{self.name}' stored: {input_str[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"ExecutionMemory memory node '{self.name}' failed to store information: {e}")
            raise Exception(f"Memory storage failed: {e}")

    def clear_execution_traces(self) -> None:
        """Clear all execution steps."""
        self._exec_steps.clear()

    def add_exec_step(
        self, node_name: str, node_input: str, node_output: str, solved_task: Optional[str] = None, node_type: Optional[str] = None
    ) -> None:
        """Add an execution step to the memory."""
        # Store the execution step
        step = ExecutionStep(
            node_name=node_name,
            node_input=node_input,
            node_output=node_output,
            node_type=node_type,
        )
        self._exec_steps.append(step)
        
        # Update summary for non-system nodes
        if node_name not in ["__start__", "__end__"]:
            # Track completed node
            if node_name not in self.summary["completed_nodes"]:
                self.summary["completed_nodes"].append(node_name)
            
            # Track solved task if provided
            if solved_task and solved_task not in self.summary["solved_tasks"]:
                self.summary["solved_tasks"].append(solved_task)
            
            # Store brief output description
            output_desc = str(node_output)[:50] + "..." if len(str(node_output)) > 50 else str(node_output)
            self.summary["available_outputs"][node_name] = output_desc
            
            # Update total count
            self.summary["total_completed"] = len(self.summary["completed_nodes"])
        
        # Record completion event if event store is available
        if self.event_store:
            import asyncio
            try:
                # Create an async task to store the event with complete execution memory
                loop = asyncio.get_event_loop()
                _ = loop.create_task(
                    self.event_store.store_event(
                        workflow_id=self.workflow_id,
                        event_type="node_completed",
                        event_data={
                            'node_name': node_name,
                            'node_input': str(node_input),
                            'node_output': str(node_output),
                            # Save the complete execution step for reconstruction
                            'execution_step': self._serialize_execution_step(step),
                            # Save current execution memory state for full reconstruction
                            'current_exec_memory': self._serialize_execution_memory()
                        }
                    )
                )
                # Don't wait for completion to avoid blocking execution
                logger.debug(f"Recorded node completion event with execution memory for {node_name}")
            except Exception as e:
                logger.error(f"Failed to record node completion event: {e}")

    def get_node_output(self, node_name: str) -> Optional[str]:
        """Get the output from a specific node (most recent execution)."""
        # Iterate in reverse to get the most recent execution of the node
        for step in reversed(self._exec_steps):
            if step.node_name == node_name:
                return step.node_output
        return None

    def get_node_input(self, node_name: str) -> Optional[Union[str, ToolCall]]:
        """Get the input for a specific node (most recent execution)."""
        # Iterate in reverse to get the most recent execution of the node
        for step in reversed(self._exec_steps):
            if step.node_name == node_name:
                return step.node_input
        return None

    def get_entries_for_nodes(self, node_names: Optional[List[str]] = None) -> List[ExecutionStep]:
        """
        Retrieve execution entries for specific nodes.
        
        Args:
            node_names: List of node names to retrieve entries for. 
                       If None or empty, returns all entries.
        
        Returns:
            List of ExecutionStep objects for the specified nodes
        """
        if not node_names:
            # Return all entries if no specific nodes requested
            return self._exec_steps.copy()
        
        # Filter entries for specified nodes
        filtered_entries = []

        for step in self._exec_steps:
            if step.node_name in node_names:
                filtered_entries.append(step)
        
        return filtered_entries

    async def save_execution_memory_snapshot(self) -> Optional[str]:
        """Save a complete snapshot of the execution memory state."""
        if not self.event_store:
            return None
            
        try:
            return await self.event_store.store_event(
                workflow_id=self.workflow_id,
                event_type="execution_memory_snapshot",
                event_data=self._serialize_execution_memory()
            )
        except Exception as e:
            logger.error(f"Failed to save execution memory snapshot: {e}")
            return None

    def _serialize_execution_step(self, step: ExecutionStep) -> Dict[str, Any]:
        """Serialize an execution step for storage."""
        # Handle different input types
        serialized_input = step.node_input
        if isinstance(step.node_input, ToolCall):
            serialized_input = {
                'type': 'ToolCall',
                'tool_name': step.node_input.tool_name,
                'arguments': step.node_input.arguments
            }
        
        return {
            'node_name': step.node_name,
            'node_input': serialized_input,
            'node_output': step.node_output,
            'node_type': step.node_type
        }
    
    def _serialize_execution_memory(self) -> Dict[str, Any]:
        """Serialize the complete execution memory state."""
        return {
            'workflow_id': self.workflow_id,
            'exec_steps': [self._serialize_execution_step(step) for step in self._exec_steps],
            'total_steps': len(self._exec_steps)
        }

    def get_summary_for_orchestrator(self) -> str:
        """Return formatted summary for orchestrator context."""
        if not self.summary["completed_nodes"]:
            return "No previous work completed."
        
        lines = ["Previous work completed:"]
        
        # Show solved tasks
        if self.summary["solved_tasks"]:
            lines.append("\nTasks solved:")
            for task in self.summary["solved_tasks"]:
                lines.append(f"✓ {task}")
        
        # Show available data
        lines.append("\nData available:")
        for node_name in self.summary["completed_nodes"]:
            output_desc = self.summary["available_outputs"].get(node_name, "output ready")
            lines.append(f"- {node_name}: {output_desc}")
        
        return "\n".join(lines)
    
    def get_summary_dict(self) -> dict:
        """Return raw summary dictionary."""
        return self.summary.copy()

    def resolve_references(self, text: str) -> str:
        """Resolve memory references in text to actual content."""
        def replace_reference(match):
            ref_full = match.group(1)  # e.g., "node_name" or "node_name.summary"
            
            if '.' in ref_full:
                node_name, modifier = ref_full.split('.', 1)
            else:
                node_name, modifier = ref_full, None
            
            # Get the actual content
            output = self.get_node_output(node_name)
            if output is None:
                return f"[Reference {node_name}: not found]"
            
            # Apply modifier if specified
            if modifier == 'summary':
                # Return first 100 characters
                return str(output)[:100] + "..." if len(str(output)) > 100 else str(output)
            else:
                # Return full content
                return str(output)
        
        # Replace all {ref:...} patterns
        return re.sub(r'\{ref:([^}]+)\}', replace_reference, text)

    def get_available_references(self) -> List[str]:
        """Get list of nodes that can be referenced."""
        return [node for node in self.summary["completed_nodes"] if node not in ["__start__", "__end__"]]

    def preview_reference(self, node_name: str) -> str:
        """Get a preview of what a reference would resolve to."""
        output = self.get_node_output(node_name)
        if output is None:
            return f"[{node_name}: not available]"
        
        preview = str(output)[:50] + "..." if len(str(output)) > 50 else str(output)
        return f"{node_name}: {preview}"

    def get_planning_memory_entries(self) -> List[str]:
        """
        Get memory entries formatted for planning agents.
        
        Returns summaries for all memory entries except for human-in-the-loop node outputs
        (user input), which are provided in full.
        
        Returns:
            List of formatted memory entry strings for planning context
        """
        if not self._exec_steps:
            return []
        
        formatted_entries = []
        
        for step in self._exec_steps:
            # Skip system nodes
            if step.node_name in ["__start__", "__end__"]:
                continue
            
            # Check if this is a human-in-the-loop node (user input) using node_type
            is_user_input = step.node_type == "HumanInTheLoopNode"
            
            # Format the entry
            if is_user_input:
                # Provide full content for user input
                entry = f"**{step.node_name}** (User Input):\n"
                entry += f"Output: {str(step.node_output)}\n"
            else:
                # Provide summary for other nodes
                output_summary = str(step.node_output)[:100] + "..." if len(str(step.node_output)) > 100 else str(step.node_output)
                
                entry = f"**{step.node_name}** (Summary):\n"
                entry += f"Output: {output_summary}\n"
            
            formatted_entries.append(entry)
        
        return formatted_entries
