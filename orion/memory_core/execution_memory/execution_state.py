from typing import List, Union, Dict, Optional, Any
import uuid
import logging

from orion.persistence.event_store import EventStore
from orion.agent_core.models import ToolCall
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExecutionStep:
    node_name: str
    node_input: Union[str, ToolCall]
    node_output: str


class ExecutionMemory:
    def __init__(
        self, 
        event_store: Optional["EventStore"] = None,
        workflow_id: Optional[str] = None,
        name: str = "execution_memory"
    ) -> None:
        self.name = name  # Add name attribute for node behavior
        self._exec_steps: List[ExecutionStep] = []
        self._node_counters: Dict[str, int] = {}  # Track execution count per node
        
        # Event sourcing integration
        self.event_store = event_store
        self.workflow_id = workflow_id or str(uuid.uuid4())
        
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
        self, node_name: str, node_input: str, node_output: str
    ) -> None:
        """Add an execution step to the memory with auto-numbering."""
        # Skip numbering for special nodes
        if node_name in ["__start__", "__end__", "execution_memory"]:
            numbered_node_name = node_name
        else:
            # Auto-number the node execution
            if node_name not in self._node_counters:
                self._node_counters[node_name] = 0
            self._node_counters[node_name] += 1
            numbered_node_name = f"{node_name}_{self._node_counters[node_name]}"
        
        # Store the execution step with numbered name
        step = ExecutionStep(
            node_name=numbered_node_name,
            node_input=node_input,
            node_output=node_output,
        )
        self._exec_steps.append(step)
        
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
            'node_output': step.node_output
        }
    
    def _serialize_execution_memory(self) -> Dict[str, Any]:
        """Serialize the complete execution memory state."""
        return {
            'workflow_id': self.workflow_id,
            'exec_steps': [self._serialize_execution_step(step) for step in self._exec_steps],
            'total_steps': len(self._exec_steps)
        }
