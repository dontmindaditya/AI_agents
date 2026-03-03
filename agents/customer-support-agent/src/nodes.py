"""
Node functions for the customer support workflow graph.
Each node performs a specific task in the support pipeline.
"""

from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .models import State, QueryCategory, Sentiment
from .config import get_config

# Get configuration
config = get_config()

def categorize(state: State) -> Dict[str, str]:
    """
    Categorize the customer query into Technical, Billing, or General.
    
    Args:
        state: Current state containing the customer query
        
    Returns:
        Dictionary with the category key updated
    """
    prompt = ChatPromptTemplate.from_template(
        "Categorize the following customer query into one of these categories: "
        "Technical, Billing, General. Respond with only the category name. "
        "Query: {query}"
    )
    chain = prompt | ChatOpenAI(
        temperature=config.temperature,
        model=config.openai_model
    )
    
    try:
        category = chain.invoke({"query": state["query"]}).content.strip()
        # Validate category
        valid_categories = [QueryCategory.TECHNICAL, QueryCategory.BILLING, QueryCategory.GENERAL]
        if category not in valid_categories:
            # Default to General if invalid category
            category = QueryCategory.GENERAL
        return {"category": category}
    except Exception as e:
        print(f"Error in categorize node: {e}")
        return {"category": QueryCategory.GENERAL}

def analyze_sentiment(state: State) -> Dict[str, str]:
    """
    Analyze the sentiment of the customer query as Positive, Neutral, or Negative.
    
    Args:
        state: Current state containing the customer query
        
    Returns:
        Dictionary with the sentiment key updated
    """
    prompt = ChatPromptTemplate.from_template(
        "Analyze the sentiment of the following customer query. "
        "Respond with ONLY one word: 'Positive', 'Neutral', or 'Negative'. "
        "Query: {query}"
    )
    chain = prompt | ChatOpenAI(
        temperature=config.temperature,
        model=config.openai_model
    )
    
    try:
        sentiment = chain.invoke({"query": state["query"]}).content.strip()
        # Validate sentiment
        valid_sentiments = [Sentiment.POSITIVE, Sentiment.NEUTRAL, Sentiment.NEGATIVE]
        if sentiment not in valid_sentiments:
            # Default to Neutral if invalid sentiment
            sentiment = Sentiment.NEUTRAL
        return {"sentiment": sentiment}
    except Exception as e:
        print(f"Error in analyze_sentiment node: {e}")
        return {"sentiment": Sentiment.NEUTRAL}

def handle_technical(state: State) -> Dict[str, str]:
    """
    Provide a technical support response to the query.
    
    Args:
        state: Current state containing the customer query
        
    Returns:
        Dictionary with the response key updated
    """
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful technical support agent. Provide a clear, professional, "
        "and solution-oriented response to the following technical query. "
        "Be concise but thorough. Query: {query}"
    )
    chain = prompt | ChatOpenAI(
        temperature=config.temperature,
        model=config.openai_model
    )
    
    try:
        response = chain.invoke({"query": state["query"]}).content
        return {"response": response}
    except Exception as e:
        print(f"Error in handle_technical node: {e}")
        return {"response": "We apologize for the inconvenience. Please contact our technical support team directly for assistance."}

def handle_billing(state: State) -> Dict[str, str]:
    """
    Provide a billing support response to the query.
    
    Args:
        state: Current state containing the customer query
        
    Returns:
        Dictionary with the response key updated
    """
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful billing support agent. Provide a clear, professional response "
        "to the following billing query. Be helpful and guide the customer to the right resources. "
        "Query: {query}"
    )
    chain = prompt | ChatOpenAI(
        temperature=config.temperature,
        model=config.openai_model
    )
    
    try:
        response = chain.invoke({"query": state["query"]}).content
        return {"response": response}
    except Exception as e:
        print(f"Error in handle_billing node: {e}")
        return {"response": "We apologize for the inconvenience. Please contact our billing department directly for assistance."}

def handle_general(state: State) -> Dict[str, str]:
    """
    Provide a general support response to the query.
    
    Args:
        state: Current state containing the customer query
        
    Returns:
        Dictionary with the response key updated
    """
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful customer support agent. Provide a friendly, professional response "
        "to the following general query. Be informative and helpful. "
        "Query: {query}"
    )
    chain = prompt | ChatOpenAI(
        temperature=config.temperature,
        model=config.openai_model
    )
    
    try:
        response = chain.invoke({"query": state["query"]}).content
        return {"response": response}
    except Exception as e:
        print(f"Error in handle_general node: {e}")
        return {"response": "Thank you for contacting us. Please reach out to our support team for further assistance."}

def escalate(state: State) -> Dict[str, str]:
    """
    Escalate the query to a human agent due to negative sentiment.
    
    Args:
        state: Current state containing the customer query
        
    Returns:
        Dictionary with the response key updated with escalation message
    """
    return {
        "response": (
            "We understand your concern and take it seriously. "
            "This query has been escalated to a human agent who will respond shortly. "
            "Thank you for your patience."
        )
    }

def route_query(state: State) -> str:
    """
    Route the query based on its sentiment and category.
    
    Args:
        state: Current state containing category and sentiment
        
    Returns:
        Name of the next node to execute
    """
    # Priority: Escalate negative sentiment first
    if state.get("sentiment") == Sentiment.NEGATIVE:
        return "escalate"
    
    # Route based on category
    category = state.get("category", QueryCategory.GENERAL)
    if category == QueryCategory.TECHNICAL:
        return "handle_technical"
    elif category == QueryCategory.BILLING:
        return "handle_billing"
    else:
        return "handle_general"