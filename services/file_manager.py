"""
File management utilities

This module provides asynchronous file operations for managing generated
project files. It supports:
- Writing files to disk with path validation
- Reading files asynchronously
- Batch file operations
- Project directory management

Usage:
    from services.file_manager import FileManager
    
    manager = FileManager("/tmp/projects")
    
    # Write a single file
    await manager.write_file("my-project", "src/App.tsx", "export default function() {}")
    
    # Write multiple files
    await manager.write_multiple_files("my-project", [
        {"path": "src/index.tsx", "content": "..."},
        {"path": "src/App.tsx", "content": "..."}
    ])
    
    # Read a file
    content = await manager.read_file("my-project", "src/App.tsx")
"""

import os
import aiofiles
from typing import Dict, List
from utils.logger import get_logger
from utils.validator import validate_file_path

logger = get_logger(__name__)


class FileManager:
    """
    File operations manager for generated projects.
    
    This class provides async methods for reading and writing files
    with built-in path validation for security.
    
    Attributes:
        base_path: Base directory for all project files
        
    Example:
        >>> manager = FileManager("/tmp/myapp")
        >>> await manager.write_file("project-1", "README.md", "# My Project")
        >>> content = await manager.read_file("project-1", "README.md")
    """
    
    def __init__(self, base_path: str = "/tmp/agenthub"):
        """
        Initialize the file manager.
        
        Args:
            base_path: Base directory path for storing project files
        """
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    async def write_file(self, project_id: str, file_path: str, content: str) -> bool:
        """
        Write a file to disk.
        
        Args:
            project_id: Unique project identifier
            file_path: Relative path within the project
            content: File content to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate path
            is_valid, error = validate_file_path(file_path)
            if not is_valid:
                logger.error(f"Invalid path: {error}")
                return False
            
            # Create full path
            full_path = os.path.join(self.base_path, project_id, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write file
            async with aiofiles.open(full_path, 'w') as f:
                await f.write(content)
            
            logger.info(f"✅ Written: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write {file_path}: {e}")
            return False
    
    async def read_file(self, project_id: str, file_path: str) -> str:
        """Read file from disk"""
        try:
            full_path = os.path.join(self.base_path, project_id, file_path)
            
            async with aiofiles.open(full_path, 'r') as f:
                return await f.read()
                
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return ""
    
    async def write_multiple_files(
        self,
        project_id: str,
        files: List[Dict[str, str]]
    ) -> int:
        """Write multiple files"""
        count = 0
        
        for file_info in files:
            path = file_info.get("path")
            content = file_info.get("content")
            
            if path and content:
                if await self.write_file(project_id, path, content):
                    count += 1
        
        return count
    
    def get_project_path(self, project_id: str) -> str:
        """Get project directory path"""
        return os.path.join(self.base_path, project_id)