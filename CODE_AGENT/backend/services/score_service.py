
import ast
from typing import Dict, Any, Optional

class ScoreService:
    @staticmethod
    def calculate_optimality_score(code: str) -> Dict[str, Any]:
        """
        Calculate an optimality score based on AST metrics.
        - Number of nodes
        - Cyclomatic complexity (as a simple proxy)
        - Use of specific modern idioms
        """
        try:
            if not code or not code.strip():
                return {
                    "score": 0,
                    "error": "Empty code provided"
                }
                
            tree = ast.parse(code)
            
            # Simple scoring criteria
            node_count = 0
            complexity_score = 0
            for node in ast.walk(tree):
                node_count += 1
                if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try, ast.AsyncWith, ast.AsyncFor)):
                    complexity_score += 1

            # Metric: Density Score (lower is often better, or more concise)
            lines = len([line for line in code.splitlines() if line.strip()])
            density = node_count / lines if lines > 0 else 0
            
            # Optimality Score (0-100)
            # Higher is better: conciseness + lower complexity
            base_score = 100
            base_score -= complexity_score * 5
            base_score = max(0, min(100, base_score))

            return {
                "score": base_score,
                "metrics": {
                    "node_count": node_count,
                    "complexity": complexity_score,
                    "density": f"{density:.2f}",
                    "lines": lines
                }
            }
        except SyntaxError as e:
            return {
                "score": 0,
                "error": f"AST parsing failed: {str(e)}"
            }
        except Exception as e:
            return {
                "score": 0,
                "error": f"Score calculation failed: {str(e)}"
            }

    @staticmethod
    def get_syntax_fix_prompt(code: str, error: str) -> str:
        """
        Generates a prompt to fix Python syntax only.
        """
        return f"""
        The following Python code has a syntax error:
        {code}
        
        Error: {error}
        
        Fix the syntax error and return the complete code.
        Do not include an explanation or any other text.
        """
