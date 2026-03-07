"""
PIPELINE ROUTER - Main Orchestration Endpoint

This is the MOST IMPORTANT router in the system. It orchestrates the complete
code generation pipeline from start to finish.

Pipeline Flow:
1. Code Generation - Generate code using Ollama/templates with user level
2. Debugging - Fix any issues in the generated code
3. Scoring - Calculate code quality metrics
4. Visualization - Create Mermaid flowchart diagram

Endpoint: POST /api/pipeline/run
Request Body: {
    "user_input": "bubble sort",
    "experience_level": "Beginner" | "Intermediate" | "Advanced"
}

Response: Complete pipeline results with code, score, and diagram
"""

from fastapi import APIRouter, Depends, Body
from models.schemas import SuccessResponse, FailureResponse, PipelineRequest
from utils.service_container import ServiceContainer, get_services
from utils.prompts import PromptTemplates

# Create FastAPI router instance
router = APIRouter()

@router.post("/run")
async def run_pipeline(
    request: PipelineRequest = Body(...),
    services: ServiceContainer = Depends(get_services)
):
    """
    Full Agentic Pipeline Orchestration
    
    This endpoint runs all 4 stages of the code generation pipeline:
    1. Code Generation - Uses Ollama with meta-prompting based on user level
    2. Debugging - Fixes syntax errors and improves code quality
    3. Optimality Score - Calculates code complexity and quality metrics
    4. Visual Flow - Generates Mermaid flowchart diagram
    
    Args:
        request: PipelineRequest containing:
            - user_input: Task description (e.g., "bubble sort")
            - experience_level: "Beginner", "Intermediate", or "Advanced"
        services: Injected service container with all dependencies
    
    Returns:
        SuccessResponse with results from all pipeline stages
    """
    # Dictionary to store results from each pipeline stage
    pipeline_results = {}

    # ========== STAGE 1: CODE GENERATION ==========
    # Generate Python code based on user input and experience level
    
    # Create generation prompt with user level context
    gen_prompt = PromptTemplates.get_generation_prompt(request.user_input, request.experience_level)
    
    # Execute generation with retry engine (up to 3 attempts)
    gen_result = services.retry_engine.execute_stage(
        stage_name="Code Generation",
        original_input=gen_prompt,
        # Lambda function that calls LLM with user level
        generation_fn=lambda prompt, max_new_tokens: (
            services.llm.generate(prompt, max_new_tokens, request.experience_level) if services.llm 
            else services.simple_generator.generate_from_prompt(request.user_input)
        ),
        # Validate generated code has valid Python syntax
        validation_fn=services.validator.validate_python_ast,
        max_tokens=300  # Limit tokens for faster generation
    )
    
    # Handle generation failure
    if gen_result["status"] == "error":
        # Try simple generator as last resort if no LLM available
        if not services.llm:
            try:
                code = services.simple_generator.generate_from_prompt(request.user_input)
                gen_result = {"status": "success", "data": code, "retries": 0, "fallback": True}
            except:
                # Complete failure - return error and skip remaining stages
                return SuccessResponse(data={
                    "code_generation": {"status": "error", "message": "All generation methods failed", "faulty_output": gen_result.get("faulty_output")},
                    "debugging": {"status": "skipped"},
                    "score": {"status": "skipped"},
                    "visual_flow": {"status": "skipped"}
                })
        else:
            # LLM failed - return error and skip remaining stages
            return SuccessResponse(data={
                "code_generation": {"status": "error", "message": gen_result["message"], "faulty_output": gen_result.get("faulty_output")},
                "debugging": {"status": "skipped"},
                "score": {"status": "skipped"},
                "visual_flow": {"status": "skipped"}
            })
    
    # Store generated code for next stages
    current_code = gen_result["data"]
    pipeline_results["code_generation"] = {"status": "success", "code": current_code, "retries": gen_result["retries"]}

    # ========== STAGE 2: DEBUGGING ==========
    # Fix any issues in the generated code
    
    # Skip debugging if code came from template (already perfect)
    if gen_result.get("fallback"):
        pipeline_results["debugging"] = {"status": "skipped", "message": "Code from template, no debugging needed"}
    else:
        # Create debugging prompt with the generated code
        debug_prompt = PromptTemplates.get_debug_prompt(current_code)
        
        # Execute debugging with retry engine
        debug_result = services.retry_engine.execute_stage(
            stage_name="Debugging",
            original_input=debug_prompt,
            # Lambda function that calls LLM with user level for debugging
            generation_fn=lambda prompt, max_new_tokens: (
                services.llm.generate(prompt, max_new_tokens, request.experience_level) if services.llm
                else current_code  # Return unchanged if no LLM
            ),
            # Validate debugged code has valid syntax
            validation_fn=services.validator.validate_python_ast,
            max_tokens=300
        )
        
        if debug_result["status"] == "success":
            # Update current code with debugged version
            current_code = debug_result["data"]
            pipeline_results["debugging"] = {"status": "success", "fixed_code": current_code, "retries": debug_result["retries"]}
        else:
            # Debugging failed, keep original code
            pipeline_results["debugging"] = {
                "status": "error",
                "message": debug_result["message"],
                "faulty_output": debug_result.get("faulty_output"),
                "fallback_used": True
            }

    # ========== STAGE 3: OPTIMALITY SCORE ==========
    # Calculate code quality metrics (complexity, lines, functions, etc.)
    
    score_data = services.score.calculate_optimality_score(current_code)
    
    # If scoring failed due to syntax error, try to fix it
    if "error" in score_data:
        # Create fix prompt with error details
        fix_prompt = PromptTemplates.get_score_prompt(current_code, score_data["error"])
        
        # Try to fix syntax error with retry engine
        fix_result = services.retry_engine.execute_stage(
            stage_name="Score Syntax Correction",
            original_input=fix_prompt,
            # Lambda function that calls LLM with user level for fixing
            generation_fn=lambda prompt, max_new_tokens: services.llm.generate(prompt, max_new_tokens, request.experience_level),
            validation_fn=services.validator.validate_python_ast,
            max_tokens=400
        )
        
        if fix_result["status"] == "success":
            # Update code and recalculate score
            current_code = fix_result["data"]
            score_data = services.score.calculate_optimality_score(current_code)
            pipeline_results["score"] = {"status": "success", **score_data}
        else:
            # Syntax fix failed, return error with zero score
            pipeline_results["score"] = {"status": "error", "message": "AST parsing failed after self-healing.", "score": 0}
    else:
        # Scoring succeeded
        pipeline_results["score"] = {"status": "success", **score_data}

    # ========== STAGE 4: VISUAL FLOW (MERMAID DIAGRAM) ==========
    # Generate flowchart diagram from the code
    
    # Create Mermaid generation prompt
    mermaid_prompt = PromptTemplates.get_mermaid_prompt(current_code)
    
    def validate_mermaid_flow(m_code: str) -> bool:
        """
        Validate Mermaid syntax using local CLI
        
        Args:
            m_code: Mermaid diagram syntax
        
        Returns:
            True if valid, False otherwise
        """
        # First check basic Mermaid syntax
        if not services.validator.validate_mermaid(m_code): 
            return False
        # Then validate by attempting to render with local CLI
        is_valid, _ = services.mermaid_cli.validate_syntax(m_code)
        return is_valid

    # Execute Mermaid generation with retry engine
    mermaid_result = services.retry_engine.execute_stage(
        stage_name="Visual Flow (CLI)",
        original_input=mermaid_prompt,
        # Lambda function that calls LLM with user level for Mermaid
        generation_fn=lambda prompt, max_new_tokens: (
            services.llm.generate(prompt, max_new_tokens, request.experience_level) if services.llm
            else services.simple_generator.generate_mermaid_for_code(current_code)
        ),
        # Validate Mermaid syntax
        validation_fn=validate_mermaid_flow,
        max_tokens=200  # Mermaid diagrams are typically shorter
    )
    
    if mermaid_result["status"] == "success":
        mermaid_syntax = mermaid_result["data"]
        
        # Render Mermaid diagram to SVG using local CLI
        import base64
        svg_bytes = services.mermaid_cli.render_diagram(
            mermaid_code=mermaid_syntax,
            output_format="svg",
            background_color="white"
        )
        
        if svg_bytes:
            # Successfully rendered locally - convert to base64
            svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
            svg_data_uri = f"data:image/svg+xml;base64,{svg_base64}"
            svg_url = services.kroki.get_svg_url(mermaid_syntax)  # Kroki URL as fallback
            
            pipeline_results["visual_flow"] = {
                "status": "success",
                "mermaid_syntax": mermaid_syntax,
                "svg_url": svg_url,  # Kroki URL (fallback)
                "svg_data_uri": svg_data_uri,  # Local render (primary)
                "svg_base64": svg_base64,
                "rendered_locally": True,
                "retries": mermaid_result["retries"]
            }
        else:
            # Local rendering failed, use Kroki as fallback
            svg_url = services.kroki.get_svg_url(mermaid_syntax)
            pipeline_results["visual_flow"] = {
                "status": "success",
                "mermaid_syntax": mermaid_syntax,
                "svg_url": svg_url,
                "rendered_locally": False,
                "fallback": "kroki",
                "retries": mermaid_result["retries"]
            }
    else:
        # Mermaid generation failed - try simple generator as last resort
        if not services.llm:
            try:
                mermaid_syntax = services.simple_generator.generate_mermaid_for_code(current_code)
                
                # Validate the generated Mermaid
                if validate_mermaid_flow(mermaid_syntax):
                    # Try to render locally
                    import base64
                    svg_bytes = services.mermaid_cli.render_diagram(
                        mermaid_code=mermaid_syntax,
                        output_format="svg",
                        background_color="white"
                    )
                    
                    if svg_bytes:
                        # Local render succeeded
                        svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
                        svg_data_uri = f"data:image/svg+xml;base64,{svg_base64}"
                        svg_url = services.kroki.get_svg_url(mermaid_syntax)
                        
                        pipeline_results["visual_flow"] = {
                            "status": "success",
                            "mermaid_syntax": mermaid_syntax,
                            "svg_url": svg_url,
                            "svg_data_uri": svg_data_uri,
                            "svg_base64": svg_base64,
                            "rendered_locally": True,
                            "retries": 0,
                            "fallback": "simple_generator"
                        }
                    else:
                        # Local render failed, use Kroki
                        svg_url = services.kroki.get_svg_url(mermaid_syntax)
                        pipeline_results["visual_flow"] = {
                            "status": "success",
                            "mermaid_syntax": mermaid_syntax,
                            "svg_url": svg_url,
                            "rendered_locally": False,
                            "retries": 0,
                            "fallback": "kroki"
                        }
                else:
                    # Validation failed
                    pipeline_results["visual_flow"] = {
                        "status": "error",
                        "message": "Mermaid generation failed",
                        "faulty_output": mermaid_syntax
                    }
            except Exception as e:
                # Complete failure
                pipeline_results["visual_flow"] = {
                    "status": "error",
                    "message": f"All Mermaid generation methods failed: {str(e)}",
                    "faulty_output": mermaid_result.get("faulty_output")
                }
        else:
            # LLM available but failed
            pipeline_results["visual_flow"] = {
                "status": "error",
                "message": mermaid_result["message"],
                "faulty_output": mermaid_result.get("faulty_output")
            }

    # Return complete pipeline results
    return SuccessResponse(data=pipeline_results)
