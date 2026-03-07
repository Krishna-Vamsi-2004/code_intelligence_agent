"""
GENERATE ROUTER - Standalone Code Generation Endpoint

This router provides a standalone endpoint for code generation only,
without running the full pipeline.

Endpoint: POST /api/generate
Request Body: {
    "user_input": "bubble sort",
    "experience_level": "Beginner" | "Intermediate" | "Advanced"
}

Response: Generated code with retry count
"""

from fastapi import APIRouter, Depends, Body
from models.schemas import SuccessResponse, FailureResponse, PipelineRequest
from utils.service_container import ServiceContainer, get_services
from utils.prompts import PromptTemplates

# Create FastAPI router instance
router = APIRouter()

@router.post("/")
async def generate_code(
    request: PipelineRequest = Body(...),
    services: ServiceContainer = Depends(get_services)
):
    """
    Standalone Code Generation Endpoint
    
    Generates Python code based on user input and experience level.
    Uses Ollama with meta-prompting and falls back to templates if needed.
    
    Args:
        request: PipelineRequest containing:
            - user_input: Task description (e.g., "linear search")
            - experience_level: "Beginner", "Intermediate", or "Advanced"
        services: Injected service container
    
    Returns:
        SuccessResponse with generated code, or FailureResponse on error
    """
    # Create generation prompt with user level context
    prompt = PromptTemplates.get_generation_prompt(request.user_input, request.experience_level)

    # Execute code generation with retry engine (up to 3 attempts)
    result = services.retry_engine.execute_stage(
        stage_name="Code Generation",
        original_input=prompt,
        # Lambda function that calls LLM with user level
        generation_fn=lambda prompt, max_new_tokens: services.llm.generate(prompt, max_new_tokens, request.experience_level),
        # Validate generated code has valid Python syntax
        validation_fn=services.validator.validate_python_ast,
        # Error context function for better error messages
        error_context_fn=lambda e: f"Python Syntax Error: {str(e)}",
        max_tokens=400
    )

    # Return success or failure response
    if result["status"] == "success":
        return SuccessResponse(data={"generated_code": result["data"], "retries": result["retries"]})
    else:
        return FailureResponse(
            stage="Code Generation",
            message=result["message"],
            retry_attempted=result["retry_attempted"],
            faulty_output=result["faulty_output"]
        )
