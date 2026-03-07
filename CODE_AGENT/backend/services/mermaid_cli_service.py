import subprocess
import tempfile
import os
import base64
import logging
from pathlib import Path
from typing import Optional, Tuple, Literal

class MermaidCLIService:
    """
    Service for rendering Mermaid diagrams using the locally installed Mermaid CLI (mmdc).
    This provides faster and more reliable rendering compared to external services.
    """
    
    def __init__(self, mmdc_path: str = "mmdc"):
        """
        Initialize the Mermaid CLI service.
        
        Args:
            mmdc_path: Path to the mmdc executable (default: "mmdc" assumes it's in PATH)
        """
        # On Windows, prefer .cmd version
        import platform
        if platform.system() == "Windows" and mmdc_path == "mmdc":
            self.mmdc_path = "mmdc.cmd"
        else:
            self.mmdc_path = mmdc_path
        
        self.logger = logging.getLogger(__name__)
        self._verify_installation()
    
    def _verify_installation(self) -> bool:
        """Verify that Mermaid CLI is installed and accessible"""
        try:
            import platform
            use_shell = platform.system() == "Windows"
            
            result = subprocess.run(
                [self.mmdc_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=use_shell
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"Mermaid CLI found: version {version}")
                return True
            else:
                self.logger.error("Mermaid CLI not found or not working")
                return False
        except Exception as e:
            self.logger.error(f"Failed to verify Mermaid CLI installation: {e}")
            return False
    
    def render_diagram(
        self,
        mermaid_code: str,
        output_format: Literal["svg", "png", "pdf"] = "svg",
        background_color: str = "white",
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Optional[bytes]:
        """
        Render a Mermaid diagram to the specified format.
        
        Args:
            mermaid_code: The Mermaid diagram code
            output_format: Output format (svg, png, or pdf)
            background_color: Background color (default: white, use "transparent" for transparency)
            width: Optional width in pixels
            height: Optional height in pixels
            
        Returns:
            Rendered diagram as bytes, or None if rendering failed
        """
        try:
            # Clean the mermaid code
            cleaned_code = self._clean_mermaid_code(mermaid_code)
            
            if not cleaned_code:
                self.logger.error("Empty or invalid Mermaid code")
                return None
            
            # Create temporary files
            with tempfile.TemporaryDirectory() as temp_dir:
                input_file = Path(temp_dir) / "diagram.mmd"
                output_file = Path(temp_dir) / f"diagram.{output_format}"
                
                # Write Mermaid code to input file
                input_file.write_text(cleaned_code, encoding='utf-8')
                
                # Build mmdc command
                cmd = [
                    self.mmdc_path,
                    "-i", str(input_file),
                    "-o", str(output_file),
                    "-b", background_color
                ]
                
                # Add optional dimensions
                if width:
                    cmd.extend(["-w", str(width)])
                if height:
                    cmd.extend(["-H", str(height)])
                
                self.logger.info(f"Executing: {' '.join(cmd)}")
                
                # Execute mmdc command (use shell=True on Windows for .cmd files)
                import platform
                use_shell = platform.system() == "Windows"
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=use_shell
                )
                
                if result.returncode != 0:
                    self.logger.error(f"mmdc failed: {result.stderr}")
                    return None
                
                # Read the output file
                if output_file.exists():
                    content = output_file.read_bytes()
                    self.logger.info(f"Successfully rendered {output_format} ({len(content)} bytes)")
                    return content
                else:
                    self.logger.error("Output file was not created")
                    return None
                    
        except subprocess.TimeoutExpired:
            self.logger.error("Mermaid CLI rendering timeout")
            return None
        except Exception as e:
            self.logger.error(f"Error rendering diagram: {e}")
            return None
    
    def render_to_svg(self, mermaid_code: str, background_color: str = "white") -> Optional[str]:
        """
        Render Mermaid diagram to SVG string.
        
        Args:
            mermaid_code: The Mermaid diagram code
            background_color: Background color
            
        Returns:
            SVG content as string, or None if rendering failed
        """
        svg_bytes = self.render_diagram(mermaid_code, "svg", background_color)
        if svg_bytes:
            return svg_bytes.decode('utf-8')
        return None
    
    def render_to_base64(
        self,
        mermaid_code: str,
        output_format: Literal["svg", "png", "pdf"] = "png"
    ) -> Optional[str]:
        """
        Render Mermaid diagram and return as base64 encoded string.
        
        Args:
            mermaid_code: The Mermaid diagram code
            output_format: Output format
            
        Returns:
            Base64 encoded diagram, or None if rendering failed
        """
        diagram_bytes = self.render_diagram(mermaid_code, output_format)
        if diagram_bytes:
            return base64.b64encode(diagram_bytes).decode('utf-8')
        return None
    
    def validate_syntax(self, mermaid_code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Mermaid syntax by attempting to render it.
        
        Args:
            mermaid_code: The Mermaid diagram code
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            result = self.render_diagram(mermaid_code, "svg")
            if result and len(result) > 100:
                return True, None
            else:
                return False, "Rendering produced invalid or empty output"
        except Exception as e:
            return False, str(e)
    
    def _clean_mermaid_code(self, mermaid_code: str) -> str:
        """Clean and validate Mermaid code before rendering"""
        # Remove any markdown code blocks
        code = mermaid_code.strip()
        
        # Check if empty
        if not code:
            return ""
        
        if code.startswith("```mermaid"):
            code = code[10:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        
        code = code.strip()
        
        # Check again after cleaning
        if not code:
            return ""
        
        # Ensure it starts with a diagram type
        valid_diagram_types = [
            'flowchart', 'graph', 'sequenceDiagram', 'classDiagram',
            'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey',
            'gitGraph', 'mindmap', 'timeline', 'quadrantChart'
        ]
        
        if not any(code.startswith(t) for t in valid_diagram_types):
            # If no diagram type, assume flowchart
            if not code.startswith('flowchart') and not code.startswith('graph'):
                code = f"flowchart TD\n{code}"
        
        return code
    
    def get_supported_formats(self) -> list:
        """Get list of supported output formats"""
        return ["svg", "png", "pdf"]
