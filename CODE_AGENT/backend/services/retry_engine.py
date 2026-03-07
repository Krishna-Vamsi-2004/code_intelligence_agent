
from typing import Callable, Any, Dict, Optional, TypeVar, Generic
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryEngine:
    def __init__(self, llm_service, max_retries: int = 2):
        self.llm_service = llm_service
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute_stage(
        self,
        stage_name: str,
        original_input: Any,
        generation_fn: Callable[..., str],
        validation_fn: Callable[[str], bool],
        error_context_fn: Callable[[Exception], str] = lambda e: str(e),
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """
        Executes a stage with self-healing retry logic.
        """
        current_input = original_input
        retries = 0
        last_faulty_output = None
        last_error_message = None

        while retries <= self.max_retries:
            try:
                self.logger.info(f"Stage '{stage_name}' - Attempt {retries + 1}/{self.max_retries + 1}")
                
                # Generation stage
                if retries == 0:
                    current_output = generation_fn(current_input, max_new_tokens=max_tokens)
                else:
                    # Correction generation
                    self.logger.info(f"Attempting self-healing correction for stage '{stage_name}'")
                    current_output = self.llm_service.corrective_generate(
                        original_input=str(original_input),
                        faulty_output=last_faulty_output,
                        error_message=last_error_message,
                        stage=stage_name,
                        max_new_tokens=max_tokens
                    )

                self.logger.debug(f"Generated output length: {len(current_output) if current_output else 0}")

                # Validation stage
                is_valid = False
                try:
                    is_valid = validation_fn(current_output)
                    self.logger.debug(f"Validation result: {is_valid}")
                except Exception as val_error:
                    last_error_message = f"Validation error: {error_context_fn(val_error)}"
                    last_faulty_output = current_output
                    self.logger.warning(f"Validation exception: {last_error_message}")
                    retries += 1
                    if retries > self.max_retries:
                        break
                    self.logger.info(f"Retrying stage {stage_name}, attempt {retries + 1}...")
                    continue

                if is_valid:
                    self.logger.info(f"Stage '{stage_name}' completed successfully after {retries} retries")
                    return {
                        "status": "success",
                        "data": current_output,
                        "retries": retries
                    }
                else:
                    last_error_message = "Validation failed: Output does not meet the required format/criteria."
                    last_faulty_output = current_output
                    self.logger.warning(f"Validation failed for stage '{stage_name}'")
            
            except Exception as e:
                last_error_message = error_context_fn(e)
                last_faulty_output = current_output if 'current_output' in locals() else "No valid output generated."
                self.logger.error(f"Exception in stage '{stage_name}': {last_error_message}")
            
            # If we reached here, it's a failure
            retries += 1
            if retries > self.max_retries:
                break
            
            self.logger.info(f"Retrying stage {stage_name}, attempt {retries + 1}...")

        # Final failure
        self.logger.error(f"Stage '{stage_name}' failed after {retries} attempts")
        return {
            "status": "error",
            "stage": stage_name,
            "message": last_error_message or "Unknown error occurred",
            "faulty_output": last_faulty_output or "No output generated",
            "retry_attempted": retries > 0
        }
