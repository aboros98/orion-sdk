"""
Workflow state reconstruction from event streams.

This module provides capabilities to rebuild complete workflow execution
state from stored events, enabling crash recovery and state inspection.
"""

import logging
from typing import Dict, List, Optional, Any, Union, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from .event_store import EventStore, WorkflowEvent
    from orion.graph_core.nodes.base_node import BaseNode
    from orion.graph_core.edges import BaseEdge

from orion.agent_core.models import ToolCall

logger = logging.getLogger(__name__)


@dataclass
class ReconstructedExecutionStep:
    """Reconstructed execution step from events."""
    
    node_name: str
    source_nodes: List[str]  # Store as names for reconstruction
    node_input: Union[str, ToolCall]
    node_output: str
    start_timestamp: str
    end_timestamp: str
    was_successful: bool
    error_message: Optional[str] = None


class WorkflowStateReconstructor:
    """
    Reconstructs workflow execution state from event streams.
    
    This class provides the ability to rebuild the complete execution
    state of a workflow from its event history, enabling crash recovery
    and detailed analysis of workflow execution.
    """
    
    def __init__(self, event_store: "EventStore"):
        """
        Initialize the state reconstructor.
        
        Args:
            event_store: The event store to read events from
        """
        self.event_store = event_store
        
    async def reconstruct_execution_state(
        self,
        workflow_id: str,
        nodes: Dict[str, "BaseNode"],
        edges: Dict[str, List["BaseEdge"]]
    ) -> "ReconstructedExecutionState":
        """
        Reconstruct the complete execution state from events.
        
        Args:
            workflow_id: The workflow to reconstruct
            nodes: Current nodes dictionary for validation
            edges: Current edges dictionary for validation
            
        Returns:
            ReconstructedExecutionState with all execution steps
        """
        logger.info(f"Starting reconstruction for workflow {workflow_id}")
        
        # Check for latest state snapshot first for performance
        latest_snapshot = await self.event_store.get_latest_workflow_state(workflow_id)
        from_sequence = 0
        
        if latest_snapshot:
            logger.debug(f"Found state snapshot for workflow {workflow_id}")
            # If we have a snapshot, we only need events after it
            from_sequence = latest_snapshot.get('last_sequence_number', 0) + 1
        
        # Get all events from the starting point
        events = await self.event_store.get_workflow_events(
            workflow_id, 
            from_sequence=from_sequence
        )
        
        # Initialize state
        state = ReconstructedExecutionState(
            workflow_id=workflow_id,
            nodes=nodes,
            edges=edges
        )
        
        # If we have a snapshot, apply it first
        if latest_snapshot:
            state = self._apply_snapshot(state, latest_snapshot)
        
        # Replay events to reconstruct state
        state = await self._replay_events(state, events)
        
        logger.info(f"Reconstruction complete for workflow {workflow_id}: {len(state.execution_steps)} steps")
        return state
    
    def _apply_snapshot(
        self,
        state: "ReconstructedExecutionState",
        snapshot_data: Dict[str, Any]
    ) -> "ReconstructedExecutionState":
        """Apply a state snapshot to the reconstruction."""
        try:
            # Restore initial input
            if 'initial_input' in snapshot_data:
                state.initial_input = snapshot_data['initial_input']
            
            # Restore execution steps
            if 'execution_steps' in snapshot_data:
                for step_data in snapshot_data['execution_steps']:
                    step = ReconstructedExecutionStep(
                        node_name=step_data['node_name'],
                        source_nodes=step_data['source_nodes'],
                        node_input=step_data['node_input'],
                        node_output=step_data['node_output'],
                        start_timestamp=step_data['start_timestamp'],
                        end_timestamp=step_data['end_timestamp'],
                        was_successful=step_data['was_successful'],
                        error_message=step_data.get('error_message')
                    )
                    state.execution_steps.append(step)
            
            # Restore workflow status
            if 'workflow_status' in snapshot_data:
                state.workflow_status = snapshot_data['workflow_status']
            
            logger.debug(f"Applied snapshot with {len(state.execution_steps)} steps")
            return state
            
        except Exception as e:
            logger.error(f"Failed to apply snapshot: {e}")
            # Return original state if snapshot is corrupted
            return state
    
    async def _replay_events(
        self,
        state: "ReconstructedExecutionState",
        events: List["WorkflowEvent"]
    ) -> "ReconstructedExecutionState":
        """Replay events to reconstruct the current state."""
        node_executions = {}  # Track ongoing node executions
        
        for event in events:
            try:
                event_type = event.event_type
                event_data = event.event_data
                
                if event_type == "workflow_started":
                    state.initial_input = event_data.get('initial_input')
                    state.workflow_status = "running"
                    state.start_timestamp = event.timestamp.isoformat()
                
                elif event_type == "workflow_completed":
                    state.workflow_status = "completed"
                    state.end_timestamp = event.timestamp.isoformat()
                    state.final_output = event_data.get('final_output')
                
                elif event_type == "workflow_failed":
                    state.workflow_status = "failed"
                    state.end_timestamp = event.timestamp.isoformat()
                    state.error_message = event_data.get('error_message')
                
                elif event_type == "node_started":
                    node_name = event_data['node_name']
                    node_executions[node_name] = {
                        'start_timestamp': event.timestamp.isoformat(),
                        'node_input': event_data.get('node_input'),
                        'source_nodes': event_data.get('source_nodes', [])
                    }
                
                elif event_type == "node_completed":
                    node_name = event_data['node_name']
                    if node_name in node_executions:
                        exec_info = node_executions.pop(node_name)
                        step = ReconstructedExecutionStep(
                            node_name=node_name,
                            source_nodes=exec_info['source_nodes'],
                            node_input=exec_info['node_input'],
                            node_output=event_data.get('node_output', ''),
                            start_timestamp=exec_info['start_timestamp'],
                            end_timestamp=event.timestamp.isoformat(),
                            was_successful=True
                        )
                        state.execution_steps.append(step)
                
                elif event_type == "execution_memory_snapshot":
                    # Use complete execution memory snapshot if available
                    if 'current_exec_memory' in event_data:
                        memory_data = event_data['current_exec_memory']
                        state.initial_input = memory_data.get('initial_input')
                        
                        # Clear existing steps and rebuild from snapshot
                        state.execution_steps = []
                        for step_data in memory_data.get('exec_steps', []):
                            step = ReconstructedExecutionStep(
                                node_name=step_data['node_name'],
                                source_nodes=step_data['source_nodes'],
                                node_input=step_data['node_input'],
                                node_output=step_data['node_output'],
                                start_timestamp=event.timestamp.isoformat(),
                                end_timestamp=event.timestamp.isoformat(),
                                was_successful=True
                            )
                            state.execution_steps.append(step)
                
                elif event_type == "node_failed":
                    node_name = event_data['node_name']
                    if node_name in node_executions:
                        exec_info = node_executions.pop(node_name)
                        step = ReconstructedExecutionStep(
                            node_name=node_name,
                            source_nodes=exec_info['source_nodes'],
                            node_input=exec_info['node_input'],
                            node_output='',
                            start_timestamp=exec_info['start_timestamp'],
                            end_timestamp=event.timestamp.isoformat(),
                            was_successful=False,
                            error_message=event_data.get('error_message')
                        )
                        state.execution_steps.append(step)
                
            except Exception as e:
                logger.error(f"Failed to replay event {event.event_id}: {e}")
                continue
        
        return state
    
    async def create_state_snapshot(
        self,
        workflow_id: str,
        state: "ReconstructedExecutionState"
    ) -> str:
        """
        Create a state snapshot for performance optimization.
        
        Args:
            workflow_id: Workflow identifier
            state: Current execution state
            
        Returns:
            Event ID of the created snapshot
        """
        snapshot_data = {
            'initial_input': state.initial_input,
            'workflow_status': state.workflow_status,
            'start_timestamp': state.start_timestamp,
            'end_timestamp': state.end_timestamp,
            'final_output': state.final_output,
            'error_message': state.error_message,
            'execution_steps': [
                {
                    'node_name': step.node_name,
                    'source_nodes': step.source_nodes,
                    'node_input': step.node_input,
                    'node_output': step.node_output,
                    'start_timestamp': step.start_timestamp,
                    'end_timestamp': step.end_timestamp,
                    'was_successful': step.was_successful,
                    'error_message': step.error_message
                }
                for step in state.execution_steps
            ],
            'last_sequence_number': len(state.execution_steps)  # Simple approximation
        }
        
        event_id = await self.event_store.save_state_snapshot(workflow_id, snapshot_data)
        logger.info(f"Created state snapshot for workflow {workflow_id}")
        return event_id


class ReconstructedExecutionState:
    """
    Reconstructed execution state from events.
    
    This mirrors the original ExecutionState but includes additional
    metadata from event reconstruction.
    """
    
    def __init__(
        self,
        workflow_id: str,
        nodes: Dict[str, "BaseNode"],
        edges: Dict[str, List["BaseEdge"]]
    ):
        """Initialize the reconstructed state."""
        self.workflow_id = workflow_id
        self.nodes = nodes
        self.edges = edges
        
        # Workflow metadata
        self.initial_input: Optional[str] = None
        self.workflow_status: str = "unknown"  # running, completed, failed
        self.start_timestamp: Optional[str] = None
        self.end_timestamp: Optional[str] = None
        self.final_output: Optional[str] = None
        self.error_message: Optional[str] = None
        
        # Execution steps
        self.execution_steps: List[ReconstructedExecutionStep] = []
    
    @property
    def is_empty(self) -> bool:
        """Check if the execution state is empty."""
        return len(self.execution_steps) == 0
    
    @property
    def last_node_name(self) -> Optional[str]:
        """Get the name of the last executed node."""
        if self.execution_steps:
            return self.execution_steps[-1].node_name
        return None
    
    def get_node_output(self, node_name: str) -> Optional[str]:
        """Get the output of a specific node."""
        for step in reversed(self.execution_steps):
            if step.node_name == node_name and step.was_successful:
                return step.node_output
        return None
    
    def get_node_input(self, node_name: str) -> Optional[Union[str, ToolCall]]:
        """Get the input of a specific node."""
        for step in reversed(self.execution_steps):
            if step.node_name == node_name:
                return step.node_input
        return None
    
    def get_failed_nodes(self) -> List[str]:
        """Get list of nodes that failed during execution."""
        return [step.node_name for step in self.execution_steps if not step.was_successful]
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution."""
        successful_steps = sum(1 for step in self.execution_steps if step.was_successful)
        failed_steps = len(self.execution_steps) - successful_steps
        
        return {
            'workflow_id': self.workflow_id,
            'status': self.workflow_status,
            'total_steps': len(self.execution_steps),
            'successful_steps': successful_steps,
            'failed_steps': failed_steps,
            'start_time': self.start_timestamp,
            'end_time': self.end_timestamp,
            'has_errors': failed_steps > 0
        } 