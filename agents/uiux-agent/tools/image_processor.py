"""
Image processing tools using OpenCV and PIL
"""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict, Any
import io


class ImageProcessor:
    """Image processing utilities for design analysis"""
    
    @staticmethod
    def load_image(image_data: bytes) -> Tuple[np.ndarray, Image.Image]:
        """
        Load image from bytes
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Tuple of (OpenCV image, PIL image)
        """
        # Load as PIL Image
        pil_image = Image.open(io.BytesIO(image_data))
        
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return cv_image, pil_image
    
    @staticmethod
    def get_dimensions(image: np.ndarray) -> Dict[str, int]:
        """Get image dimensions"""
        height, width = image.shape[:2]
        return {
            "width": width,
            "height": height,
            "aspect_ratio": round(width / height, 2)
        }
    
    @staticmethod
    def detect_edges(image: np.ndarray, low_threshold: int = 50, high_threshold: int = 150) -> np.ndarray:
        """
        Detect edges using Canny edge detection
        
        Args:
            image: Input image
            low_threshold: Lower threshold for edge detection
            high_threshold: Upper threshold for edge detection
            
        Returns:
            Edge map
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, low_threshold, high_threshold)
        return edges
    
    @staticmethod
    def detect_contours(image: np.ndarray) -> List[np.ndarray]:
        """
        Detect contours in image
        
        Args:
            image: Input image
            
        Returns:
            List of contours
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return contours
    
    @staticmethod
    def detect_rectangles(image: np.ndarray, min_area: int = 1000) -> List[Dict[str, Any]]:
        """
        Detect rectangular regions (potential UI components)
        
        Args:
            image: Input image
            min_area: Minimum area to consider
            
        Returns:
            List of rectangles with coordinates and properties
        """
        edges = ImageProcessor.detect_edges(image)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            # Approximate contour to polygon
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if it's roughly rectangular (4 corners)
            if len(approx) >= 4:
                x, y, w, h = cv2.boundingRect(contour)
                rectangles.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "area": int(area),
                    "aspect_ratio": round(w / h, 2) if h > 0 else 0
                })
        
        return rectangles
    
    @staticmethod
    def calculate_grid(rectangles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze rectangles to detect grid patterns
        
        Args:
            rectangles: List of detected rectangles
            
        Returns:
            Grid information
        """
        if not rectangles:
            return {"detected": False}
        
        # Extract x and y positions
        x_positions = [r["x"] for r in rectangles]
        y_positions = [r["y"] for r in rectangles]
        
        # Find unique positions with tolerance
        tolerance = 20
        unique_x = ImageProcessor._cluster_positions(x_positions, tolerance)
        unique_y = ImageProcessor._cluster_positions(y_positions, tolerance)
        
        return {
            "detected": len(unique_x) > 1 or len(unique_y) > 1,
            "columns": len(unique_x),
            "rows": len(unique_y),
            "x_positions": unique_x,
            "y_positions": unique_y
        }
    
    @staticmethod
    def _cluster_positions(positions: List[int], tolerance: int) -> List[int]:
        """Cluster similar positions together"""
        if not positions:
            return []
        
        sorted_positions = sorted(positions)
        clusters = [[sorted_positions[0]]]
        
        for pos in sorted_positions[1:]:
            if abs(pos - clusters[-1][-1]) <= tolerance:
                clusters[-1].append(pos)
            else:
                clusters.append([pos])
        
        # Return average of each cluster
        return [int(np.mean(cluster)) for cluster in clusters]
    
    @staticmethod
    def calculate_spacing_consistency(rectangles: List[Dict[str, Any]]) -> float:
        """
        Calculate spacing consistency score (0-1)
        
        Args:
            rectangles: List of detected rectangles
            
        Returns:
            Consistency score (higher is more consistent)
        """
        if len(rectangles) < 2:
            return 1.0
        
        # Calculate gaps between rectangles
        sorted_by_x = sorted(rectangles, key=lambda r: r["x"])
        x_gaps = []
        for i in range(len(sorted_by_x) - 1):
            gap = sorted_by_x[i + 1]["x"] - (sorted_by_x[i]["x"] + sorted_by_x[i]["width"])
            if gap > 0:
                x_gaps.append(gap)
        
        sorted_by_y = sorted(rectangles, key=lambda r: r["y"])
        y_gaps = []
        for i in range(len(sorted_by_y) - 1):
            gap = sorted_by_y[i + 1]["y"] - (sorted_by_y[i]["y"] + sorted_by_y[i]["height"])
            if gap > 0:
                y_gaps.append(gap)
        
        all_gaps = x_gaps + y_gaps
        if not all_gaps:
            return 1.0
        
        # Calculate coefficient of variation (lower is more consistent)
        mean_gap = np.mean(all_gaps)
        std_gap = np.std(all_gaps)
        
        if mean_gap == 0:
            return 1.0
        
        cv = std_gap / mean_gap
        # Convert to 0-1 score (invert and normalize)
        consistency = max(0, 1 - (cv / 2))
        
        return round(consistency, 2)
    
    @staticmethod
    def resize_image(image: np.ndarray, max_dimension: int = 1920) -> np.ndarray:
        """
        Resize image maintaining aspect ratio
        
        Args:
            image: Input image
            max_dimension: Maximum width or height
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        if width <= max_dimension and height <= max_dimension:
            return image
        
        if width > height:
            new_width = max_dimension
            new_height = int((new_width / width) * height)
        else:
            new_height = max_dimension
            new_width = int((new_height / height) * width)
        
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def to_base64(image: np.ndarray, format: str = "png") -> str:
        """
        Convert OpenCV image to base64 string
        
        Args:
            image: OpenCV image
            format: Image format (png, jpg)
            
        Returns:
            Base64 encoded string with data URI
        """
        import base64
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        
        buffer = io.BytesIO()
        pil_image.save(buffer, format=format.upper())
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/{format};base64,{img_str}"