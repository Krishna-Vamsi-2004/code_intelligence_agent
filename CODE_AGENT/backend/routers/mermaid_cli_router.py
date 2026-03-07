from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import Response
from models.schemas import SuccessResponse, FailureResponse
from utils.service_container import ServiceContainer, get_services
from typing import Literal, Optional

router = APIRouter()

@router.post("/render")
async def render_mermaid_diagram(
    mermaid_code: str = Body(..., embed=True),
    output_format: Literal["svg", "png", "pdf"] = Body("svg", embed=True),
    background_color: str = Body("white", embed=True),
    services: ServiceContainer = Depends(get_services)
):
    """
    Render a Mermaid diagram using the local Mermaid CLI.
    
    Args:
        mermaid_code: The Mermaid diagram code
        output_format: Output format (svg, png, or pdf)
        background_color: Background color (default: white, use "transparent" for transparency)
    
    Returns:
        Rendered diagram content with appropriate content type
    """
    try:
        # Render the diagram
        diagram_bytes = services.mermaid_cli.render_diagram(
            mermaid_code=mermaid_code,
            output_format=output_format,
            background_color=background_color
        )
        
        if diagram_bytes is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to render Mermaid diagram. Check syntax and try again."
            )
        
        # Set appropriate content type
        content_types = {
            "svg": "image/svg+xml",
            "png": "image/png",
            "pdf": "application/pdf"
        }
        
        return Response(
            content=diagram_bytes,
            media_type=content_types.get(output_format, "application/octet-stream")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering diagram: {str(e)}")


@router.post("/render-base64")
async def render_mermaid_base64(
    mermaid_code: str = Body(..., embed=True),
    output_format: Literal["svg", "png", "pdf"] = Body("svg", embed=True),
    services: ServiceContainer = Depends(get_services)
):
    """
    Render a Mermaid diagram and return as base64 encoded string.
    Useful for embedding in JSON responses or HTML.
    
    Args:
        mermaid_code: The Mermaid diagram code
        output_format: Output format (svg, png, or pdf)
    
    Returns:
        JSON response with base64 encoded diagram
    """
    try:
        base64_result = services.mermaid_cli.render_to_base64(
            mermaid_code=mermaid_code,
            output_format=output_format
        )
        
        if base64_result is None:
            return FailureResponse(
                stage="Mermaid Rendering",
                message="Failed to render diagram",
                retry_attempted=False,
                faulty_output=mermaid_code
            )
        
        return SuccessResponse(data={
            "base64": base64_result,
            "format": output_format,
            "data_uri": f"data:image/{output_format};base64,{base64_result}"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering diagram: {str(e)}")


@router.post("/validate")
async def validate_mermaid_syntax(
    mermaid_code: str = Body(..., embed=True),
    services: ServiceContainer = Depends(get_services)
):
    """
    Validate Mermaid diagram syntax by attempting to render it.
    
    Args:
        mermaid_code: The Mermaid diagram code to validate
    
    Returns:
        JSON response indicating if syntax is valid
    """
    try:
        is_valid, error_message = services.mermaid_cli.validate_syntax(mermaid_code)
        
        if is_valid:
            return SuccessResponse(data={
                "valid": True,
                "message": "Mermaid syntax is valid"
            })
        else:
            return SuccessResponse(data={
                "valid": False,
                "message": error_message or "Invalid Mermaid syntax"
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating syntax: {str(e)}")


@router.post("/generate-and-render")
async def generate_and_render_diagram(
    code_for_diagram: str = Body(..., embed=True),
    output_format: Literal["svg", "png", "pdf"] = Body("svg", embed=True),
    background_color: str = Body("white", embed=True),
    services: ServiceContainer = Depends(get_services)
):
    """
    Generate a Mermaid diagram from code and render it using local CLI.
    This combines LLM generation with local rendering for better performance.
    
    Args:
        code_for_diagram: The code to convert to a diagram
        output_format: Output format (svg, png, or pdf)
        background_color: Background color
    
    Returns:
        JSON response with Mermaid syntax and rendered diagram
    """
    # Generate Mermaid syntax using LLM
    mermaid_prompt = f"Convert this code to a Mermaid flowchart. Start with 'flowchart TD'. Code:\n{code_for_diagram}\n\nReturn only the Mermaid syntax."
    
    def validate_flowchart(mermaid_code: str) -> bool:
        """Validate using local Mermaid CLI"""
        if not services.validator.validate_mermaid(mermaid_code):
            return False
        
        # Validate by attempting to render
        is_valid, _ = services.mermaid_cli.validate_syntax(mermaid_code)
        return is_valid
    
    # Generate with retry engine
    result = services.retry_engine.execute_stage(
        stage_name="Mermaid Generation (CLI)",
        original_input=mermaid_prompt,
        generation_fn=lambda prompt, max_new_tokens: services.llm.generate(prompt, max_new_tokens),
        validation_fn=validate_flowchart,
        error_context_fn=lambda e: f"Mermaid syntax error: {str(e)}",
        max_tokens=300
    )
    
    if result["status"] == "success":
        mermaid_syntax = result["data"]
        
        # Render using local CLI
        diagram_bytes = services.mermaid_cli.render_diagram(
            mermaid_code=mermaid_syntax,
            output_format=output_format,
            background_color=background_color
        )
        
        if diagram_bytes:
            # Convert to base64 for JSON response
            import base64
            base64_diagram = base64.b64encode(diagram_bytes).decode('utf-8')
            
            return SuccessResponse(data={
                "mermaid_syntax": mermaid_syntax,
                "diagram_base64": base64_diagram,
                "format": output_format,
                "data_uri": f"data:image/{output_format};base64,{base64_diagram}",
                "retries": result["retries"]
            })
        else:
            return FailureResponse(
                stage="Mermaid Rendering",
                message="Generated valid syntax but rendering failed",
                retry_attempted=False,
                faulty_output=mermaid_syntax
            )
    else:
        # Try simplified version
        simplified_prompt = f"Create a simple Mermaid flowchart for this code. Use minimal nodes. Code:\n{code_for_diagram}"
        simplified_result = services.retry_engine.execute_stage(
            stage_name="Simplified Mermaid (CLI)",
            original_input=simplified_prompt,
            generation_fn=lambda prompt, max_new_tokens: services.llm.generate(prompt, max_new_tokens),
            validation_fn=validate_flowchart,
            error_context_fn=lambda e: f"Simplified Mermaid error: {str(e)}",
            max_tokens=200
        )
        
        if simplified_result["status"] == "success":
            mermaid_syntax = simplified_result["data"]
            diagram_bytes = services.mermaid_cli.render_diagram(
                mermaid_code=mermaid_syntax,
                output_format=output_format,
                background_color=background_color
            )
            
            if diagram_bytes:
                import base64
                base64_diagram = base64.b64encode(diagram_bytes).decode('utf-8')
                
                return SuccessResponse(data={
                    "mermaid_syntax": mermaid_syntax,
                    "diagram_base64": base64_diagram,
                    "format": output_format,
                    "data_uri": f"data:image/{output_format};base64,{base64_diagram}",
                    "simplified": True
                })
        
        return FailureResponse(
            stage="Mermaid Generation",
            message=f"Failed to generate valid Mermaid diagram: {result['message']}",
            retry_attempted=True,
            faulty_output=result.get("faulty_output", "")
        )


@router.get("/formats")
async def get_supported_formats(services: ServiceContainer = Depends(get_services)):
    """Get list of supported output formats"""
    return SuccessResponse(data={
        "formats": services.mermaid_cli.get_supported_formats()
    })
