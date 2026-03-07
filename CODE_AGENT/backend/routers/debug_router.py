"""
DEBUG ROUTER - Standalone Code Debugging Endpoint

This router provides a standalone endpoint for debugging existing code.
It identifies and fixes bugs, syntax errors, and improves code quality.

Endpoint: POST /api/debug
Request Body: {
    "code_to_debug": "def foo():\n  print('hello'"  // Code with issues
}

Response: Fixed code with retry count
"""

from fastapi import APIRouter, Depends, Body
from models.schemas import SuccessResponse, FailureResponse, PipelineRequest
from utils.service_container import ServiceContainer, get_services

# Create FastAPI router instance
router = APIRouter()

@router.post("/")
async def debug_code(
    code_to_debug: str = Body(..., embed=True),
    services: ServiceContainer = Depends(get_services)
):
    """
    Standalone Code Debugging Endpoint
    
    Analyzes code for bugs and syntax errors, then generates fixed version.
    Uses LLM to identify issues and provide corrections.
    
    Args:
        code_to_debug: Python code string that needs debugging
        services: Injected service container
    
    Returns:
        SuccessResponse with fixed code, or FailureResponse on error
    
    Note:
        This endpoint doesn't receive experience_level because it's
        debugging existing code, not generating new code.
    """
    # Create debugging prompt with the code to fix
    prompt = f"Identify and fix bugs in this Python code:\n{code_to_debug}\n\nReturn fixed code only."

    # Execute debugging with retry engine (up to 3 attempts)
    result = services.retry_engine.execute_stage(
        stage_name="Debugging",
        original_input=prompt,
        # Lambda function that calls LLM for debugging
        generation_fn=lambda prompt, max_new_tokens: services.llm.generate(prompt, max_new_tokens),
        # Validate fixed code has valid Python syntax
        validation_fn=services.validator.validate_python_ast,
        # Error context function for better error messages
        error_context_fn=lambda e: f"Debugging Fix Syntax Error: {str(e)}",
        max_tokens=400
    )

    # Return success or failure response
    if result["status"] == "success":
        return SuccessResponse(data={"fixed_code": result["data"], "retries": result["retries"]})
    else:
        return FailureResponse(
            stage="Debugging",
            message=result["message"],
            retry_attempted=result["retry_attempted"],
            faulty_output=result["faulty_output"]
        )
