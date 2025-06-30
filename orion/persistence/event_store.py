import asyncio
import logging
import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

logger = logging.getLogger(__name__)


@dataclass
class WorkflowEvent:
    """Represents a single event in a workflow execution."""
    
    event_id: str
    workflow_id: str
    event_type: str  # workflow_started, workflow_completed, workflow_failed, node_started, node_completed, node_failed
    timestamp: datetime
    event_data: Dict[str, Any]
    sequence_number: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary for MongoDB storage."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowEvent':
        """Create an event from a MongoDB document."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class EventStore:
    """
    MongoDB-based event store for workflow event persistence.
    
    This class provides thread-safe event storage and retrieval capabilities,
    ensuring that all workflow events are persisted even if the system crashes.
    """
    
    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017/",
        database_name: str = "orion_events",
        collection_name: str = "workflow_events"
    ):
        """
        Initialize the event store with MongoDB connection.
        
        Args:
            mongo_uri: MongoDB connection string
            database_name: Name of the database to use
            collection_name: Name of the collection to store events
        """
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.collection_name = collection_name
        
        # Thread safety
        self._lock = threading.RLock()
        self._thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Connection management
        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None
        self._collection: Optional[Collection] = None
        
        # Sequence tracking per workflow
        self._sequence_counters: Dict[str, int] = {}
        
        # Initialize connection
        self._ensure_connection()
        
    def _ensure_connection(self) -> None:
        """Ensure MongoDB connection is established."""
        if self._client is None:
            try:
                self._client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
                self._database = self._client[self.database_name]
                self._collection = self._database[self.collection_name]
                
                # Create indexes for efficient querying
                self._collection.create_index([
                    ("workflow_id", pymongo.ASCENDING),
                    ("sequence_number", pymongo.ASCENDING)
                ])
                self._collection.create_index("timestamp")
                self._collection.create_index("event_type")
                
                logger.info(f"Connected to MongoDB: {self.database_name}.{self.collection_name}")
                
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
    
    def _get_next_sequence_number(self, workflow_id: str) -> int:
        """Get the next sequence number for a workflow."""
        with self._lock:
            if workflow_id not in self._sequence_counters:
                # Find the highest sequence number for this workflow
                self._ensure_connection()
                assert self._collection is not None
                last_event = self._collection.find_one(
                    {"workflow_id": workflow_id},
                    sort=[("sequence_number", pymongo.DESCENDING)]
                )
                self._sequence_counters[workflow_id] = (
                    last_event["sequence_number"] + 1 if last_event else 0
                )
            else:
                self._sequence_counters[workflow_id] += 1
            
            return self._sequence_counters[workflow_id]
    
    async def store_event(
        self,
        workflow_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> str:
        """
        Store an event asynchronously.
        
        Args:
            workflow_id: Unique identifier for the workflow
            event_type: Type of event (e.g., 'workflow_started', 'node_completed')
            event_data: Additional data associated with the event
            
        Returns:
            str: Unique event ID
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        sequence_number = self._get_next_sequence_number(workflow_id)
        
        event = WorkflowEvent(
            event_id=event_id,
            workflow_id=workflow_id,
            event_type=event_type,
            timestamp=timestamp,
            event_data=event_data,
            sequence_number=sequence_number
        )
        
        # Store event asynchronously
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self._thread_pool,
            self._store_event_sync,
            event
        )
        
        logger.debug(f"Stored event {event_type} for workflow {workflow_id}")
        return event_id
    
    def _store_event_sync(self, event: WorkflowEvent) -> None:
        """Synchronously store an event to MongoDB."""
        try:
            self._ensure_connection()
            assert self._collection is not None
            document = event.to_dict()
            self._collection.insert_one(document)
        except Exception as e:
            logger.error(f"Failed to store event {event.event_id}: {e}")
            raise
    
    async def get_workflow_events(
        self,
        workflow_id: str,
        event_type: Optional[str] = None,
        from_sequence: int = 0
    ) -> List[WorkflowEvent]:
        """
        Retrieve events for a specific workflow.
        
        Args:
            workflow_id: Workflow identifier
            event_type: Optional filter by event type
            from_sequence: Start from this sequence number
            
        Returns:
            List of workflow events in sequence order
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._thread_pool,
            self._get_workflow_events_sync,
            workflow_id,
            event_type,
            from_sequence
        )
    
    def _get_workflow_events_sync(
        self,
        workflow_id: str,
        event_type: Optional[str] = None,
        from_sequence: int = 0
    ) -> List[WorkflowEvent]:
        """Synchronously retrieve workflow events."""
        try:
            self._ensure_connection()
            assert self._collection is not None
            
            query = {
                "workflow_id": workflow_id,
                "sequence_number": {"$gte": from_sequence}
            }
            
            if event_type:
                query["event_type"] = event_type
            
            cursor = self._collection.find(query).sort("sequence_number")
            events = [WorkflowEvent.from_dict(doc) for doc in cursor]
            
            logger.debug(f"Retrieved {len(events)} events for workflow {workflow_id}")
            return events
            
        except Exception as e:
            logger.error(f"Failed to retrieve events for workflow {workflow_id}: {e}")
            raise
    
    async def get_latest_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest state snapshot for a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Latest workflow state or None if no snapshots exist
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._thread_pool,
            self._get_latest_workflow_state_sync,
            workflow_id
        )
    
    def _get_latest_workflow_state_sync(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Synchronously get the latest workflow state."""
        try:
            self._ensure_connection()
            assert self._collection is not None
            
            # Look for the most recent state snapshot
            snapshot = self._collection.find_one(
                {
                    "workflow_id": workflow_id,
                    "event_type": "state_snapshot"
                },
                sort=[("sequence_number", pymongo.DESCENDING)]
            )
            
            return snapshot["event_data"] if snapshot else None
            
        except Exception as e:
            logger.error(f"Failed to get latest state for workflow {workflow_id}: {e}")
            return None
    
    async def save_state_snapshot(
        self,
        workflow_id: str,
        state_data: Dict[str, Any]
    ) -> str:
        """
        Save a state snapshot for performance optimization.
        
        Args:
            workflow_id: Workflow identifier
            state_data: Complete workflow state
            
        Returns:
            Event ID of the snapshot
        """
        return await self.store_event(
            workflow_id=workflow_id,
            event_type="state_snapshot",
            event_data=state_data
        )
    
    def close(self) -> None:
        """Close the MongoDB connection and cleanup resources."""
        if self._client:
            self._client.close()
            self._client = None
        self._thread_pool.shutdown(wait=True)
        logger.info("Event store connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


 