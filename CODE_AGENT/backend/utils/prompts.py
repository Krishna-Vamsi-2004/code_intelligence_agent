
class PromptTemplates:
    @staticmethod
    def get_generation_prompt(user_input: str, level: str) -> str:
        """Generate prompt using meta-prompting techniques"""
        levels = {
            "Beginner": {
                "style": "simple and well-commented",
                "complexity": "basic",
                "guidance": "Use simple logic, clear variable names, and add helpful comments"
            },
            "Intermediate": {
                "style": "clean and efficient",
                "complexity": "moderate",
                "guidance": "Use Pythonic patterns, proper error handling, and concise logic"
            },
            "Advanced": {
                "style": "optimized with advanced patterns",
                "complexity": "sophisticated",
                "guidance": "Use advanced techniques, optimal algorithms, and professional patterns"
            }
        }
        
        level_config = levels.get(level, levels['Intermediate'])
        
        # Meta-prompt: Teach the model HOW to generate code
        return f"""You are an expert Python programmer. Your task is to write {level_config['style']} Python code.

TASK: {user_input}

REQUIREMENTS:
1. Write a complete, working function
2. Use descriptive function and variable names
3. Include a docstring explaining what the function does
4. Add type hints if appropriate for {level} level
5. Ensure proper error handling for edge cases
6. Follow PEP 8 style guidelines
7. Make it {level_config['complexity']} in complexity

GUIDANCE: {level_config['guidance']}

OUTPUT FORMAT:
- Start with 'def function_name(parameters):'
- Include docstring on next line
- Write complete implementation
- End with return statement
- NO explanations, ONLY code

CODE:
def """

    @staticmethod
    def get_debug_prompt(code: str) -> str:
        """Generate debugging prompt with meta-prompting"""
        return f"""You are a Python debugging expert. Analyze and fix the code below.

CODE TO DEBUG:
{code}

DEBUGGING PROCESS:
1. Identify syntax errors (missing colons, parentheses, indentation)
2. Find logic errors (wrong operators, incorrect conditions)
3. Check for runtime errors (division by zero, index out of range)
4. Verify edge cases are handled
5. Ensure proper return values

REQUIREMENTS:
- Fix ALL identified issues
- Maintain original functionality
- Keep the same function signature
- Add error handling if missing
- Ensure code is production-ready

OUTPUT: Return ONLY the corrected code, no explanations.

CORRECTED CODE:
"""

    @staticmethod
    def get_mermaid_prompt(code: str) -> str:
        """Generate Mermaid prompt with meta-prompting"""
        return f"""You are a flowchart expert. Create a clear Mermaid diagram for this code.

PYTHON CODE:
{code}

FLOWCHART REQUIREMENTS:
1. Start with 'flowchart TD' (top-down)
2. Use clear node labels (A, B, C, etc.)
3. Show main logic flow
4. Include decision points (if/else)
5. Show loops (for/while)
6. Mark start and end points
7. Keep it simple and readable

NODE TYPES:
- Start/End: ([label])
- Process: [label]
- Decision: {{label}}
- Arrow: -->

EXAMPLE STRUCTURE:
flowchart TD
    A([Start]) --> B[Initialize]
    B --> C{{Check Condition}}
    C -->|Yes| D[Process]
    C -->|No| E[Skip]
    D --> F([End])
    E --> F

OUTPUT: Return ONLY Mermaid syntax, no explanations.

MERMAID CODE:
flowchart TD
"""

    @staticmethod
    def get_score_prompt(code: str, error: str) -> str:
        """Generate syntax fix prompt with meta-prompting"""
        return f"""You are a Python syntax expert. Fix the syntax error in this code.

CODE WITH ERROR:
{code}

ERROR MESSAGE:
{error}

FIX PROCESS:
1. Locate the exact line with the error
2. Identify the syntax issue (missing colon, parenthesis, etc.)
3. Fix ONLY the syntax error
4. Preserve all logic and functionality
5. Ensure proper indentation

REQUIREMENTS:
- Fix syntax error only
- Keep original logic unchanged
- Maintain function signature
- Ensure valid Python syntax

OUTPUT: Return ONLY the corrected code.

FIXED CODE:
"""

    @staticmethod
    def get_corrective_prompt(stage: str, original_input: str, faulty_output: str, error_message: str) -> str:
        """Generate corrective prompt with meta-prompting"""
        if stage == "Visual Flow" or "Mermaid" in stage:
            return f"""You are a Mermaid flowchart expert. Your previous attempt failed. Fix it now.

ORIGINAL REQUEST:
{original_input}

PREVIOUS FAILED OUTPUT:
{faulty_output}

ERROR:
{error_message}

COMMON MERMAID MISTAKES TO AVOID:
1. Not starting with 'flowchart TD'
2. Invalid node syntax (use [], {{}}, ([]))
3. Invalid arrow syntax (use -->)
4. Missing node IDs
5. Unclosed brackets

CORRECTION STEPS:
1. Start with 'flowchart TD'
2. Use simple node IDs: A, B, C
3. Use valid node types: [], {{}}, ([])
4. Connect with -->
5. Test syntax mentally

OUTPUT: Return ONLY valid Mermaid code.

CORRECTED MERMAID:
flowchart TD
"""
        else:
            return f"""You are a Python expert. Your previous code failed. Fix it now.

ORIGINAL REQUEST:
{original_input}

PREVIOUS FAILED CODE:
{faulty_output}

ERROR:
{error_message}

COMMON PYTHON MISTAKES TO AVOID:
1. Missing colons after def, if, for, while
2. Incorrect indentation
3. Undefined variables
4. Missing return statements
5. Syntax errors in expressions

CORRECTION STEPS:
1. Fix syntax errors first
2. Ensure proper indentation (4 spaces)
3. Add missing return statements
4. Handle edge cases
5. Test logic mentally

OUTPUT: Return ONLY corrected Python code.

CORRECTED CODE:
def """

