"""
Color extraction and analysis tools
"""
from PIL import Image
import numpy as np
from typing import List, Tuple, Dict, Optional
from collections import Counter
import colorsys
import webcolors


class ColorExtractor:
    """Extract and analyze colors from images"""
    
    @staticmethod
    def extract_dominant_colors(
        image: Image.Image,
        num_colors: int = 5,
        quality: int = 10
    ) -> List[Tuple[int, int, int]]:
        """
        Extract dominant colors using k-means clustering
        
        Args:
            image: PIL Image object
            num_colors: Number of dominant colors to extract
            quality: Sample quality (lower = faster but less accurate)
            
        Returns:
            List of RGB tuples
        """
        # Resize image for faster processing
        img = image.copy()
        img.thumbnail((200, 200))
        
        # Convert to numpy array
        pixels = np.array(img)
        
        # Reshape to list of pixels
        pixels = pixels.reshape(-1, 3)
        
        # Sample pixels for performance
        if quality > 1:
            pixels = pixels[::quality]
        
        # Use k-means clustering
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(pixels)
        
        colors = kmeans.cluster_centers_
        
        # Convert to integers
        colors = colors.astype(int)
        
        return [tuple(color) for color in colors]
    
    @staticmethod
    def extract_palette(image: Image.Image) -> Dict[str, str]:
        """
        Extract a comprehensive color palette
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with color roles (primary, secondary, etc.)
        """
        # Get dominant colors
        colors = ColorExtractor.extract_dominant_colors(image, num_colors=8)
        
        # Sort by brightness
        colors_with_brightness = [
            (color, ColorExtractor.get_brightness(color))
            for color in colors
        ]
        colors_with_brightness.sort(key=lambda x: x[1], reverse=True)
        
        # Assign roles
        palette = {}
        
        # Background (lightest or darkest)
        if colors_with_brightness[0][1] > 200:
            palette["background"] = ColorExtractor.rgb_to_hex(colors_with_brightness[0][0])
            palette["text"] = ColorExtractor.rgb_to_hex(colors_with_brightness[-1][0])
        else:
            palette["background"] = ColorExtractor.rgb_to_hex(colors_with_brightness[-1][0])
            palette["text"] = ColorExtractor.rgb_to_hex(colors_with_brightness[0][0])
        
        # Find most saturated color for primary
        colors_with_saturation = [
            (color, ColorExtractor.get_saturation(color))
            for color in colors
        ]
        colors_with_saturation.sort(key=lambda x: x[1], reverse=True)
        
        palette["primary"] = ColorExtractor.rgb_to_hex(colors_with_saturation[0][0])
        
        # Secondary and accent
        if len(colors_with_saturation) > 1:
            palette["secondary"] = ColorExtractor.rgb_to_hex(colors_with_saturation[1][0])
        if len(colors_with_saturation) > 2:
            palette["accent"] = ColorExtractor.rgb_to_hex(colors_with_saturation[2][0])
        
        # All colors
        palette["all_colors"] = [ColorExtractor.rgb_to_hex(c) for c in colors]
        
        return palette
    
    @staticmethod
    def get_brightness(rgb: Tuple[int, int, int]) -> float:
        """Calculate perceived brightness of RGB color"""
        r, g, b = rgb
        # Use perceived brightness formula
        return (0.299 * r + 0.587 * g + 0.114 * b)
    
    @staticmethod
    def get_saturation(rgb: Tuple[int, int, int]) -> float:
        """Calculate saturation of RGB color"""
        r, g, b = [x / 255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return s
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color code"""
        return "#{:02x}{:02x}{:02x}".format(*rgb)
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def calculate_contrast_ratio(color1: str, color2: str) -> float:
        """
        Calculate WCAG contrast ratio between two colors
        
        Args:
            color1: Hex color code
            color2: Hex color code
            
        Returns:
            Contrast ratio (1-21)
        """
        rgb1 = ColorExtractor.hex_to_rgb(color1)
        rgb2 = ColorExtractor.hex_to_rgb(color2)
        
        l1 = ColorExtractor.get_relative_luminance(rgb1)
        l2 = ColorExtractor.get_relative_luminance(rgb2)
        
        lighter = max(l1, l2)
        darker = min(l1, l2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def get_relative_luminance(rgb: Tuple[int, int, int]) -> float:
        """Calculate relative luminance for WCAG contrast"""
        def adjust(color_value):
            color_value = color_value / 255.0
            if color_value <= 0.03928:
                return color_value / 12.92
            else:
                return ((color_value + 0.055) / 1.055) ** 2.4
        
        r, g, b = rgb
        r = adjust(r)
        g = adjust(g)
        b = adjust(b)
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    @staticmethod
    def get_color_name(hex_color: str) -> str:
        """
        Get closest CSS3 color name
        
        Args:
            hex_color: Hex color code
            
        Returns:
            Color name
        """
        try:
            rgb = ColorExtractor.hex_to_rgb(hex_color)
            return webcolors.rgb_to_name(rgb, spec='css3')
        except ValueError:
            # Find closest color
            rgb = ColorExtractor.hex_to_rgb(hex_color)
            min_distance = float('inf')
            closest_name = None
            
            for name in webcolors.CSS3_NAMES_TO_HEX:
                css_rgb = webcolors.hex_to_rgb(webcolors.CSS3_NAMES_TO_HEX[name])
                distance = sum((a - b) ** 2 for a, b in zip(rgb, css_rgb))
                if distance < min_distance:
                    min_distance = distance
                    closest_name = name
            
            return closest_name
    
    @staticmethod
    def is_dark_color(hex_color: str) -> bool:
        """Check if color is dark"""
        rgb = ColorExtractor.hex_to_rgb(hex_color)
        brightness = ColorExtractor.get_brightness(rgb)
        return brightness < 128
    
    @staticmethod
    def generate_complementary(hex_color: str) -> str:
        """Generate complementary color"""
        rgb = ColorExtractor.hex_to_rgb(hex_color)
        r, g, b = [x / 255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        # Rotate hue by 180 degrees
        h = (h + 0.5) % 1.0
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        rgb = tuple(int(x * 255) for x in (r, g, b))
        
        return ColorExtractor.rgb_to_hex(rgb)
    
    @staticmethod
    def analyze_color_harmony(colors: List[str]) -> Dict[str, any]:
        """
        Analyze color harmony in palette
        
        Args:
            colors: List of hex colors
            
        Returns:
            Harmony analysis
        """
        if len(colors) < 2:
            return {"harmony_type": "single", "score": 1.0}
        
        # Convert to HSV
        hsv_colors = []
        for color in colors:
            rgb = ColorExtractor.hex_to_rgb(color)
            r, g, b = [x / 255.0 for x in rgb]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            hsv_colors.append((h, s, v))
        
        # Analyze hue differences
        hues = [h for h, s, v in hsv_colors]
        hue_diffs = []
        for i in range(len(hues)):
            for j in range(i + 1, len(hues)):
                diff = abs(hues[i] - hues[j])
                hue_diffs.append(min(diff, 1.0 - diff))  # Circular difference
        
        avg_diff = np.mean(hue_diffs) if hue_diffs else 0
        
        # Determine harmony type
        if avg_diff < 0.1:
            harmony_type = "monochromatic"
        elif avg_diff < 0.2:
            harmony_type = "analogous"
        elif 0.4 < avg_diff < 0.6:
            harmony_type = "complementary"
        elif 0.25 < avg_diff < 0.4:
            harmony_type = "triadic"
        else:
            harmony_type = "mixed"
        
        return {
            "harmony_type": harmony_type,
            "avg_hue_difference": round(avg_diff, 2),
            "color_count": len(colors)
        }