"""
Data Processing Chain
"""
from typing import Dict, Any, List, Optional
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.services.llm_service import llm_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataProcessingChain:
    """Chain for processing and transforming data"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create data processing chain"""
        prompt = PromptTemplate(
            input_variables=["data", "operation"],
            template="""
You are a data processing expert. Process the given data according to the operation.

Data: {data}
Operation: {operation}

Provide:
1. Processed Result
2. Summary of changes
3. Any issues encountered

Output:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def process(
        self,
        data: Any,
        operation: str
    ) -> str:
        """
        Process data with specified operation
        
        Args:
            data: Data to process
            operation: Processing operation description
            
        Returns:
            Processing result
        """
        try:
            result = await self.chain.ainvoke({
                "data": str(data),
                "operation": operation
            })
            
            logger.info("Data processed successfully")
            return result
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            raise


class DataValidationChain:
    """Chain for validating data"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create data validation chain"""
        prompt = PromptTemplate(
            input_variables=["data", "schema"],
            template="""
Validate the given data against the provided schema or requirements.

Data: {data}
Schema/Requirements: {schema}

Provide:
1. Validation Status (Valid/Invalid)
2. Issues Found (if any)
3. Suggestions for fixing issues

Validation Result:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def validate(
        self,
        data: Any,
        schema: Dict[str, Any]
    ) -> str:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            schema: Validation schema
            
        Returns:
            Validation result
        """
        try:
            result = await self.chain.ainvoke({
                "data": str(data),
                "schema": str(schema)
            })
            
            logger.info("Data validated successfully")
            return result
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            raise


class DataTransformationChain:
    """Chain for transforming data formats"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        """Create data transformation chain"""
        prompt = PromptTemplate(
            input_variables=["data", "source_format", "target_format"],
            template="""
Transform data from one format to another.

Data: {data}
Source Format: {source_format}
Target Format: {target_format}

Provide the transformed data in the target format.
Ensure all data is preserved during transformation.

Transformed Data:
"""
        )
        
        return prompt | self.llm | StrOutputParser()
    
    async def transform(
        self,
        data: Any,
        source_format: str,
        target_format: str
    ) -> str:
        """
        Transform data from source to target format
        
        Args:
            data: Data to transform
            source_format: Source format
            target_format: Target format
            
        Returns:
            Transformed data
        """
        try:
            result = await self.chain.ainvoke({
                "data": str(data),
                "source_format": source_format,
                "target_format": target_format
            })
            
            logger.info(f"Data transformed from {source_format} to {target_format}")
            return result
        except Exception as e:
            logger.error(f"Data transformation failed: {e}")
            raise


class SequentialDataPipeline:
    """Sequential pipeline for multi-step data processing"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        self.llm = llm_service.get_model(llm_provider)
        self.validation_chain = DataValidationChain(llm_provider)
        self.processing_chain = DataProcessingChain(llm_provider)
        self.transformation_chain = DataTransformationChain(llm_provider)
    
    async def run_pipeline(
        self,
        data: Any,
        steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run data through a sequential pipeline
        
        Args:
            data: Input data
            steps: List of processing steps
            
        Returns:
            Pipeline result with all intermediate outputs
        """
        try:
            results = {
                "input": data,
                "steps": [],
                "final_output": None
            }
            
            current_data = data
            
            for i, step in enumerate(steps):
                step_type = step.get("type")
                step_config = step.get("config", {})
                
                logger.info(f"Executing pipeline step {i + 1}: {step_type}")
                
                if step_type == "validate":
                    output = await self.validation_chain.validate(
                        current_data,
                        step_config.get("schema", {})
                    )
                elif step_type == "process":
                    output = await self.processing_chain.process(
                        current_data,
                        step_config.get("operation", "")
                    )
                elif step_type == "transform":
                    output = await self.transformation_chain.transform(
                        current_data,
                        step_config.get("source_format", "json"),
                        step_config.get("target_format", "json")
                    )
                else:
                    output = current_data
                
                results["steps"].append({
                    "step": i + 1,
                    "type": step_type,
                    "output": output
                })
                
                current_data = output
            
            results["final_output"] = current_data
            
            logger.info("Pipeline execution completed")
            return results
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise


# Global instances
processing_chain = DataProcessingChain()
validation_chain = DataValidationChain()
transformation_chain = DataTransformationChain()
data_pipeline = SequentialDataPipeline()