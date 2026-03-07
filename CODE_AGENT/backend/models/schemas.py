
from pydantic import BaseModel
from typing import Optional, Any, Dict, List

class SuccessResponse(BaseModel):
    status: str = "success"
    data: Any

class FailureResponse(BaseModel):
    status: str = "error"
    stage: str
    message: str
    retry_attempted: bool
    faulty_output: Optional[str] = None

class ErrorObject(BaseModel):
    stage: str
    error_type: str
    error_message: str
    faulty_output: str

class PipelineRequest(BaseModel):
    user_input: str
    experience_level: str = "Intermediate" # Beginner / Intermediate / Advanced
