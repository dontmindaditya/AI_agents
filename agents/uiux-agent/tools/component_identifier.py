"""
UI component identification tools
"""
from typing import List, Dict, Any, Optional
import numpy as np


class ComponentIdentifier:
    """Identify UI components from layout analysis"""
    
    # Component identification rules based on dimensions and position
    COMPONENT_RULES = {
        "navbar": {
            "height_ratio": (0.05, 0.15),  # 5-15% of screen height
            "position_y": (0, 0.2),  # Top 20% of screen
            "width_ratio": (0.8, 1.0)  # 80-100% of screen width
        },
        "footer": {
            "height_ratio": (0.05, 0.2),
            "position_y": (0.8, 1.0),  # Bottom 20% of screen
            "width_ratio": (0.8, 1.0)
        },
        "sidebar": {
            "width_ratio": (0.15, 0.3),  # 15-30% of screen width
            "height_ratio": (0.4, 1.0),  # Tall
            "position_x": [(0, 0.2), (0.8, 1.0)]  # Left or right edge
        },
        "card": {
            "aspect_ratio": (0.6, 2.5),  # Vertical or square-ish
            "size_range": (5000, 200000)  # Medium-sized
        },
        "button": {
            "aspect_ratio": (1.5, 5.0),  # Horizontal rectangle
            "size_range": (500, 15000)  # Small to medium
        },
        "input": {
            "aspect_ratio": (2.0, 10.0),  # Very horizontal
            "size_range": (1000, 30000)
        },
        "modal": {
            "aspect_ratio": (0.7, 1.5),  # Square-ish
            "size_range": (30000, 500000),  # Large
            "position_center": True
        }
    }
    
    @staticmethod
    def identify_components(
        rectangles: List[Dict[str, Any]],
        image_dimensions: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Identify UI components from rectangles
        
        Args:
            rectangles: Detected rectangles
            image_dimensions: Image width and height
            
        Returns:
            List of identified components
        """
        components = []
        img_width = image_dimensions["width"]
        img_height = image_dimensions["height"]
        
        for rect in rectangles:
            component = ComponentIdentifier._identify_single_component(
                rect, img_width, img_height
            )
            if component:
                components.append(component)
        
        # Post-processing: resolve conflicts and improve accuracy
        components = ComponentIdentifier._resolve_conflicts(components)
        
        return components
    
    @staticmethod
    def _identify_single_component(
        rect: Dict[str, Any],
        img_width: int,
        img_height: int
    ) -> Optional[Dict[str, Any]]:
        """Identify a single component"""
        x, y, w, h = rect["x"], rect["y"], rect["width"], rect["height"]
        area = rect["area"]
        aspect_ratio = rect["aspect_ratio"]
        
        # Calculate normalized positions
        x_ratio = x / img_width
        y_ratio = y / img_height
        w_ratio = w / img_width
        h_ratio = h / img_height
        
        # Score each component type
        scores = {}
        
        # Check navbar
        if (ComponentIdentifier._in_range(h_ratio, *ComponentIdentifier.COMPONENT_RULES["navbar"]["height_ratio"]) and
            ComponentIdentifier._in_range(y_ratio, *ComponentIdentifier.COMPONENT_RULES["navbar"]["position_y"]) and
            ComponentIdentifier._in_range(w_ratio, *ComponentIdentifier.COMPONENT_RULES["navbar"]["width_ratio"])):
            scores["navbar"] = 0.9
        
        # Check footer
        if (ComponentIdentifier._in_range(h_ratio, *ComponentIdentifier.COMPONENT_RULES["footer"]["height_ratio"]) and
            ComponentIdentifier._in_range(y_ratio, *ComponentIdentifier.COMPONENT_RULES["footer"]["position_y"]) and
            ComponentIdentifier._in_range(w_ratio, *ComponentIdentifier.COMPONENT_RULES["footer"]["width_ratio"])):
            scores["footer"] = 0.85
        
        # Check sidebar
        sidebar_rules = ComponentIdentifier.COMPONENT_RULES["sidebar"]
        if (ComponentIdentifier._in_range(w_ratio, *sidebar_rules["width_ratio"]) and
            ComponentIdentifier._in_range(h_ratio, *sidebar_rules["height_ratio"])):
            # Check if on left or right edge
            for pos_range in sidebar_rules["position_x"]:
                if ComponentIdentifier._in_range(x_ratio, *pos_range):
                    scores["sidebar"] = 0.8
                    break
        
        # Check card
        if (ComponentIdentifier._in_range(aspect_ratio, *ComponentIdentifier.COMPONENT_RULES["card"]["aspect_ratio"]) and
            ComponentIdentifier._in_range(area, *ComponentIdentifier.COMPONENT_RULES["card"]["size_range"])):
            scores["card"] = 0.7
        
        # Check button
        if (ComponentIdentifier._in_range(aspect_ratio, *ComponentIdentifier.COMPONENT_RULES["button"]["aspect_ratio"]) and
            ComponentIdentifier._in_range(area, *ComponentIdentifier.COMPONENT_RULES["button"]["size_range"])):
            scores["button"] = 0.75
        
        # Check input
        if (ComponentIdentifier._in_range(aspect_ratio, *ComponentIdentifier.COMPONENT_RULES["input"]["aspect_ratio"]) and
            ComponentIdentifier._in_range(area, *ComponentIdentifier.COMPONENT_RULES["input"]["size_range"])):
            scores["input"] = 0.7
        
        # Check modal
        modal_rules = ComponentIdentifier.COMPONENT_RULES["modal"]
        if (ComponentIdentifier._in_range(aspect_ratio, *modal_rules["aspect_ratio"]) and
            ComponentIdentifier._in_range(area, *modal_rules["size_range"])):
            # Check if centered
            center_x = x + w / 2
            center_y = y + h / 2
            if (abs(center_x - img_width/2) < img_width * 0.2 and
                abs(center_y - img_height/2) < img_height * 0.2):
                scores["modal"] = 0.85
        
        # If no strong match, classify as container or generic
        if not scores:
            if area > 50000:
                scores["container"] = 0.5
            else:
                scores["unknown"] = 0.3
        
        # Get best match
        component_type = max(scores.items(), key=lambda x: x[1])
        
        return {
            "type": component_type[0],
            "confidence": component_type[1],
            "position": {"x": x, "y": y, "width": w, "height": h},
            "properties": {
                "area": area,
                "aspect_ratio": aspect_ratio
            }
        }
    
    @staticmethod
    def _in_range(value: float, min_val: float, max_val: float) -> bool:
        """Check if value is in range"""
        return min_val <= value <= max_val
    
    @staticmethod
    def _resolve_conflicts(components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Resolve conflicting component identifications
        
        Args:
            components: List of identified components
            
        Returns:
            Resolved component list
        """
        # Remove duplicates (same position, different types)
        unique_components = []
        seen_positions = set()
        
        # Sort by confidence
        sorted_components = sorted(components, key=lambda c: c["confidence"], reverse=True)
        
        for comp in sorted_components:
            pos_key = (
                comp["position"]["x"],
                comp["position"]["y"],
                comp["position"]["width"],
                comp["position"]["height"]
            )
            
            if pos_key not in seen_positions:
                unique_components.append(comp)
                seen_positions.add(pos_key)
        
        return unique_components
    
    @staticmethod
    def group_components(components: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group components by type
        
        Args:
            components: List of components
            
        Returns:
            Dictionary with components grouped by type
        """
        grouped = {}
        
        for comp in components:
            comp_type = comp["type"]
            if comp_type not in grouped:
                grouped[comp_type] = []
            grouped[comp_type].append(comp)
        
        return grouped
    
    @staticmethod
    def get_component_hierarchy(components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build a hierarchical structure of components
        
        Args:
            components: List of components
            
        Returns:
            Hierarchical structure
        """
        # Define hierarchy levels
        hierarchy_levels = {
            "navbar": 1,
            "footer": 1,
            "sidebar": 2,
            "container": 2,
            "card": 3,
            "modal": 3,
            "input": 4,
            "button": 4,
            "text": 4,
            "icon": 5,
            "unknown": 6
        }
        
        # Sort by hierarchy level
        sorted_comps = sorted(
            components,
            key=lambda c: hierarchy_levels.get(c["type"], 999)
        )
        
        # Build tree structure
        tree = {
            "root": [],
            "children": {}
        }
        
        for comp in sorted_comps:
            comp_type = comp["type"]
            level = hierarchy_levels.get(comp_type, 999)
            
            if level == 1:
                tree["root"].append(comp)
            else:
                # Find parent (component that contains this one)
                parent = ComponentIdentifier._find_parent(comp, sorted_comps[:sorted_comps.index(comp)])
                
                if parent:
                    parent_id = id(parent)
                    if parent_id not in tree["children"]:
                        tree["children"][parent_id] = []
                    tree["children"][parent_id].append(comp)
                else:
                    tree["root"].append(comp)
        
        return tree
    
    @staticmethod
    def _find_parent(
        component: Dict[str, Any],
        potential_parents: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Find parent component that contains this component"""
        comp_pos = component["position"]
        
        for parent in reversed(potential_parents):  # Check from most recent
            parent_pos = parent["position"]
            
            # Check if component is inside parent
            if (comp_pos["x"] >= parent_pos["x"] and
                comp_pos["y"] >= parent_pos["y"] and
                comp_pos["x"] + comp_pos["width"] <= parent_pos["x"] + parent_pos["width"] and
                comp_pos["y"] + comp_pos["height"] <= parent_pos["y"] + parent_pos["height"]):
                return parent
        
        return None
    
    @staticmethod
    def estimate_component_count(components: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get count of each component type"""
        counts = {}
        for comp in components:
            comp_type = comp["type"]
            counts[comp_type] = counts.get(comp_type, 0) + 1
        return counts