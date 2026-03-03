from typing import Dict, Any, Optional
from ..base import BaseAgent, AgentMetadata

class TextProcessorAgent(BaseAgent):
    """
    An example agent that performs simple text processing tasks.
    """

    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Text Processor",
            description="Analyzes and transforms text input (uppercase, word count, validation).",
            version="1.0.0",
            author="Webby Example",
            tags=["text", "utility", "example"],
            inputs={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to process"},
                    "operation": {
                        "type": "string", 
                        "enum": ["uppercase", "lowercase", "count_words", "reverse"],
                        "description": "Operation to perform"
                    }
                },
                "required": ["text", "operation"]
            },
            outputs={
                "type": "object",
                "properties": {
                    "result": {"type": "string", "description": "Processed text or result"},
                    "meta": {"type": "object", "description": "Processing metadata"}
                }
            }
        )

    async def run(self, inputs: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        text = inputs.get("text", "")
        operation = inputs.get("operation", "count_words")
        
        result = ""
        
        if operation == "uppercase":
            result = text.upper()
        elif operation == "lowercase":
            result = text.lower()
        elif operation == "reverse":
            result = text[::-1]
        elif operation == "count_words":
            result = str(len(text.split())) # Store as string for consistency
        else:
            result = text  # fallback
            
        return {
            "result": result,
            "meta": {
                "length": len(text),
                "operation_used": operation
            }
        }
