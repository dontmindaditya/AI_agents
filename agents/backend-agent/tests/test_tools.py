"""
Tests for Tools Functionality
"""
import pytest
from app.tools.validation_tools import (
    json_validator_tool,
    email_validator_tool,
    url_validator_tool,
    data_sanitizer_tool
)
from app.tools.search_tools import (
    data_formatter_tool,
    data_aggregator_tool,
    text_analyzer_tool
)


def test_json_validator_valid():
    """Test JSON validator with valid JSON"""
    result = json_validator_tool._run('{"name": "test", "value": 123}')
    
    assert result["success"] == True
    assert result["valid"] == True
    assert "parsed_data" in result


def test_json_validator_invalid():
    """Test JSON validator with invalid JSON"""
    result = json_validator_tool._run('{"name": "test", invalid}')
    
    assert result["success"] == True
    assert result["valid"] == False
    assert "error" in result


def test_email_validator_valid():
    """Test email validator with valid email"""
    result = email_validator_tool._run("user@example.com")
    
    assert result["success"] == True
    assert result["valid"] == True


def test_email_validator_invalid():
    """Test email validator with invalid email"""
    result = email_validator_tool._run("invalid-email")
    
    assert result["success"] == True
    assert result["valid"] == False


def test_url_validator_valid():
    """Test URL validator with valid URL"""
    result = url_validator_tool._run("https://example.com")
    
    assert result["success"] == True
    assert result["valid"] == True


def test_url_validator_invalid():
    """Test URL validator with invalid URL"""
    result = url_validator_tool._run("not-a-url")
    
    assert result["success"] == True
    assert result["valid"] == False


def test_data_sanitizer():
    """Test data sanitizer"""
    result = data_sanitizer_tool._run("  Test\x00String  ", max_length=100)
    
    assert result["success"] == True
    assert result["sanitized_data"] == "TestString"
    assert result["was_modified"] == True


def test_data_formatter_json():
    """Test data formatter with JSON format"""
    data = {"name": "test", "value": 123}
    result = data_formatter_tool._run(data, "json")
    
    assert result["success"] == True
    assert "formatted_data" in result


def test_data_formatter_text():
    """Test data formatter with text format"""
    data = {"name": "test", "value": 123}
    result = data_formatter_tool._run(data, "text")
    
    assert result["success"] == True
    assert "name:" in result["formatted_data"]


def test_data_aggregator_sum():
    """Test data aggregator with sum operation"""
    data = [1, 2, 3, 4, 5]
    result = data_aggregator_tool._run(data, "sum")
    
    assert result["success"] == True
    assert result["result"] == 15


def test_data_aggregator_average():
    """Test data aggregator with average operation"""
    data = [10, 20, 30]
    result = data_aggregator_tool._run(data, "average")
    
    assert result["success"] == True
    assert result["result"] == 20


def test_data_aggregator_count():
    """Test data aggregator with count operation"""
    data = [1, 2, 3, 4, 5]
    result = data_aggregator_tool._run(data, "count")
    
    assert result["success"] == True
    assert result["result"] == 5


def test_text_analyzer():
    """Test text analyzer"""
    text = "This is a test. It has multiple sentences."
    result = text_analyzer_tool._run(text)
    
    assert result["success"] == True
    assert result["word_count"] > 0
    assert result["character_count"] > 0
    assert result["sentence_count"] >= 2


@pytest.mark.asyncio
async def test_json_validator_async():
    """Test JSON validator async method"""
    result = await json_validator_tool._arun('{"test": true}')
    
    assert result["success"] == True
    assert result["valid"] == True


@pytest.mark.asyncio
async def test_email_validator_async():
    """Test email validator async method"""
    result = await email_validator_tool._arun("test@example.com")
    
    assert result["success"] == True
    assert result["valid"] == True