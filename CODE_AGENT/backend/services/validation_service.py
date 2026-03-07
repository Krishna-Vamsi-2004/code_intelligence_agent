
import re
import json
import ast
from typing import Any, Dict, Optional

class ValidationService:
    @staticmethod
    def validate_json(content: str) -> bool:
        try:
            json.loads(content)
            return True
        except (ValueError, json.JSONDecodeError):
            return False

    @staticmethod
    def validate_mermaid(content: str) -> bool:
        """
        Validates Mermaid syntax with improved checking.
        """
        try:
            if not content or not content.strip():
                return False
            
            # Remove any leading/trailing whitespace and markdown blocks
            content = content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```mermaid"):
                content = content[10:].strip()
            elif content.startswith("```"):
                content = content[3:].strip()
            
            if content.endswith("```"):
                content = content[:-3].strip()
            
            # Check if it starts with valid Mermaid diagram types
            valid_starts = [
                "flowchart", "graph", "sequenceDiagram", "classDiagram",
                "stateDiagram", "erDiagram", "gantt", "pie", "journey",
                "gitGraph", "mindmap", "timeline"
            ]
            
            # Check if content starts with any valid diagram type
            for diagram_type in valid_starts:
                if content.startswith(diagram_type):
                    # Additional check: ensure it has some content after the diagram type
                    if len(content) > len(diagram_type) + 5:
                        return True
            
            return False
            
        except (AttributeError, TypeError):
            return False

    @staticmethod
    def validate_python_ast(code: str) -> bool:
        """
        Validates Python syntax using AST parsing.
        """
        try:
            if not code or not code.strip():
                return False
            
            # Check if it's an error message
            if code.strip().startswith("# Error:"):
                return False
            
            # Check if it contains error keywords
            error_keywords = ["Error:", "Exception:", "Traceback:", "Failed:"]
            for keyword in error_keywords:
                if keyword in code[:100]:  # Check first 100 chars
                    return False
            
            ast.parse(code)
            return True
        except (SyntaxError, ValueError, TypeError):
            return False

    @staticmethod
    def validate_llm_structure(content: str, required_sections: list) -> bool:
        """
        Checks if the content includes required sections.
        """
        for section in required_sections:
            if section not in content:
                return False
        return True

    @staticmethod
    def validate_kroki_svg(response_body: bytes) -> bool:
        """
        Check if Kroki response is a valid SVG.
        """
        try:
            # Simple check for SVG tag
            return b"<svg" in response_body and b"</svg>" in response_body
        except Exception:
            return False
