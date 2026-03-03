from typing import List, Dict
import re


class PatternMatcher:
    """
    Utility class for matching UI patterns in requirements and code.
    """
    
    # Define common UI patterns
    UI_PATTERNS = {
        "form": {
            "keywords": ["form", "input", "submit", "validation", "field"],
            "description": "Form handling with validation"
        },
        "list": {
            "keywords": ["list", "items", "array", "collection", "map"],
            "description": "List rendering and management"
        },
        "modal": {
            "keywords": ["modal", "dialog", "popup", "overlay"],
            "description": "Modal/Dialog component"
        },
        "navigation": {
            "keywords": ["nav", "menu", "router", "link", "navigation"],
            "description": "Navigation and routing"
        },
        "authentication": {
            "keywords": ["login", "auth", "signup", "signin", "authentication"],
            "description": "Authentication flow"
        },
        "data_fetching": {
            "keywords": ["api", "fetch", "axios", "data", "loading"],
            "description": "Data fetching and loading states"
        },
        "search": {
            "keywords": ["search", "filter", "query"],
            "description": "Search and filtering"
        },
        "pagination": {
            "keywords": ["pagination", "page", "next", "previous"],
            "description": "Pagination component"
        },
        "table": {
            "keywords": ["table", "grid", "rows", "columns"],
            "description": "Data table/grid"
        },
        "card": {
            "keywords": ["card", "panel", "box"],
            "description": "Card component"
        },
        "tabs": {
            "keywords": ["tab", "tabs", "panels"],
            "description": "Tabbed interface"
        },
        "dropdown": {
            "keywords": ["dropdown", "select", "options"],
            "description": "Dropdown/Select component"
        },
        "toast": {
            "keywords": ["toast", "notification", "alert", "message"],
            "description": "Toast/Notification system"
        }
    }
    
    DESIGN_PATTERNS = {
        "container_presentational": {
            "indicators": ["container", "presentation", "smart", "dumb"],
            "description": "Container/Presentational pattern"
        },
        "compound_component": {
            "indicators": ["compound", "composite", "children"],
            "description": "Compound component pattern"
        },
        "render_props": {
            "indicators": ["render prop", "function as child"],
            "description": "Render props pattern"
        },
        "hoc": {
            "indicators": ["higher order", "HOC", "withAuth"],
            "description": "Higher-Order Component pattern"
        },
        "custom_hooks": {
            "indicators": ["custom hook", "use"],
            "description": "Custom hooks pattern"
        }
    }
    
    @staticmethod
    def match_ui_patterns(text: str) -> List[Dict[str, str]]:
        """Match UI patterns in user input"""
        text_lower = text.lower()
        matched_patterns = []
        
        for pattern_name, pattern_info in PatternMatcher.UI_PATTERNS.items():
            # Check if any keyword is in the text
            if any(keyword in text_lower for keyword in pattern_info["keywords"]):
                matched_patterns.append({
                    "name": pattern_name,
                    "description": pattern_info["description"]
                })
        
        return matched_patterns
    
    @staticmethod
    def match_design_patterns(text: str) -> List[Dict[str, str]]:
        """Match design patterns in user input"""
        text_lower = text.lower()
        matched_patterns = []
        
        for pattern_name, pattern_info in PatternMatcher.DESIGN_PATTERNS.items():
            if any(indicator in text_lower for indicator in pattern_info["indicators"]):
                matched_patterns.append({
                    "name": pattern_name,
                    "description": pattern_info["description"]
                })
        
        return matched_patterns
    
    @staticmethod
    def detect_complexity(text: str) -> str:
        """Detect complexity level from user input"""
        text_lower = text.lower()
        
        # Simple indicators
        simple_indicators = ["simple", "basic", "minimal"]
        # Complex indicators
        complex_indicators = ["complex", "advanced", "sophisticated", "enterprise"]
        # Medium indicators
        medium_indicators = ["standard", "typical", "normal"]
        
        if any(indicator in text_lower for indicator in complex_indicators):
            return "high"
        elif any(indicator in text_lower for indicator in simple_indicators):
            return "low"
        elif any(indicator in text_lower for indicator in medium_indicators):
            return "medium"
        
        # Default based on feature count
        feature_count = sum([
            len(PatternMatcher.match_ui_patterns(text)),
            text_lower.count("and"),
            text_lower.count("also"),
            text_lower.count("with")
        ])
        
        if feature_count > 5:
            return "high"
        elif feature_count > 2:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def extract_features(text: str) -> List[str]:
        """Extract feature requirements from text"""
        features = []
        
        # Common feature keywords
        feature_keywords = [
            "responsive", "mobile", "desktop", "tablet",
            "dark mode", "light mode", "theme",
            "animation", "transition",
            "real-time", "live",
            "drag and drop", "drag-drop",
            "search", "filter", "sort",
            "export", "import",
            "print", "download",
            "share", "social",
            "accessibility", "a11y",
            "i18n", "internationalization",
            "offline", "PWA"
        ]
        
        text_lower = text.lower()
        for keyword in feature_keywords:
            if keyword in text_lower:
                features.append(keyword.title())
        
        return list(set(features))
    
    @staticmethod
    def suggest_components(patterns: List[Dict[str, str]]) -> List[str]:
        """Suggest component names based on detected patterns"""
        component_suggestions = {
            "form": ["Form", "FormField", "ValidationMessage"],
            "list": ["List", "ListItem"],
            "modal": ["Modal", "ModalHeader", "ModalBody", "ModalFooter"],
            "navigation": ["Navbar", "NavItem", "Sidebar"],
            "authentication": ["LoginForm", "SignupForm", "AuthProvider"],
            "data_fetching": ["DataFetcher", "LoadingSpinner", "ErrorBoundary"],
            "search": ["SearchBar", "SearchResults", "SearchFilters"],
            "pagination": ["Pagination", "PageButton"],
            "table": ["Table", "TableRow", "TableCell", "TableHeader"],
            "card": ["Card", "CardHeader", "CardBody"],
            "tabs": ["Tabs", "TabList", "TabPanel"],
            "dropdown": ["Dropdown", "DropdownItem"],
            "toast": ["Toast", "ToastContainer"]
        }
        
        components = []
        for pattern in patterns:
            pattern_name = pattern["name"]
            if pattern_name in component_suggestions:
                components.extend(component_suggestions[pattern_name])
        
        return list(set(components))