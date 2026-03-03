"""
Layout detection and analysis tools
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from tools.image_processor import ImageProcessor


class LayoutDetector:
    """Detect and analyze layout patterns"""
    
    @staticmethod
    def analyze_layout(image: np.ndarray) -> Dict[str, Any]:
        """
        Comprehensive layout analysis
        
        Args:
            image: OpenCV image
            
        Returns:
            Layout analysis results
        """
        dimensions = ImageProcessor.get_dimensions(image)
        rectangles = ImageProcessor.detect_rectangles(image)
        grid_info = ImageProcessor.calculate_grid(rectangles)
        spacing_score = ImageProcessor.calculate_spacing_consistency(rectangles)
        alignment_score = LayoutDetector.calculate_alignment_score(rectangles)
        
        return {
            "dimensions": dimensions,
            "rectangles_detected": len(rectangles),
            "grid_detected": grid_info["detected"],
            "columns": grid_info.get("columns", 0),
            "rows": grid_info.get("rows", 0),
            "spacing_consistency": spacing_score,
            "alignment_score": alignment_score,
            "complexity": LayoutDetector.calculate_complexity(rectangles),
            "layout_type": LayoutDetector.determine_layout_type(rectangles, grid_info)
        }
    
    @staticmethod
    def calculate_alignment_score(rectangles: List[Dict[str, Any]]) -> float:
        """
        Calculate alignment score (0-1)
        
        Args:
            rectangles: List of detected rectangles
            
        Returns:
            Alignment score
        """
        if len(rectangles) < 2:
            return 1.0
        
        # Check left edge alignment
        left_edges = [r["x"] for r in rectangles]
        left_alignment = LayoutDetector._calculate_position_alignment(left_edges)
        
        # Check right edge alignment
        right_edges = [r["x"] + r["width"] for r in rectangles]
        right_alignment = LayoutDetector._calculate_position_alignment(right_edges)
        
        # Check top edge alignment
        top_edges = [r["y"] for r in rectangles]
        top_alignment = LayoutDetector._calculate_position_alignment(top_edges)
        
        # Check bottom edge alignment
        bottom_edges = [r["y"] + r["height"] for r in rectangles]
        bottom_alignment = LayoutDetector._calculate_position_alignment(bottom_edges)
        
        # Average all alignments
        avg_alignment = np.mean([left_alignment, right_alignment, top_alignment, bottom_alignment])
        
        return round(avg_alignment, 2)
    
    @staticmethod
    def _calculate_position_alignment(positions: List[int], tolerance: int = 20) -> float:
        """Calculate how well positions align"""
        if len(positions) < 2:
            return 1.0
        
        # Count how many positions are within tolerance of each other
        aligned_count = 0
        total_pairs = 0
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                total_pairs += 1
                if abs(positions[i] - positions[j]) <= tolerance:
                    aligned_count += 1
        
        return aligned_count / total_pairs if total_pairs > 0 else 1.0
    
    @staticmethod
    def calculate_complexity(rectangles: List[Dict[str, Any]]) -> float:
        """
        Calculate layout complexity score (0-1)
        
        Args:
            rectangles: List of detected rectangles
            
        Returns:
            Complexity score (0 = simple, 1 = complex)
        """
        if not rectangles:
            return 0.0
        
        # Factors:
        # 1. Number of elements
        element_score = min(len(rectangles) / 50.0, 1.0)
        
        # 2. Size variance
        areas = [r["area"] for r in rectangles]
        area_variance = np.std(areas) / np.mean(areas) if np.mean(areas) > 0 else 0
        variance_score = min(area_variance / 2.0, 1.0)
        
        # 3. Positional entropy
        positions = [(r["x"], r["y"]) for r in rectangles]
        x_positions = [p[0] for p in positions]
        y_positions = [p[1] for p in positions]
        
        x_std = np.std(x_positions) if len(x_positions) > 0 else 0
        y_std = np.std(y_positions) if len(y_positions) > 0 else 0
        position_score = min((x_std + y_std) / 1000.0, 1.0)
        
        # Weighted average
        complexity = (
            element_score * 0.4 +
            variance_score * 0.3 +
            position_score * 0.3
        )
        
        return round(complexity, 2)
    
    @staticmethod
    def determine_layout_type(
        rectangles: List[Dict[str, Any]],
        grid_info: Dict[str, Any]
    ) -> str:
        """
        Determine the type of layout
        
        Args:
            rectangles: Detected rectangles
            grid_info: Grid analysis results
            
        Returns:
            Layout type name
        """
        if not rectangles:
            return "empty"
        
        # Check for grid layout
        if grid_info["detected"] and grid_info["columns"] > 2:
            return "grid"
        
        # Check for single column
        x_positions = [r["x"] for r in rectangles]
        x_variance = np.std(x_positions) if len(x_positions) > 0 else 0
        
        if x_variance < 50:
            return "single_column"
        
        # Check for sidebar layout
        sorted_by_x = sorted(rectangles, key=lambda r: r["x"])
        if len(sorted_by_x) > 5:
            left_group = sorted_by_x[:len(sorted_by_x)//3]
            right_group = sorted_by_x[len(sorted_by_x)//3:]
            
            left_x = np.mean([r["x"] for r in left_group])
            right_x = np.mean([r["x"] for r in right_group])
            
            if right_x - left_x > 200:
                return "sidebar"
        
        # Check for centered layout
        widths = [r["width"] for r in rectangles]
        avg_width = np.mean(widths)
        
        centered_count = sum(1 for r in rectangles if abs(r["x"] + r["width"]/2 - avg_width) < 100)
        if centered_count / len(rectangles) > 0.7:
            return "centered"
        
        return "mixed"
    
    @staticmethod
    def detect_sections(rectangles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Group rectangles into logical sections
        
        Args:
            rectangles: Detected rectangles
            
        Returns:
            List of sections with their rectangles
        """
        if not rectangles:
            return []
        
        # Sort by Y position
        sorted_rects = sorted(rectangles, key=lambda r: r["y"])
        
        sections = []
        current_section = {
            "rectangles": [sorted_rects[0]],
            "y_start": sorted_rects[0]["y"],
            "y_end": sorted_rects[0]["y"] + sorted_rects[0]["height"]
        }
        
        section_gap_threshold = 100
        
        for rect in sorted_rects[1:]:
            # Check if rectangle belongs to current section
            if rect["y"] - current_section["y_end"] < section_gap_threshold:
                current_section["rectangles"].append(rect)
                current_section["y_end"] = max(
                    current_section["y_end"],
                    rect["y"] + rect["height"]
                )
            else:
                # Start new section
                sections.append(current_section)
                current_section = {
                    "rectangles": [rect],
                    "y_start": rect["y"],
                    "y_end": rect["y"] + rect["height"]
                }
        
        sections.append(current_section)
        
        return sections
    
    @staticmethod
    def calculate_whitespace_ratio(image: np.ndarray, rectangles: List[Dict[str, Any]]) -> float:
        """
        Calculate ratio of whitespace to content
        
        Args:
            image: OpenCV image
            rectangles: Detected rectangles
            
        Returns:
            Whitespace ratio (0-1)
        """
        if not rectangles:
            return 1.0
        
        total_area = image.shape[0] * image.shape[1]
        content_area = sum(r["area"] for r in rectangles)
        whitespace_area = total_area - content_area
        
        return round(whitespace_area / total_area, 2) if total_area > 0 else 0.0
    
    @staticmethod
    def detect_responsive_breakpoints(rectangles: List[Dict[str, Any]]) -> List[int]:
        """
        Suggest responsive breakpoints based on layout
        
        Args:
            rectangles: Detected rectangles
            
        Returns:
            List of suggested breakpoint widths
        """
        if not rectangles:
            return [640, 768, 1024, 1280]  # Default breakpoints
        
        # Analyze rectangle widths
        widths = [r["width"] for r in rectangles]
        max_width = max(widths) if widths else 1920
        
        breakpoints = []
        
        # Small devices
        if max_width > 400:
            breakpoints.append(640)
        
        # Tablets
        if max_width > 700:
            breakpoints.append(768)
        
        # Laptops
        if max_width > 900:
            breakpoints.append(1024)
        
        # Desktops
        if max_width > 1200:
            breakpoints.append(1280)
        
        if max_width > 1400:
            breakpoints.append(1536)
        
        return breakpoints