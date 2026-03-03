"""File management utilities"""

import os
import aiofiles
from typing import Dict, List
from utils.logger import get_logger
from utils.validator import validate_file_path

logger = get_logger(__name__)


class FileManager:
    """File operations manager"""
    
    def __init__(self, base_path: str = "/tmp/webby"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    async def write_file(self, project_id: str, file_path: str, content: str) -> bool:
        """Write file to disk"""
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