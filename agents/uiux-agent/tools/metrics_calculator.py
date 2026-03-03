"""
Design metrics and quality assessment tools
"""
from typing import List, Dict, Any
import numpy as np


class MetricsCalculator:
    """Calculate various design quality metrics"""
    
    @staticmethod
    def calculate_visual_balance(
        components: List[Dict[str, Any]],
        image_dimensions: Dict[str, int]
    ) -> float:
        """
        Calculate visual balance score (0-1)
        
        Uses center of mass calculation
        
        Args:
            components: List of UI components
            image_dimensions: Image width and height
            
        Returns:
            Balance score (1.0 = perfectly balanced)
        """
        if not components:
            return 1.0
        
        img_width = image_dimensions["width"]
        img_height = image_dimensions["height"]
        img_center_x = img_width / 2
        img_center_y = img_height / 2
        
        # Calculate weighted center of mass
        total_area = 0
        weighted_x = 0
        weighted_y = 0
        
        for comp in components:
            pos = comp["position"]
            area = pos["width"] * pos["height"]
            center_x = pos["x"] + pos["width"] / 2
            center_y = pos["y"] + pos["height"] / 2
            
            total_area += area
            weighted_x += center_x * area
            weighted_y += center_y * area
        
        if total_area == 0:
            return 1.0
        
        com_x = weighted_x / total_area
        com_y = weighted_y / total_area
        
        # Calculate distance from image center
        distance = np.sqrt((com_x - img_center_x)**2 + (com_y - img_center_y)**2)
        max_distance = np.sqrt(img_center_x**2 + img_center_y**2)
        
        # Convert to balance score (closer to center = higher score)
        balance = 1.0 - (distance / max_distance)
        
        return round(balance, 2)
    
    @staticmethod
    def calculate_density(
        components: List[Dict[str, Any]],
        image_dimensions: Dict[str, int]
    ) -> float:
        """
        Calculate content density (0-1)
        
        Args:
            components: List of UI components
            image_dimensions: Image width and height
            
        Returns:
            Density score
        """
        if not components:
            return 0.0
        
        total_area = image_dimensions["width"] * image_dimensions["height"]
        content_area = sum(
            comp["position"]["width"] * comp["position"]["height"]
            for comp in components
        )
        
        density = content_area / total_area if total_area > 0 else 0.0
        
        return round(density, 2)
    
    @staticmethod
    def calculate_hierarchy_score(components: List[Dict[str, Any]]) -> float:
        """
        Calculate visual hierarchy score based on size variance
        
        Args:
            components: List of UI components
            
        Returns:
            Hierarchy score (0-1)
        """
        if len(components) < 2:
            return 1.0
        
        # Calculate size variance
        areas = [
            comp["position"]["width"] * comp["position"]["height"]
            for comp in components
        ]
        
        mean_area = np.mean(areas)
        std_area = np.std(areas)
        
        if mean_area == 0:
            return 0.0
        
        # Coefficient of variation
        cv = std_area / mean_area
        
        # Good hierarchy has moderate variance (not too uniform, not too chaotic)
        # Optimal CV around 0.5-1.5
        if cv < 0.3:
            score = cv / 0.3  # Too uniform
        elif cv <= 1.5:
            score = 1.0  # Good hierarchy
        else:
            score = max(0, 1.0 - (cv - 1.5) / 2.0)  # Too chaotic
        
        return round(score, 2)
    
    @staticmethod
    def calculate_rhythm_score(components: List[Dict[str, Any]]) -> float:
        """
        Calculate visual rhythm/consistency score
        
        Args:
            components: List of UI components
            
        Returns:
            Rhythm score (0-1)
        """
        if len(components) < 3:
            return 1.0
        
        # Sort by position
        sorted_by_x = sorted(components, key=lambda c: c["position"]["x"])
        sorted_by_y = sorted(components, key=lambda c: c["position"]["y"])
        
        # Calculate spacing between consecutive elements
        x_spacings = []
        for i in range(len(sorted_by_x) - 1):
            current = sorted_by_x[i]["position"]
            next_comp = sorted_by_x[i + 1]["position"]
            spacing = next_comp["x"] - (current["x"] + current["width"])
            if spacing > 0:
                x_spacings.append(spacing)
        
        y_spacings = []
        for i in range(len(sorted_by_y) - 1):
            current = sorted_by_y[i]["position"]
            next_comp = sorted_by_y[i + 1]["position"]
            spacing = next_comp["y"] - (current["y"] + current["height"])
            if spacing > 0:
                y_spacings.append(spacing)
        
        all_spacings = x_spacings + y_spacings
        
        if not all_spacings:
            return 1.0
        
        # Calculate consistency (lower std = more rhythmic)
        mean_spacing = np.mean(all_spacings)
        std_spacing = np.std(all_spacings)
        
        if mean_spacing == 0:
            return 1.0
        
        cv = std_spacing / mean_spacing
        rhythm = max(0, 1.0 - (cv / 2.0))
        
        return round(rhythm, 2)
    
    @staticmethod
    def calculate_symmetry_score(
        components: List[Dict[str, Any]],
        image_dimensions: Dict[str, int]
    ) -> float:
        """
        Calculate symmetry score
        
        Args:
            components: List of UI components
            image_dimensions: Image width and height
            
        Returns:
            Symmetry score (0-1)
        """
        if not components:
            return 1.0
        
        img_width = image_dimensions["width"]
        center_x = img_width / 2
        
        # Compare left and right halves
        left_components = [c for c in components if c["position"]["x"] + c["position"]["width"]/2 < center_x]
        right_components = [c for c in components if c["position"]["x"] + c["position"]["width"]/2 >= center_x]
        
        # Calculate total area on each side
        left_area = sum(c["position"]["width"] * c["position"]["height"] for c in left_components)
        right_area = sum(c["position"]["width"] * c["position"]["height"] for c in right_components)
        
        total_area = left_area + right_area
        if total_area == 0:
            return 1.0
        
        # Calculate symmetry (how close left and right areas are)
        symmetry = 1.0 - abs(left_area - right_area) / total_area
        
        return round(symmetry, 2)
    
    @staticmethod
    def calculate_proximity_score(components: List[Dict[str, Any]]) -> float:
        """
        Calculate how well related elements are grouped (Gestalt proximity)
        
        Args:
            components: List of UI components
            
        Returns:
            Proximity score (0-1)
        """
        if len(components) < 2:
            return 1.0
        
        # Group components by type
        type_groups = {}
        for comp in components:
            comp_type = comp["type"]
            if comp_type not in type_groups:
                type_groups[comp_type] = []
            type_groups[comp_type].append(comp)
        
        # For each type, calculate average distance between same-type components
        type_distances = []
        
        for comp_type, comps in type_groups.items():
            if len(comps) < 2:
                continue
            
            distances = []
            for i, comp1 in enumerate(comps):
                for comp2 in comps[i+1:]:
                    # Calculate center distance
                    c1_x = comp1["position"]["x"] + comp1["position"]["width"] / 2
                    c1_y = comp1["position"]["y"] + comp1["position"]["height"] / 2
                    c2_x = comp2["position"]["x"] + comp2["position"]["width"] / 2
                    c2_y = comp2["position"]["y"] + comp2["position"]["height"] / 2
                    
                    distance = np.sqrt((c1_x - c2_x)**2 + (c1_y - c2_y)**2)
                    distances.append(distance)
            
            if distances:
                type_distances.append(np.mean(distances))
        
        if not type_distances:
            return 1.0
        
        # Lower average distance = better proximity
        avg_distance = np.mean(type_distances)
        # Normalize (assuming 500px is far, 100px is close)
        proximity = max(0, 1.0 - (avg_distance - 100) / 400)
        
        return round(proximity, 2)
    
    @staticmethod
    def calculate_overall_quality(metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate overall design quality from individual metrics
        
        Args:
            metrics: Dictionary of individual metric scores
            
        Returns:
            Overall quality assessment
        """
        # Weighted average of metrics
        weights = {
            "balance": 0.15,
            "hierarchy": 0.20,
            "rhythm": 0.15,
            "spacing_consistency": 0.15,
            "alignment": 0.15,
            "symmetry": 0.10,
            "proximity": 0.10
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for metric_name, weight in weights.items():
            if metric_name in metrics:
                weighted_sum += metrics[metric_name] * weight
                total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0.5
        
        # Classify quality
        if overall_score >= 0.8:
            quality_rating = "excellent"
        elif overall_score >= 0.6:
            quality_rating = "good"
        elif overall_score >= 0.4:
            quality_rating = "fair"
        else:
            quality_rating = "needs_improvement"
        
        return {
            "overall_score": round(overall_score, 2),
            "rating": quality_rating,
            "individual_metrics": metrics
        }
    
    @staticmethod
    def calculate_all_metrics(
        components: List[Dict[str, Any]],
        layout_metrics: Dict[str, Any],
        image_dimensions: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Calculate all design metrics
        
        Args:
            components: List of UI components
            layout_metrics: Layout analysis metrics
            image_dimensions: Image dimensions
            
        Returns:
            Complete metrics dictionary
        """
        metrics = {
            "balance": MetricsCalculator.calculate_visual_balance(components, image_dimensions),
            "density": MetricsCalculator.calculate_density(components, image_dimensions),
            "hierarchy": MetricsCalculator.calculate_hierarchy_score(components),
            "rhythm": MetricsCalculator.calculate_rhythm_score(components),
            "symmetry": MetricsCalculator.calculate_symmetry_score(components, image_dimensions),
            "proximity": MetricsCalculator.calculate_proximity_score(components),
            "spacing_consistency": layout_metrics.get("spacing_consistency", 0.5),
            "alignment": layout_metrics.get("alignment_score", 0.5)
        }
        
        quality = MetricsCalculator.calculate_overall_quality(metrics)
        
        return {
            **metrics,
            "overall_quality": quality
        }