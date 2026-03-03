"""
Search and Utility Tools for Agents
"""
from typing import Any, Dict, List, Optional
from langchain.tools import BaseTool
import json

from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class WebSearchTool(BaseTool):
    """Tool for web search (placeholder for actual search API)"""
    
    name: str = "web_search"
    description: str = """
    Search the web for information.
    Input should be a search query string.
    Returns search results.
    """
    
    def _run(self, query: str) -> Dict[str, Any]:
        """Execute web search"""
        try:
            # Placeholder implementation
            # In production, integrate with actual search API (Google, Bing, etc.)
            logger.info(f"Web search query: {query}")
            
            return {
                "success": True,
                "query": query,
                "results": [],
                "message": "Web search tool is a placeholder. Integrate with actual search API."
            }
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, query: str) -> Dict[str, Any]:
        """Async wrapper for web search"""
        return self._run(query)


class DataFormatterTool(BaseTool):
    """Tool for formatting data"""
    
    name: str = "data_formatter"
    description: str = """
    Format data into different structures (JSON, CSV-like, readable text).
    Input should be data and desired format ('json', 'text', 'table').
    Returns formatted data.
    """
    
    def _run(self, data: Any, format_type: str = "json") -> Dict[str, Any]:
        """Format data"""
        try:
            if format_type.lower() == "json":
                formatted = json.dumps(data, indent=2)
            elif format_type.lower() == "text":
                if isinstance(data, dict):
                    formatted = "\n".join([f"{k}: {v}" for k, v in data.items()])
                elif isinstance(data, list):
                    formatted = "\n".join([str(item) for item in data])
                else:
                    formatted = str(data)
            elif format_type.lower() == "table":
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    # Simple table formatting
                    headers = list(data[0].keys())
                    formatted = " | ".join(headers) + "\n"
                    formatted += "-" * len(formatted) + "\n"
                    for item in data:
                        row = " | ".join([str(item.get(h, "")) for h in headers])
                        formatted += row + "\n"
                else:
                    formatted = str(data)
            else:
                formatted = str(data)
            
            return {
                "success": True,
                "format": format_type,
                "formatted_data": formatted
            }
        except Exception as e:
            logger.error(f"Data formatting failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, data: Any, format_type: str = "json") -> Dict[str, Any]:
        """Async wrapper for data formatting"""
        return self._run(data, format_type)


class DataAggregatorTool(BaseTool):
    """Tool for aggregating data"""
    
    name: str = "data_aggregator"
    description: str = """
    Aggregate data using common operations (count, sum, average, min, max).
    Input should be a list of numbers and operation type.
    Returns aggregated result.
    """
    
    def _run(self, data: List[float], operation: str = "sum") -> Dict[str, Any]:
        """Aggregate data"""
        try:
            if not data:
                return {
                    "success": False,
                    "error": "No data provided"
                }
            
            result = None
            operation = operation.lower()
            
            if operation == "count":
                result = len(data)
            elif operation == "sum":
                result = sum(data)
            elif operation == "average" or operation == "mean":
                result = sum(data) / len(data)
            elif operation == "min":
                result = min(data)
            elif operation == "max":
                result = max(data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
            return {
                "success": True,
                "operation": operation,
                "result": result,
                "data_count": len(data)
            }
        except Exception as e:
            logger.error(f"Data aggregation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, data: List[float], operation: str = "sum") -> Dict[str, Any]:
        """Async wrapper for data aggregation"""
        return self._run(data, operation)


class TextAnalyzerTool(BaseTool):
    """Tool for analyzing text"""
    
    name: str = "text_analyzer"
    description: str = """
    Analyze text and provide statistics (word count, character count, etc.).
    Input should be a text string.
    Returns analysis results.
    """
    
    def _run(self, text: str) -> Dict[str, Any]:
        """Analyze text"""
        try:
            words = text.split()
            sentences = text.split('.')
            lines = text.split('\n')
            
            return {
                "success": True,
                "character_count": len(text),
                "word_count": len(words),
                "sentence_count": len([s for s in sentences if s.strip()]),
                "line_count": len(lines),
                "average_word_length": sum(len(w) for w in words) / len(words) if words else 0,
                "unique_words": len(set(word.lower() for word in words))
            }
        except Exception as e:
            logger.error(f"Text analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, text: str) -> Dict[str, Any]:
        """Async wrapper for text analysis"""
        return self._run(text)


class DataFilterTool(BaseTool):
    """Tool for filtering data"""
    
    name: str = "data_filter"
    description: str = """
    Filter a list of dictionaries based on conditions.
    Input should be data (list of dicts) and a filter condition (key, operator, value).
    Returns filtered results.
    """
    
    def _run(self, data: List[Dict[str, Any]], key: str, operator: str, value: Any) -> Dict[str, Any]:
        """Filter data"""
        try:
            if not isinstance(data, list):
                return {
                    "success": False,
                    "error": "Data must be a list"
                }
            
            filtered = []
            operator = operator.lower()
            
            for item in data:
                if not isinstance(item, dict) or key not in item:
                    continue
                
                item_value = item[key]
                
                if operator == "eq" or operator == "==":
                    if item_value == value:
                        filtered.append(item)
                elif operator == "ne" or operator == "!=":
                    if item_value != value:
                        filtered.append(item)
                elif operator == "gt" or operator == ">":
                    if item_value > value:
                        filtered.append(item)
                elif operator == "gte" or operator == ">=":
                    if item_value >= value:
                        filtered.append(item)
                elif operator == "lt" or operator == "<":
                    if item_value < value:
                        filtered.append(item)
                elif operator == "lte" or operator == "<=":
                    if item_value <= value:
                        filtered.append(item)
                elif operator == "contains":
                    if str(value).lower() in str(item_value).lower():
                        filtered.append(item)
            
            return {
                "success": True,
                "original_count": len(data),
                "filtered_count": len(filtered),
                "results": filtered
            }
        except Exception as e:
            logger.error(f"Data filtering failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _arun(self, data: List[Dict[str, Any]], key: str, operator: str, value: Any) -> Dict[str, Any]:
        """Async wrapper for data filtering"""
        return self._run(data, key, operator, value)


# Tool instances
web_search_tool = WebSearchTool()
data_formatter_tool = DataFormatterTool()
data_aggregator_tool = DataAggregatorTool()
text_analyzer_tool = TextAnalyzerTool()
data_filter_tool = DataFilterTool()

# Export all search and utility tools
search_tools = [
    web_search_tool,
    data_formatter_tool,
    data_aggregator_tool,
    text_analyzer_tool,
    data_filter_tool
]