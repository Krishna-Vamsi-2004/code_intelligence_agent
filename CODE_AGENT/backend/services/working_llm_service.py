"""
Optimized LLM Service - 100% Dynamic Generation with Ollama
All template-based generation is commented out - using pure LLM generation
"""
import os
import re
import logging
from dotenv import load_dotenv
# Templates kept as reference but not used
# from services.enhanced_templates import (
#     get_linear_search_template,
#     get_bubble_sort_template,
#     get_factorial_template
# )

load_dotenv(override=True)
logger = logging.getLogger(__name__)


class WorkingLLMService:
    """LLM Service with 100% dynamic Ollama generation"""
    
    def __init__(self):
        """Initialize with Ollama for dynamic generation"""
        self.use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
        
        if self.use_ollama:
            from services.ollama_service import OllamaService
            ollama_model = os.getenv("OLLAMA_MODEL", "deepseek-coder:1.3b")
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            self.ollama = OllamaService(ollama_model, ollama_url)
            
            if self.ollama.is_available():
                logger.info(f"🤖 Using 100% Dynamic Ollama Generation: {ollama_model}")
                self.max_new_tokens = 800
            else:
                logger.error("❌ Ollama not available - Dynamic generation requires Ollama!")
                self.use_ollama = False
        
        if not self.use_ollama:
            logger.error("⚠️ Dynamic generation disabled - Ollama required!")
    
    def generate(self, prompt: str, max_new_tokens: int = None, user_level: str = None) -> str:
        """Generate code using 100% dynamic Ollama generation"""
        try:
            if not prompt or not prompt.strip():
                return "# Error: Empty prompt"

            # Check if Ollama is available
            if not self.use_ollama:
                logger.error("❌ Ollama not available - cannot generate code")
                return "# Error: Ollama not available. Please start Ollama service."

            # Special handling for Mermaid diagram requests
            if "mermaid" in prompt.lower() or "flowchart" in prompt.lower() or "diagram" in prompt.lower():
                logger.info("Detected Mermaid diagram request")
                return self._generate_mermaid_from_prompt(prompt)

            # Extract simple task
            simple_task = self._extract_simple_task(prompt)
            logger.info(f"🚀 Dynamic generation for: {simple_task[:100]}")

            # Use Ollama for 100% dynamic generation
            logger.info("Using 100% Dynamic Ollama Generation")
            for attempt in range(3):
                logger.info(f"🤖 Ollama attempt {attempt + 1}/3")
                code = self._generate_with_ollama(simple_task, max_new_tokens or self.max_new_tokens, user_level)

                # Validate generated code
                if code and len(code) > 40:
                    try:
                        import ast
                        ast.parse(code)
                        logger.info(f"✅ Dynamic generation SUCCESS - {len(code)} chars")
                        return code
                    except SyntaxError as e:
                        logger.warning(f"❌ Attempt {attempt + 1} syntax error: {e}")
                        continue

            # All attempts failed
            logger.error("❌ All dynamic generation attempts failed")
            return "# Error: Code generation failed after 3 attempts. Please try again."

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"# Error: {str(e)}"

    
    def _generate_with_ollama(self, task: str, max_tokens: int, user_level: str = None) -> str:
        """Generate code using Ollama service"""
        try:
            code = self.ollama.generate_code(task, user_level)
            
            if not code:
                logger.warning("Ollama returned empty response")
                return ""
            
            logger.info(f"Ollama generated {len(code)} chars")
            return self._fix_common_issues(code)
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return ""
    
    def _get_template_fallback(self, task: str, user_level: str = None) -> str:
        """Get template-based code as fallback"""
        task_lower = task.lower()
        
        if user_level:
            level = user_level.lower()
        else:
            level = self._get_complexity_level(task_lower)
        
        logger.info(f"📊 Using {level} level template")
        
        # Basic arithmetic operations
        if any(word in task_lower for word in ['sum', 'add', 'addition']) and 'number' in task_lower:
            return self._get_sum_template(level)
        
        if any(word in task_lower for word in ['subtract', 'difference', 'minus']) and 'number' in task_lower:
            return self._get_subtract_template(level)
        
        if any(word in task_lower for word in ['multiply', 'product', 'times']) and 'number' in task_lower:
            return self._get_multiply_template(level)
        
        if any(word in task_lower for word in ['divide', 'division']) and 'number' in task_lower:
            return self._get_divide_template(level)
        
        # Search algorithms
        if "linear search" in task_lower:
            return get_linear_search_template(level)
        
        if "binary search" in task_lower:
            return self._get_binary_search_template(level)
        
        # Sorting algorithms
        if "bubble sort" in task_lower:
            return get_bubble_sort_template(level)
        
        if "quick sort" in task_lower or "quicksort" in task_lower:
            return self._get_quick_sort_template(level)
        
        # Math functions
        if "factorial" in task_lower:
            return get_factorial_template(level)
        
        if "fibonacci" in task_lower:
            return self._get_fibonacci_template(level)
        
        if "prime" in task_lower and ("check" in task_lower or "test" in task_lower):
            return self._get_prime_template(level)
        
        # String operations
        if "palindrome" in task_lower:
            return self._get_palindrome_template(level)
        
        if "reverse" in task_lower and "string" in task_lower:
            return self._get_reverse_string_template(level)
        
        # Default fallback
        logger.warning("No template match found")
        return self._get_generic_template(task)
    
    def _get_complexity_level(self, task: str) -> str:
        """Get complexity level - defaults to intermediate"""
        return 'intermediate'
    
    # Basic arithmetic templates
    def _get_sum_template(self, level):
        """Sum of numbers template"""
        if level == 'beginner':
            return """# Get two numbers from user
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

# Calculate sum
result = num1 + num2

# Display result
print(f"Sum: {result}")"""
        
        elif level == 'intermediate':
            return """def add_numbers():
    \"\"\"Add two numbers with input validation\"\"\"
    try:
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        result = num1 + num2
        print(f"Sum of {num1} and {num2} is: {result}")
    except ValueError:
        print("Error: Please enter valid numbers")

if __name__ == "__main__":
    add_numbers()"""
        
        else:  # advanced
            return """from typing import Union

class Calculator:
    \"\"\"Simple calculator for addition\"\"\"
    
    def __init__(self):
        self.history = []
    
    def add(self, num1: Union[int, float], num2: Union[int, float]) -> Union[int, float]:
        \"\"\"Add two numbers and track history\"\"\"
        result = num1 + num2
        self.history.append(f"{num1} + {num2} = {result}")
        return result
    
    def show_history(self):
        \"\"\"Display calculation history\"\"\"
        print("\\nCalculation History:")
        for calc in self.history:
            print(f"  {calc}")

if __name__ == "__main__":
    calc = Calculator()
    
    while True:
        print("\\n1. Add numbers")
        print("2. Show history")
        print("3. Quit")
        
        choice = input("Choose: ")
        
        if choice == '1':
            try:
                num1 = float(input("Enter first number: "))
                num2 = float(input("Enter second number: "))
                result = calc.add(num1, num2)
                print(f"Result: {result}")
            except ValueError:
                print("Invalid input")
        elif choice == '2':
            calc.show_history()
        elif choice == '3':
            break"""
    
    def _get_subtract_template(self, level):
        """Subtraction template"""
        if level == 'beginner':
            return """# Get two numbers
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

# Calculate difference
result = num1 - num2

# Show result
print(f"Difference: {result}")"""
        return self._get_sum_template(level).replace('add', 'subtract').replace('Sum', 'Difference').replace('+', '-')
    
    def _get_multiply_template(self, level):
        """Multiplication template"""
        if level == 'beginner':
            return """# Get two numbers
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

# Calculate product
result = num1 * num2

# Show result
print(f"Product: {result}")"""
        return self._get_sum_template(level).replace('add', 'multiply').replace('Sum', 'Product').replace('+', '*')
    
    def _get_divide_template(self, level):
        """Division template"""
        if level == 'beginner':
            return """# Get two numbers
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

# Check for division by zero
if num2 != 0:
    result = num1 / num2
    print(f"Result: {result}")
else:
    print("Error: Cannot divide by zero")"""
        
        elif level == 'intermediate':
            return """def divide_numbers():
    \"\"\"Divide two numbers with validation\"\"\"
    try:
        num1 = float(input("Enter first number: "))
        num2 = float(input("Enter second number: "))
        
        if num2 == 0:
            print("Error: Cannot divide by zero")
        else:
            result = num1 / num2
            print(f"{num1} / {num2} = {result}")
    except ValueError:
        print("Error: Please enter valid numbers")

if __name__ == "__main__":
    divide_numbers()"""
        
        return self._get_sum_template(level).replace('add', 'divide').replace('Sum', 'Quotient').replace('+', '/')
    
    def corrective_generate(self, original_input: str, faulty_output: str, error_message: str, stage: str, max_new_tokens: int = 400) -> str:
        """Generate corrected output based on error feedback - handles both Python code and Mermaid"""
        
        # Check if this is a Mermaid generation stage
        is_mermaid_stage = "visual" in stage.lower() or "mermaid" in stage.lower() or "flow" in stage.lower()
        
        if is_mermaid_stage:
            # For Mermaid, extract the code from original input and regenerate
            logger.info("🔄 Corrective Mermaid generation")
            code_match = re.search(r'```python\n(.*?)\n```', original_input, re.DOTALL)
            if not code_match:
                code_match = re.search(r'```\n(.*?)\n```', original_input, re.DOTALL)
            
            if code_match:
                code = code_match.group(1)
            else:
                # Extract code from lines
                lines = original_input.split('\n')
                code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
                code = '\n'.join(code_lines)
            
            # Use Ollama to regenerate Mermaid
            if self.use_ollama and self.ollama.is_available():
                try:
                    mermaid_code = self.ollama.generate_mermaid(code)
                    if mermaid_code and len(mermaid_code) > 20:
                        return mermaid_code
                except Exception as e:
                    logger.error(f"Mermaid correction failed: {e}")
            
            logger.error("❌ Mermaid correction failed")
            return ""
        
        else:
            # For Python code correction
            correction_prompt = f"""Fix the following error in {stage}:

Error: {error_message}

Original task: {original_input}

Faulty output:
{faulty_output}

Generate corrected Python code:

```python"""
            
            try:
                if self.use_ollama and self.ollama.is_available():
                    corrected = self.ollama.generate(correction_prompt, max_new_tokens)
                    code = self.ollama._extract_code(corrected)
                    if code and len(code) > 20:
                        return code
                
                logger.error("❌ Ollama not available for correction")
                return ""
                
            except Exception as e:
                logger.error(f"Corrective generation failed: {e}")
                return ""
    
    def _extract_simple_task(self, prompt: str) -> str:
        """Extract the core task from prompt"""
        prompt = prompt.lower().strip()
        
        prefixes = [
            'write code for', 'write a function for', 'write a program for',
            'create code for', 'create a function for', 'generate code for',
            'implement', 'code for', 'write', 'create', 'generate',
            'make a function for', 'make code for'
        ]
        
        for prefix in prefixes:
            if prompt.startswith(prefix):
                prompt = prompt[len(prefix):].strip()
                break
        
        return prompt
    
    def _fix_common_issues(self, code: str) -> str:
        """Fix common formatting issues in generated code"""
        if not code:
            return code
        
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if not fixed_lines and not line.strip():
                continue
            fixed_lines.append(line)
        
        while fixed_lines and not fixed_lines[-1].strip():
            fixed_lines.pop()
        
        return '\n'.join(fixed_lines)
    
    def _generate_mermaid_from_prompt(self, prompt: str) -> str:
        """Generate Mermaid diagram dynamically using Ollama from code logic"""
        # Extract code from prompt
        code_match = re.search(r'```python\n(.*?)\n```', prompt, re.DOTALL)
        if not code_match:
            code_match = re.search(r'```\n(.*?)\n```', prompt, re.DOTALL)
        
        if code_match:
            code = code_match.group(1)
        else:
            lines = prompt.split('\n')
            code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
            code = '\n'.join(code_lines)
        
        # Use Ollama to generate Mermaid diagram from code logic
        if self.use_ollama and self.ollama.is_available():
            try:
                # Use dedicated Mermaid generation method
                mermaid_code = self.ollama.generate_mermaid(code)
                
                if mermaid_code:
                    logger.info(f"✅ Generated Mermaid diagram dynamically from code logic")
                    return mermaid_code
                    
            except Exception as e:
                logger.error(f"Ollama Mermaid generation failed: {e}")
        
        # Fallback to generic template only if Ollama fails
        logger.warning("Using generic Mermaid template as fallback")
        mermaid = "flowchart TD\n"
        mermaid += "    Start([Start]) --> Input[Get Input]\n"
        mermaid += "    Input --> Process[Process Data]\n"
        mermaid += "    Process --> Output[Return Result]\n"
        mermaid += "    Output --> End([End])\n"
        
        return mermaid
    
    # Template methods (simplified versions)
    def _get_binary_search_template(self, level):
        """Binary search template"""
        if level == 'beginner':
            return """def binary_search(arr, target):
    \"\"\"Binary search (array must be sorted)\"\"\"
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9, 11, 13]
    target = int(input("Enter target: "))
    result = binary_search(arr, target)
    print(f"Found at index: {result}" if result != -1 else "Not found")"""
        return """def binary_search(arr, target):
    \"\"\"Binary search with steps\"\"\"
    left, right = 0, len(arr) - 1
    steps = 0
    
    while left <= right:
        steps += 1
        mid = (left + right) // 2
        print(f"Step {steps}: Checking index {mid}, value {arr[mid]}")
        
        if arr[mid] == target:
            return mid, steps
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1, steps

if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9, 11, 13]
    target = int(input("Enter target: "))
    result, steps = binary_search(arr, target)
    print(f"Found at {result} in {steps} steps" if result != -1 else f"Not found after {steps} steps")"""
    
    def _get_quick_sort_template(self, level):
        """Quick sort template"""
        return """def quick_sort(arr):
    \"\"\"Quick sort algorithm\"\"\"
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

if __name__ == "__main__":
    arr = list(map(int, input("Enter numbers: ").split()))
    print(f"Sorted: {quick_sort(arr)}")"""
    
    def _get_fibonacci_template(self, level):
        """Fibonacci template"""
        return """def fibonacci(n):
    \"\"\"Generate first n Fibonacci numbers\"\"\"
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

if __name__ == "__main__":
    n = int(input("How many numbers? "))
    print(f"Fibonacci: {fibonacci(n)}")"""
    
    def _get_prime_template(self, level):
        """Prime check template"""
        return """def is_prime(n):
    \"\"\"Check if number is prime\"\"\"
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    n = int(input("Enter number: "))
    print(f"{n} is {'prime' if is_prime(n) else 'not prime'}")"""
    
    def _get_palindrome_template(self, level):
        """Palindrome check template"""
        return """def is_palindrome(s):
    \"\"\"Check if string is palindrome\"\"\"
    s = s.lower().replace(' ', '')
    return s == s[::-1]

if __name__ == "__main__":
    text = input("Enter text: ")
    print(f"'{text}' is {'a palindrome' if is_palindrome(text) else 'not a palindrome'}")"""
    
    def _get_reverse_string_template(self, level):
        """Reverse string template"""
        return """def reverse_string(s):
    \"\"\"Reverse a string\"\"\"
    return s[::-1]

if __name__ == "__main__":
    text = input("Enter text: ")
    print(f"Reversed: {reverse_string(text)}")"""
    
    def _get_generic_template(self, task):
        """Generic template when no match found"""
        return f"""def process_data(data):
    \"\"\"
    Process data for: {task}
    TODO: Implement the logic
    \"\"\"
    # Add your implementation here
    processed = data
    return processed

if __name__ == "__main__":
    data = input("Enter data: ")
    output = process_data(data)
    print(f"Result: {output}")"""
