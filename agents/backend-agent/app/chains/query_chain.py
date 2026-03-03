"""
Query Processing Chain
"""
from typing import Dict, Any, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.services.llm_service import llm_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryProcessingChain:
    """Chain for processing and analyzing queries"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create query processing chain"""
        prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="""
You are a query analysis expert. Analyze the given query and provide structured information.

Query: {query}
Context: {context}

Provide the following analysis:
1. Intent: What is the user trying to accomplish?
2. Entities: What are the key entities mentioned?
3. Required Actions: What actions need to be taken?
4. Data Requirements: What data is needed?
5. Expected Output: What should be returned?

Analysis:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process and analyze a query
        
        Args:
            query: Query to process
            context: Optional context information
            
        Returns:
            Query analysis
        """
        try:
            result = await self.chain.ainvoke({
                "query": query,
                "context": str(context or {})
            })
            
            logger.info("Query processed successfully")
            return result
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise
    
    def process_query_sync(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process and analyze a query (synchronous)
        
        Args:
            query: Query to process
            context: Optional context information
            
        Returns:
            Query analysis
        """
        try:
            result = self.chain.invoke({
                "query": query,
                "context": str(context or {})
            })
            
            logger.info("Query processed successfully")
            return result
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise


class QueryDecompositionChain:
    """Chain for decomposing complex queries into sub-queries"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create query decomposition chain"""
        prompt = PromptTemplate(
            input_variables=["query"],
            template="""
Break down this complex query into simpler sub-queries that can be executed independently.

Complex Query: {query}

Provide a numbered list of sub-queries. Each sub-query should be:
1. Self-contained and executable
2. Focused on a single task
3. In dependency order (if applicable)

Sub-queries:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def decompose(self, query: str) -> str:
        """
        Decompose complex query into sub-queries
        
        Args:
            query: Complex query to decompose
            
        Returns:
            List of sub-queries
        """
        try:
            result = await self.chain.ainvoke({"query": query})
            logger.info("Query decomposed successfully")
            return result
        except Exception as e:
            logger.error(f"Query decomposition failed: {e}")
            raise


# Global instances
query_chain = QueryProcessingChain()
decomposition_chain = QueryDecompositionChain()