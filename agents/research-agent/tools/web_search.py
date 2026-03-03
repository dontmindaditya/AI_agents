"""
Web search tools for research agent
"""

import os
import requests
from typing import List, Dict, Optional
from utils.helpers import print_error, print_info


class WebSearchTool:
    """Handle web searches using various APIs"""
    
    def __init__(self):
        """Initialize web search tool"""
        self.serper_api_key = os.getenv('SERPER_API_KEY')
    
    def search_serper(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search using Serper API
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.serper_api_key:
            print_error("SERPER_API_KEY not found in environment variables")
            return []
        
        try:
            url = "https://google.serper.dev/search"
            
            payload = {
                "q": query,
                "num": num_results
            }
            
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            if 'organic' in data:
                for item in data['organic'][:num_results]:
                    results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })
            
            return results
        
        except requests.exceptions.RequestException as e:
            print_error(f"Search request failed: {str(e)}")
            return []
        except Exception as e:
            print_error(f"Search error: {str(e)}")
            return []
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform web search using available API
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        print_info(f"Searching for: {query}")
        
        # Try Serper API if available
        if self.serper_api_key:
            results = self.search_serper(query, num_results)
            if results:
                return results
        
        # If no API key or search failed, return empty
        print_error("No search API configured. Please add SERPER_API_KEY to .env")
        return []
    
    def format_results(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results as text
        
        Args:
            results: List of search results
            
        Returns:
            Formatted text
        """
        if not results:
            return "No search results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"\n{i}. {result['title']}")
            formatted.append(f"   URL: {result['link']}")
            formatted.append(f"   {result['snippet']}")
        
        return "\n".join(formatted)


class SimpleWebSearch:
    """
    Simple web search wrapper that can be used without API keys
    This version provides structured search capability for the agents
    """
    
    def __init__(self):
        """Initialize simple web search"""
        self.web_tool = WebSearchTool()
    
    def search(self, query: str) -> str:
        """
        Perform a web search and return formatted results
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results as string
        """
        results = self.web_tool.search(query, num_results=5)
        return self.web_tool.format_results(results)
    
    def search_multiple(self, queries: List[str]) -> Dict[str, str]:
        """
        Perform multiple searches
        
        Args:
            queries: List of search queries
            
        Returns:
            Dictionary mapping queries to results
        """
        results = {}
        for query in queries:
            results[query] = self.search(query)
        return results


def create_search_tool():
    """
    Factory function to create a search tool instance
    
    Returns:
        SimpleWebSearch instance
    """
    return SimpleWebSearch()