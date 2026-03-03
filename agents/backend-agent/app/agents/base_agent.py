"""
Base Agent Class
"""
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool

from app.services.llm_service import llm_service
from app.utils.logger import setup_logger
from app.utils.helpers import generate_task_id

logger = setup_logger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(
        self,
        name: str,
        description: str,
        tools: List[BaseTool],
        llm_provider: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.tools = tools
        self.llm_provider = llm_provider
        self.llm = llm_service.get_model(llm_provider)
        self.agent_executor = self._create_agent()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get agent-specific system prompt"""
        pass
    
    def _create_agent(self) -> AgentExecutor:
        """Create agent executor"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.get_system_prompt()),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ])
            
            agent = create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
            
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=10
            )
            
            logger.info(f"Agent '{self.name}' created successfully")
            return agent_executor
        except Exception as e:
            logger.error(f"Failed to create agent '{self.name}': {e}")
            raise
    
    async def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute agent task
        
        Args:
            task: Task description
            context: Optional context data
            
        Returns:
            Execution result
        """
        try:
            task_id = generate_task_id()
            logger.info(f"Agent '{self.name}' executing task: {task_id}")
            
            input_data = {
                "input": task,
                "context": context or {}
            }
            
            result = await self.agent_executor.ainvoke(input_data)
            
            logger.info(f"Agent '{self.name}' completed task: {task_id}")
            
            return {
                "task_id": task_id,
                "agent": self.name,
                "success": True,
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            logger.error(f"Agent '{self.name}' failed: {e}")
            return {
                "task_id": task_id,
                "agent": self.name,
                "success": False,
                "error": str(e)
            }
    
    def execute_sync(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute agent task (synchronous)
        
        Args:
            task: Task description
            context: Optional context data
            
        Returns:
            Execution result
        """
        try:
            task_id = generate_task_id()
            logger.info(f"Agent '{self.name}' executing task: {task_id}")
            
            input_data = {
                "input": task,
                "context": context or {}
            }
            
            result = self.agent_executor.invoke(input_data)
            
            logger.info(f"Agent '{self.name}' completed task: {task_id}")
            
            return {
                "task_id": task_id,
                "agent": self.name,
                "success": True,
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            logger.error(f"Agent '{self.name}' failed: {e}")
            return {
                "task_id": generate_task_id(),
                "agent": self.name,
                "success": False,
                "error": str(e)
            }