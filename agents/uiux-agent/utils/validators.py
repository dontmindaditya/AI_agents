"""
Input and output validators
"""
from pathlib import Path
from typing import Optional
import base64
from PIL import Image
import io
from config import settings


class ValidationError(Exception):
    """Custom validation error"""
    pass


class ImageValidator:
    """Validator for image inputs"""
    
    @staticmethod
    def validate_file_path(file_path: str) -> Path:
        """
        Validate image file path exists and is supported format
        
        Args:
            file_path: Path to image file
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If file doesn't exist or format not supported
        """
        path = Path(file_path)
        
        if not path.exists():
            raise ValidationError(f"Image file not found: {file_path}")
        
        if not path.is_file():
            raise ValidationError(f"Path is not a file: {file_path}")
        
        extension = path.suffix.lower().replace(".", "")
        supported_formats = settings.get_supported_formats()
        
        if extension not in supported_formats:
            raise ValidationError(
                f"Unsupported image format: {extension}. "
                f"Supported formats: {', '.join(supported_formats)}"
            )
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > settings.max_image_size:
            max_mb = settings.max_image_size / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            raise ValidationError(
                f"Image file too large: {actual_mb:.2f}MB. "
                f"Maximum size: {max_mb:.2f}MB"
            )
        
        return path
    
    @staticmethod
    def validate_image_data(image_data: bytes) -> Image.Image:
        """
        Validate image data can be loaded
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            PIL Image object
            
        Raises:
            ValidationError: If image data is invalid
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            # Reopen after verify (verify closes the file)
            image = Image.open(io.BytesIO(image_data))
            return image
        except Exception as e:
            raise ValidationError(f"Invalid image data: {str(e)}")
    
    @staticmethod
    def load_image(file_path: str) -> tuple[bytes, Image.Image]:
        """
        Load and validate image from file
        
        Args:
            file_path: Path to image file
            
        Returns:
            Tuple of (raw_bytes, PIL_Image)
        """
        path = ImageValidator.validate_file_path(file_path)
        
        with open(path, "rb") as f:
            image_data = f.read()
        
        image = ImageValidator.validate_image_data(image_data)
        
        return image_data, image
    
    @staticmethod
    def image_to_base64(image_data: bytes, image_format: str = "png") -> str:
        """
        Convert image data to base64 string with data URI
        
        Args:
            image_data: Raw image bytes
            image_format: Image format (png, jpeg, etc.)
            
        Returns:
            Base64 data URI string
        """
        b64_data = base64.b64encode(image_data).decode("utf-8")
        mime_type = f"image/{image_format}"
        return f"data:{mime_type};base64,{b64_data}"


class TaskValidator:
    """Validator for task inputs"""
    
    @staticmethod
    def validate_task(task: str) -> str:
        """
        Validate task string
        
        Args:
            task: User task description
            
        Returns:
            Validated task string
            
        Raises:
            ValidationError: If task is invalid
        """
        if not task or not task.strip():
            raise ValidationError("Task cannot be empty")
        
        task = task.strip()
        
        if len(task) < 10:
            raise ValidationError("Task description too short (minimum 10 characters)")
        
        if len(task) > 5000:
            raise ValidationError("Task description too long (maximum 5000 characters)")
        
        return task


class CodeValidator:
    """Validator for generated code"""
    
    @staticmethod
    def validate_react_component(code: str) -> bool:
        """
        Basic validation for React component code
        
        Args:
            code: React component code
            
        Returns:
            True if valid
        """
        required_patterns = [
            "function ",  # or "const ... = "
            "return",
            "export"
        ]
        
        # Check for at least some required patterns
        valid_patterns = sum(1 for pattern in required_patterns if pattern in code)
        
        if valid_patterns < 2:
            return False
        
        # Check for balanced braces
        open_braces = code.count("{")
        close_braces = code.count("}")
        
        return open_braces == close_braces
    
    @staticmethod
    def validate_html(code: str) -> bool:
        """
        Basic validation for HTML code
        
        Args:
            code: HTML code
            
        Returns:
            True if valid
        """
        required_elements = ["<", ">"]
        
        return all(elem in code for elem in required_elements)
    
    @staticmethod
    def validate_css(code: str) -> bool:
        """
        Basic validation for CSS code
        
        Args:
            code: CSS code
            
        Returns:
            True if valid
        """
        # Check for basic CSS structure
        has_selector = "{" in code and "}" in code
        has_property = ":" in code and ";" in code
        
        return has_selector or has_property


def validate_hex_color(color: str) -> bool:
    """
    Validate hex color code
    
    Args:
        color: Hex color string (e.g., #FFFFFF or #FFF)
        
    Returns:
        True if valid hex color
    """
    if not color.startswith("#"):
        return False
    
    color = color[1:]
    
    if len(color) not in [3, 6]:
        return False
    
    try:
        int(color, 16)
        return True
    except ValueError:
        return False