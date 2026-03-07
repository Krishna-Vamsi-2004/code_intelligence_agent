"""
SCORE ROUTER - Code Quality Scoring Endpoint

This router calculates code quality metrics and optimality scores.
If code has syntax errors, it attempts to fix them before scoring.

Endpoint: POST /api/score
Request Body: {
    "code_to_score": "def foo():\n  return 42"
}

Response: Score metrics (complexity, lines, functions, etc.)
"""

from fastapi import APIRouter, Depends, Body
from models.schemas import SuccessResponse, FailureResponse, PipelineRequest
from utils.service_container import ServiceContainer, get_services

# Create FastAPI router instance
router = APIRouter()

@router.post("/")
async def score_code(
    code_to_score: str = Body(..., embed=True),
    services: ServiceContainer = Depends(get_services)
):
    """
    Code Quality Scoring Endpoint
    
    Calculates optimality score based on:
    - Code complexity (cyclomatic complexity)
    - Number of lines
    - Number of functions/classes
    - Code structure quality
    
    If AST parsing fails (syntax error), attempts to fix the code first.
    
    Args:
        code_to_score: Python code string to analyze
        services: Injected service container
    
    Returns:
        SuccessResponse with score metrics, or FailureResponse on error
    """
    
    def score_calculation_fn(code: str, tokens: int = 500) -> str:
        """
        Wrapper function for retry engine compatibility
        
        This function is used as generation_fn for the retry engine,
        but for scoring it just returns the code being validated.
        The actual scoring happens after validation.
        """
        return code
    
    def validate_ast(code: str) -> bool:
        """Validate code has valid Python syntax"""
        return services.validator.validate_python_ast(code)

    # Calculate initial score
    score_data = services.score.calculate_optimality_score(code_to_score)
    
    # If no error, return score immediately
    if "error" not in score_data:
        return SuccessResponse(data=score_data)
    
    # AST parsing failed - try to fix syntax errors
    error_msg = score_data.get("error", "AST parsing failed.")
    
    # Create fix prompt with error details
    fix_prompt = services.score.get_syntax_fix_prompt(code_to_score, error_msg)

    # Execute syntax fix with retry engine
    result = services.retry_engine.execute_stage(
        stage_name="Score Syntax Correction",
        original_input=fix_prompt,
        # Lambda function that calls LLM to fix syntax
        generation_fn=lambda prompt, max_new_tokens: services.llm.generate(prompt, max_new_tokens),
        # Validate fixed code has valid syntax
        validation_fn=validate_ast,
        # Error context function
        error_context_fn=lambda e: f"Syntax Fix Error: {str(e)}",
        max_tokens=400
    )

    # Return results
    if result["status"] == "success":
        # Recalculate score with fixed code
        fixed_score_data = services.score.calculate_optimality_score(result["data"])
        return SuccessResponse(data={"fixed_score": fixed_score_data, "fixed_code": result["data"], "retries": result["retries"]})
    else:
        # Syntax fix failed
        return FailureResponse(
            stage="Optimality Score",
            message="AST parsing failed after retries.",
            retry_attempted=result["retry_attempted"],
            faulty_output=result["faulty_output"]
        )
