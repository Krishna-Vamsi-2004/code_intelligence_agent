
from fastapi import APIRouter, Depends, Body
from models.schemas import SuccessResponse, FailureResponse, PipelineRequest
from utils.service_container import ServiceContainer, get_services
import base64

router = APIRouter()

@router.post("/")
async def generate_visual_flow(
    code_for_diagram: str = Body(..., embed=True),
    services: ServiceContainer = Depends(get_services)
):
    """
    Stage 5: Visual Flow (Mermaid syntax generated and rendered via local Mermaid CLI).
    Now uses local rendering for faster, more reliable diagram generation.
    """
    mermaid_prompt = f"Convert this Python code to a Mermaid flowchart. Start with 'flowchart TD'. Code:\n{code_for_diagram}\n\nReturn only the Mermaid syntax, no explanations."

    def validate_flowchart(mermaid_code: str) -> bool:
        """
        Validates Mermaid syntax using local CLI rendering.
        """
        if not services.validator.validate_mermaid(mermaid_code):
            return False
        
        # Validate by attempting to render with local CLI
        is_valid, _ = services.mermaid_cli.validate_syntax(mermaid_code)
        return is_valid

    # Initial generation and rendering using retry engine
    result = services.retry_engine.execute_stage(
        stage_name="Visual Flow Generation (CLI)",
        original_input=mermaid_prompt,
        generation_fn=lambda prompt, max_new_tokens: services.llm.generate(prompt, max_new_tokens),
        validation_fn=validate_flowchart,
        error_context_fn=lambda e: f"Mermaid rendering or parsing error: {str(e)}",
        max_tokens=300
    )

    if result["status"] == "success":
        mermaid_syntax = result["data"]
        
        # Render using local Mermaid CLI
        svg_bytes = services.mermaid_cli.render_diagram(
            mermaid_code=mermaid_syntax,
            output_format="svg",
            background_color="white"
        )
        
        if svg_bytes:
            # Convert to base64 for easy embedding
            svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
            svg_data_uri = f"data:image/svg+xml;base64,{svg_base64}"
            
            # Also keep Kroki URL as fallback
            svg_url = services.kroki.get_svg_url(mermaid_syntax)
            
            return SuccessResponse(data={
                "mermaid_syntax": mermaid_syntax,
                "svg_url": svg_url,  # Kroki URL (fallback)
                "svg_data_uri": svg_data_uri,  # Local CLI render (primary)
                "svg_base64": svg_base64,
                "retries": result["retries"],
                "rendered_locally": True
            })
        else:
            # Local rendering failed, try Kroki as fallback
            svg_url = services.kroki.get_svg_url(mermaid_syntax)
            return SuccessResponse(data={
                "mermaid_syntax": mermaid_syntax,
                "svg_url": svg_url,
                "retries": result["retries"],
                "rendered_locally": False,
                "fallback": "kroki"
            })
    else:
        # If it failed, try the simplified diagram correction
        simplified_prompt = f"Create a simple Mermaid flowchart for this code. Use minimal nodes and clear flow. Start with 'flowchart TD'. Code:\n{code_for_diagram}"
        simplified_result = services.retry_engine.execute_stage(
            stage_name="Simplified Visual Flow (CLI)",
            original_input=simplified_prompt,
            generation_fn=lambda prompt, max_new_tokens: services.llm.generate(prompt, max_new_tokens),
            validation_fn=validate_flowchart,
            error_context_fn=lambda e: f"Simplified Mermaid error: {str(e)}",
            max_tokens=200
        )

        if simplified_result["status"] == "success":
            mermaid_syntax = simplified_result["data"]
            
            # Render using local CLI
            svg_bytes = services.mermaid_cli.render_diagram(
                mermaid_code=mermaid_syntax,
                output_format="svg",
                background_color="white"
            )
            
            if svg_bytes:
                svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
                svg_data_uri = f"data:image/svg+xml;base64,{svg_base64}"
                svg_url = services.kroki.get_svg_url(mermaid_syntax)
                
                return SuccessResponse(data={
                    "mermaid_syntax": mermaid_syntax,
                    "svg_url": svg_url,
                    "svg_data_uri": svg_data_uri,
                    "svg_base64": svg_base64,
                    "simplified": True,
                    "rendered_locally": True
                })
            else:
                svg_url = services.kroki.get_svg_url(mermaid_syntax)
                return SuccessResponse(data={
                    "mermaid_syntax": mermaid_syntax,
                    "svg_url": svg_url,
                    "simplified": True,
                    "rendered_locally": False,
                    "fallback": "kroki"
                })
        else:
            # Final failure
            return FailureResponse(
                stage="Visual Flow",
                message=f"Mermaid generation failed even after simplification: {simplified_result['message']}",
                retry_attempted=True,
                faulty_output=result.get("faulty_output", "")
            )
