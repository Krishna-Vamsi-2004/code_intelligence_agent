
import base64
import zlib
import requests
from typing import Optional, Dict
import logging

class KrokiService:
    def __init__(self, kroki_url: str = "https://kroki.io"):
        self.kroki_url = kroki_url.rstrip('/')
        self.logger = logging.getLogger(__name__)

    def get_svg_url(self, mermaid_code: str, diagram_type: str = "mermaid") -> str:
        """
        Compresses Mermaid code and returns a Kroki SVG URL.
        """
        try:
            compressed = zlib.compress(mermaid_code.encode('utf-8'))
            encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
            return f"{self.kroki_url}/{diagram_type}/svg/{encoded}"
        except Exception as e:
            self.logger.error(f"Error generating Kroki URL: {e}")
            return ""

    def get_svg_content(self, mermaid_code: str, diagram_type: str = "mermaid") -> Optional[bytes]:
        """
        Fetches SVG content from Kroki using POST method for better reliability.
        """
        try:
            if not mermaid_code or not mermaid_code.strip():
                self.logger.warning("Empty Mermaid code provided")
                return None
            
            # Clean the mermaid code
            cleaned_code = self._clean_mermaid_code(mermaid_code)
            
            # Use POST method with direct endpoint for better reliability
            url = f"{self.kroki_url}/{diagram_type}/svg"
            
            # Send as plain text in request body
            headers = {
                'Content-Type': 'text/plain',
                'Accept': 'image/svg+xml'
            }
            
            self.logger.info(f"Sending request to Kroki: {url}")
            response = requests.post(
                url, 
                data=cleaned_code.encode('utf-8'),
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                # Validate SVG content
                if b"<svg" in response.content and len(response.content) > 100:
                    self.logger.info(f"Successfully generated SVG ({len(response.content)} bytes)")
                    return response.content
                else:
                    self.logger.error("Invalid SVG content received")
                    return None
            else:
                self.logger.error(f"Kroki error: Status {response.status_code}, Response: {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error("Kroki request timeout")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Kroki request exception: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Kroki exception: {e}")
            return None
    
    def _clean_mermaid_code(self, mermaid_code: str) -> str:
        """Clean and validate Mermaid code before sending to Kroki"""
        # Remove any markdown code blocks
        code = mermaid_code.strip()
        
        if code.startswith("```mermaid"):
            code = code[10:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        code = code.strip()
        
        # Ensure it starts with a diagram type
        if not any(code.startswith(t) for t in ['flowchart', 'graph', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'gantt', 'pie']):
            # If no diagram type, assume flowchart
            if not code.startswith('flowchart') and not code.startswith('graph'):
                code = f"flowchart TD\n{code}"
        
        return code
    
    def validate_mermaid_syntax(self, mermaid_code: str) -> bool:
        """
        Validate Mermaid syntax by attempting to render it
        """
        svg_content = self.get_svg_content(mermaid_code)
        return svg_content is not None

class MermaidService:
    @staticmethod
    def generate_flowchart(logic_description: str) -> str:
        """
        This will be called by LLM to generate Mermaid flowchart syntax.
        """
        # Placeholder for prompt construction logic
        pass

    @staticmethod
    def simplify_diagram(mermaid_code: str) -> str:
        """
        Simplifies a Mermaid diagram if rendering fails multiple times.
        Example: reducing number of nodes or flow complexity.
        This would be handled by a corrective prompt for the LLM.
        """
        return f"Simplify this Mermaid diagram:\n{mermaid_code}"
