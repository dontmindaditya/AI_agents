"""
Response Generation Chain
"""
from typing import Dict, Any, Optional, List
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.services.llm_service import llm_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ResponseGenerationChain:
    """Chain for generating formatted responses"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create response generation chain"""
        prompt = PromptTemplate(
            input_variables=["data", "format", "context"],
            template="""
Generate a well-formatted response based on the provided data.

Data: {data}
Desired Format: {format}
Context: {context}

Generate a clear, concise, and well-structured response.
Ensure the response is in the requested format.

Response:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def generate(
        self,
        data: Any,
        format: str = "text",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate formatted response
        
        Args:
            data: Data to format
            format: Desired format (text, json, markdown, etc.)
            context: Optional context
            
        Returns:
            Formatted response
        """
        try:
            result = await self.chain.ainvoke({
                "data": str(data),
                "format": format,
                "context": str(context or {})
            })
            
            logger.info(f"Response generated in {format} format")
            return result
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            raise


class SummaryChain:
    """Chain for generating summaries"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create summary chain"""
        prompt = PromptTemplate(
            input_variables=["content", "max_length"],
            template="""
Create a concise summary of the following content.

Content: {content}
Maximum Length: {max_length} words

Provide a clear and informative summary that captures the key points.

Summary:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def summarize(
        self,
        content: str,
        max_length: int = 100
    ) -> str:
        """
        Generate summary of content
        
        Args:
            content: Content to summarize
            max_length: Maximum length in words
            
        Returns:
            Summary
        """
        try:
            result = await self.chain.ainvoke({
                "content": content,
                "max_length": str(max_length)
            })
            
            logger.info("Summary generated successfully")
            return result
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            raise


class ExplanationChain:
    """Chain for generating explanations"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create explanation chain"""
        prompt = PromptTemplate(
            input_variables=["topic", "audience", "detail_level"],
            template="""
Explain the following topic clearly and effectively.

Topic: {topic}
Target Audience: {audience}
Detail Level: {detail_level}

Provide a clear explanation appropriate for the target audience.
Use examples and analogies where helpful.

Explanation:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def explain(
        self,
        topic: str,
        audience: str = "general",
        detail_level: str = "moderate"
    ) -> str:
        """
        Generate explanation
        
        Args:
            topic: Topic to explain
            audience: Target audience
            detail_level: Level of detail (basic, moderate, detailed)
            
        Returns:
            Explanation
        """
        try:
            result = await self.chain.ainvoke({
                "topic": topic,
                "audience": audience,
                "detail_level": detail_level
            })
            
            logger.info("Explanation generated successfully")
            return result
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            raise


class ErrorResponseChain:
    """Chain for generating user-friendly error responses"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create error response chain"""
        prompt = PromptTemplate(
            input_variables=["error", "context"],
            template="""
Generate a user-friendly error message for the following error.

Error: {error}
Context: {context}

Provide:
1. A clear explanation of what went wrong
2. Possible causes
3. Suggested solutions or next steps

Keep the language simple and helpful.

User-Friendly Error Message:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def generate_error_response(
        self,
        error: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate user-friendly error response
        
        Args:
            error: Error message or exception
            context: Optional error context
            
        Returns:
            User-friendly error response
        """
        try:
            result = await self.chain.ainvoke({
                "error": str(error),
                "context": str(context or {})
            })
            
            logger.info("Error response generated")
            return result
        except Exception as e:
            logger.error(f"Error response generation failed: {e}")
            # Fallback to simple error message
            return f"An error occurred: {error}"


class RecommendationChain:
    """Chain for generating recommendations"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create recommendation chain"""
        prompt = PromptTemplate(
            input_variables=["context", "criteria", "num_recommendations"],
            template="""
Generate recommendations based on the provided context and criteria.

Context: {context}
Criteria: {criteria}
Number of Recommendations: {num_recommendations}

Provide {num_recommendations} well-reasoned recommendations.
For each recommendation, include:
1. The recommendation
2. Rationale
3. Expected benefits

Recommendations:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def generate_recommendations(
        self,
        context: Dict[str, Any],
        criteria: str,
        num_recommendations: int = 3
    ) -> str:
        """
        Generate recommendations
        
        Args:
            context: Context information
            criteria: Recommendation criteria
            num_recommendations: Number of recommendations to generate
            
        Returns:
            Recommendations
        """
        try:
            result = await self.chain.ainvoke({
                "context": str(context),
                "criteria": criteria,
                "num_recommendations": str(num_recommendations)
            })
            
            logger.info(f"Generated {num_recommendations} recommendations")
            return result
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise


# Global instances
response_chain = ResponseGenerationChain()
summary_chain = SummaryChain()
explanation_chain = ExplanationChain()
error_response_chain = ErrorResponseChain()
recommendation_chain = RecommendationChain()