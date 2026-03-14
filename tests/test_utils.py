"""
Test suite for utility functions.
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

import pytest
from utils.validator import (
    validate_project_name,
    validate_project_type,
    validate_framework,
    validate_file_path,
    validate_code_length
)
from utils.parser import (
    extract_json_from_text,
    clean_code_block,
    extract_imports,
    extract_exports
)


class TestValidateProjectName:
    """Tests for project name validation."""

    def test_valid_name(self):
        """Test valid project names."""
        valid_names = ["My Project", "project-123", "test_app", "Project App 2024"]
        
        for name in valid_names:
            is_valid, error = validate_project_name(name)
            assert is_valid is True
            assert error is None

    def test_too_short(self):
        """Test that names shorter than 3 chars are rejected."""
        is_valid, error = validate_project_name("ab")
        assert is_valid is False
        assert "at least 3 characters" in error

    def test_too_long(self):
        """Test that names longer than 100 chars are rejected."""
        is_valid, error = validate_project_name("a" * 101)
        assert is_valid is False
        assert "less than 100 characters" in error

    def test_invalid_characters(self):
        """Test that invalid characters are rejected."""
        is_valid, error = validate_project_name("project@#!")
        assert is_valid is False
        assert "can only contain" in error


class TestValidateProjectType:
    """Tests for project type validation."""

    def test_valid_types(self):
        """Test valid project types."""
        valid_types = ["website", "webapp", "dashboard", "saas", "api", "ecommerce", "blog", "portfolio"]
        
        for project_type in valid_types:
            is_valid, error = validate_project_type(project_type)
            assert is_valid is True

    def test_invalid_type(self):
        """Test invalid project type."""
        is_valid, error = validate_project_type("invalid_type")
        assert is_valid is False
        assert "Invalid project type" in error


class TestValidateFramework:
    """Tests for framework validation."""

    def test_valid_frameworks(self):
        """Test valid frameworks."""
        valid_frameworks = ["nextjs", "react", "vue", "angular", "svelte"]
        
        for framework in valid_frameworks:
            is_valid, error = validate_framework(framework)
            assert is_valid is True

    def test_invalid_framework(self):
        """Test invalid framework."""
        is_valid, error = validate_framework("invalid")
        assert is_valid is False
        assert "Invalid framework" in error


class TestValidateFilePath:
    """Tests for file path validation."""

    def test_valid_paths(self):
        """Test valid file paths."""
        valid_paths = ["src/App.tsx", "components/Button.js", "src/utils/helpers.ts"]
        
        for path in valid_paths:
            is_valid, error = validate_file_path(path)
            assert is_valid is True

    def test_path_traversal(self):
        """Test that path traversal is rejected."""
        is_valid, error = validate_file_path("../etc/passwd")
        assert is_valid is False
        assert "cannot contain" in error

    def test_absolute_path(self):
        """Test that absolute paths are rejected."""
        is_valid, error = validate_file_path("/etc/passwd")
        assert is_valid is False
        assert "cannot be absolute" in error

    def test_path_too_long(self):
        """Test that too long paths are rejected."""
        is_valid, error = validate_file_path("a" * 501)
        assert is_valid is False
        assert "too long" in error


class TestValidateCodeLength:
    """Tests for code length validation."""

    def test_valid_length(self):
        """Test valid code lengths."""
        is_valid, error = validate_code_length("x" * 50000)
        assert is_valid is True

    def test_too_long(self):
        """Test that too long code is rejected."""
        is_valid, error = validate_code_length("x" * 50001)
        assert is_valid is False
        assert "exceeds maximum length" in error


class TestExtractJsonFromText:
    """Tests for JSON extraction."""

    def test_direct_json(self):
        """Test extracting direct JSON."""
        text = '{"key": "value", "number": 123}'
        result = extract_json_from_text(text)
        
        assert result == {"key": "value", "number": 123}

    def test_json_in_markdown(self):
        """Test extracting JSON from markdown code block."""
        text = '''
        Here is the JSON:
        ```json
        {"name": "test"}
        ```
        '''
        result = extract_json_from_text(text)
        
        assert result == {"name": "test"}

    def test_no_json(self):
        """Test that non-JSON text returns None."""
        result = extract_json_from_text("This is just text")
        assert result is None


class TestCleanCodeBlock:
    """Tests for code block cleaning."""

    def test_clean_markdown_code_block(self):
        """Test cleaning markdown code blocks."""
        code = '''```javascript
const x = 1;
```'''
        
        result = clean_code_block(code)
        assert result == "const x = 1;"

    def test_clean_with_language_prefix(self):
        """Test cleaning with language prefix."""
        code = '''```typescript
type Foo = string;
```'''
        
        result = clean_code_block(code)
        assert "type Foo = string;" in result


class TestExtractImports:
    """Tests for import extraction."""

    def test_extract_imports(self):
        """Test extracting import statements."""
        code = '''
import React from 'react';
import { useState } from 'react';
import './styles.css';
'''
        
        imports = extract_imports(code)
        assert len(imports) == 3
        assert "import React from 'react'" in imports


class TestExtractExports:
    """Tests for export extraction."""

    def test_extract_exports(self):
        """Test extracting export statements."""
        code = '''
export const foo = 'bar';
export default function App() {}
export { useState };
'''
        
        exports = extract_exports(code)
        assert len(exports) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
