"""
Memory Service - Centralized memory management
"""
from typing import Dict, Optional, List
from app.memory.conversation_memory import ConversationMemoryManager
from app.memory.vector_store import VectorStore
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MemoryService:
    """Service for managing conversation memory and vector storage"""
    
    def __init__(self):
        self._conversation_memories: Dict[str, ConversationMemoryManager] = {}
        self._vector_stores: Dict[str, VectorStore] = {}
    
    def get_conversation_memory(
        self,
        session_id: str,
        create_if_missing: bool = True
    ) -> Optional[ConversationMemoryManager]:
        """
        Get conversation memory for a session
        
        Args:
            session_id: Session ID
            create_if_missing: Create new memory if not found
            
        Returns:
            ConversationMemoryManager instance or None
        """
        if session_id not in self._conversation_memories:
            if create_if_missing:
                logger.info(f"Creating new conversation memory for session: {session_id}")
                self._conversation_memories[session_id] = ConversationMemoryManager(session_id)
            else:
                return None
        
        return self._conversation_memories[session_id]
    
    def get_vector_store(
        self,
        collection_name: str,
        create_if_missing: bool = True
    ) -> Optional[VectorStore]:
        """
        Get vector store for a collection
        
        Args:
            collection_name: Collection name
            create_if_missing: Create new store if not found
            
        Returns:
            VectorStore instance or None
        """
        if collection_name not in self._vector_stores:
            if create_if_missing:
                logger.info(f"Creating new vector store for collection: {collection_name}")
                self._vector_stores[collection_name] = VectorStore(collection_name)
            else:
                return None
        
        return self._vector_stores[collection_name]
    
    async def add_message_to_session(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add a message to conversation memory
        
        Args:
            session_id: Session ID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        memory = self.get_conversation_memory(session_id)
        await memory.add_message(role, content, metadata)
        logger.info(f"Added {role} message to session {session_id}")
    
    async def get_session_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session ID
            limit: Maximum number of messages
            
        Returns:
            List of messages
        """
        memory = self.get_conversation_memory(session_id, create_if_missing=False)
        if not memory:
            return []
        
        return await memory.get_history(limit)
    
    async def clear_session_memory(self, session_id: str):
        """
        Clear conversation memory for a session
        
        Args:
            session_id: Session ID
        """
        if session_id in self._conversation_memories:
            memory = self._conversation_memories[session_id]
            memory.clear_memory()
            logger.info(f"Cleared memory for session {session_id}")
    
    async def summarize_session(self, session_id: str) -> str:
        """
        Generate summary of conversation
        
        Args:
            session_id: Session ID
            
        Returns:
            Conversation summary
        """
        memory = self.get_conversation_memory(session_id, create_if_missing=False)
        if not memory:
            return "No conversation history found"
        
        return await memory.summarize_conversation()
    
    async def add_documents_to_vector_store(
        self,
        collection_name: str,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Add documents to vector store
        
        Args:
            collection_name: Collection name
            documents: List of document texts
            metadata: Optional metadata for each document
            ids: Optional document IDs
            
        Returns:
            Success status
        """
        store = self.get_vector_store(collection_name)
        success = await store.add_documents(documents, metadata, ids)
        
        if success:
            logger.info(f"Added {len(documents)} documents to {collection_name}")
        
        return success
    
    async def search_vector_store(
        self,
        collection_name: str,
        query: str,
        k: int = 5
    ) -> List[Dict]:
        """
        Search vector store
        
        Args:
            collection_name: Collection name
            query: Search query
            k: Number of results
            
        Returns:
            Search results
        """
        store = self.get_vector_store(collection_name, create_if_missing=False)
        if not store:
            return []
        
        results = await store.search(query, k)
        logger.info(f"Found {len(results)} results in {collection_name}")
        
        return results
    
    def list_active_sessions(self) -> List[str]:
        """
        List all active session IDs
        
        Returns:
            List of session IDs
        """
        return list(self._conversation_memories.keys())
    
    def list_vector_collections(self) -> List[str]:
        """
        List all vector store collections
        
        Returns:
            List of collection names
        """
        return list(self._vector_stores.keys())
    
    async def cleanup_inactive_sessions(self, max_sessions: int = 100) -> int:
        """
        Clean up least recently used sessions
        
        Args:
            max_sessions: Maximum number of sessions to keep
            
        Returns:
            Number of sessions cleaned up
        """
        if len(self._conversation_memories) <= max_sessions:
            return 0
        
        # Get oldest sessions (simple FIFO for now)
        sessions_to_remove = list(self._conversation_memories.keys())[:-max_sessions]
        
        for session_id in sessions_to_remove:
            del self._conversation_memories[session_id]
        
        logger.info(f"Cleaned up {len(sessions_to_remove)} inactive sessions")
        return len(sessions_to_remove)
    
    def get_memory_stats(self) -> Dict:
        """
        Get memory service statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            "active_sessions": len(self._conversation_memories),
            "vector_collections": len(self._vector_stores),
            "session_ids": list(self._conversation_memories.keys()),
            "collection_names": list(self._vector_stores.keys())
        }


# Global instance
memory_service = MemoryService()