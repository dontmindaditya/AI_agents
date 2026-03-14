"""
Code generation utilities

This module provides utilities for generating code configuration files
and scaffolding for various frontend frameworks.

Supported generators:
- package.json: Node.js project dependencies and scripts
- tsconfig.json: TypeScript compiler configuration
- tailwind.config.js: Tailwind CSS configuration

Usage:
    from services.code_generator import CodeGenerator
    
    # Generate package.json
    package_json = CodeGenerator.generate_package_json("react", {"axios": "^1.0.0"})
    
    # Generate tsconfig.json
    tsconfig = CodeGenerator.generate_tsconfig("nextjs")
    
    # Generate tailwind config
    tailwind = CodeGenerator.generate_tailwind_config()
"""

from typing import Dict, Any, List, Optional
from utils.parser import clean_code_block
from utils.logger import get_logger

logger = get_logger(__name__)


class CodeGenerator:
    """
    Utilities for generating code configuration files.
    
    This class provides static methods to generate various configuration
    files needed for frontend projects including package.json, tsconfig.json,
    and Tailwind CSS configuration.
    
    Example:
        >>> package = CodeGenerator.generate_package_json("react")
        >>> print(package)
        {
          "name": "webby-generated-project",
          "version": "0.1.0",
          ...
        }
    """
    
    @staticmethod
    def generate_package_json(framework: str, dependencies: Optional[Dict[str, str]] = None) -> str:
        """
        Generate a package.json file for the specified framework.
        
        Args:
            framework: Target framework (react, nextjs, vue, etc.)
            dependencies: Optional additional dependencies to include
            
        Returns:
            JSON string representing the package.json file
        """
        import json
        
        base_deps = {
            "nextjs": {
                "next": "^14.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "react": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0"
            }
        }.get(framework, {})
        
        dev_deps = {
            "typescript": "^5.0.0",
            "@types/react": "^18.2.0",
            "@types/node": "^20.0.0",
            "tailwindcss": "^3.4.0",
            "autoprefixer": "^10.4.0",
            "postcss": "^8.4.0",
            "eslint": "^8.0.0"
        }
        
        if dependencies:
            base_deps.update(dependencies)
        
        package = {
            "name": "webby-generated-project",
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev" if framework == "nextjs" else "vite",
                "build": "next build" if framework == "nextjs" else "vite build",
                "start": "next start" if framework == "nextjs" else "vite preview",
                "lint": "eslint ."
            },
            "dependencies": base_deps,
            "devDependencies": dev_deps
        }
        
        return json.dumps(package, indent=2)
    
    @staticmethod
    def generate_tsconfig(framework: str) -> str:
        """Generate tsconfig.json"""
        import json
        
        if framework == "nextjs":
            config = {
                "compilerOptions": {
                    "target": "ES2020",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [{"name": "next"}],
                    "paths": {"@/*": ["./src/*"]}
                },
                "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
                "exclude": ["node_modules"]
            }
        else:
            config = {
                "compilerOptions": {
                    "target": "ES2020",
                    "lib": ["ES2020", "DOM", "DOM.Iterable"],
                    "module": "ESNext",
                    "skipLibCheck": True,
                    "strict": True,
                    "jsx": "react-jsx"
                },
                "include": ["src"]
            }
        
        return json.dumps(config, indent=2)
    
    @staticmethod
    def generate_tailwind_config() -> str:
        """Generate tailwind.config.js"""
        return """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
        },
      },
    },
  },
  plugins: [],
}"""
    
    @staticmethod
    def clean_generated_code(code: str) -> str:
        """Clean generated code"""
        return clean_code_block(code)