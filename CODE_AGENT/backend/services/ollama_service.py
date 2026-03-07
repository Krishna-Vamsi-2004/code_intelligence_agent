"""
Ollama Local LLM Service
Uses Ollama to run local models like DeepSeek-Coder
Enhanced with meta-prompting for different user levels
"""
import requests
import logging
import random

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama local LLM with meta-prompting"""
    
    def __init__(self, model_name="deepseek-coder:1.3b", base_url="http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.generation_count = 0
        
    def is_available(self):
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate code using Ollama"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": max_tokens,
                    "top_p": 0.9,
                    "top_k": 40,
                    "stop": []  # Let it generate fully
                }
            }
            
            logger.info(f"🤖 Calling Ollama with {self.model_name}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=90  # Increased timeout for complete generation
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "")
                logger.info(f"✅ Ollama generated {len(generated_text)} chars")
                
                # Debug: print first 200 chars
                if generated_text:
                    logger.info(f"Preview: {generated_text[:200]}...")
                else:
                    logger.warning("Ollama returned empty response")
                
                return generated_text
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return ""
    
    def generate_code(self, task: str, user_level: str = None) -> str:
        """Generate Python code with meta-prompting based on user level"""
        
        # Use provided level or detect from task
        if not user_level:
            user_level = self._detect_user_level(task)
        
        logger.info(f"📊 Generating {user_level} level code")
        
        # For beginner level, try multiple times to get simple code
        max_attempts = 3 if user_level.lower() == 'beginner' else 1
        
        for attempt in range(max_attempts):
            # Create meta-prompt based on level
            prompt = self._create_meta_prompt(task, user_level)
            
            generated = self.generate(prompt, max_tokens=1000)
            
            # Extract code from response
            code = self._extract_code(generated)
            
            if not code:
                logger.warning(f"⚠️ Attempt {attempt + 1}: No code extracted from Ollama response")
                continue
            
            # For beginner level, enforce simplicity
            if user_level.lower() == 'beginner':
                validated_code = self._enforce_beginner_simplicity(code)
                if validated_code:
                    logger.info(f"✅ Beginner code validated on attempt {attempt + 1}")
                    return validated_code
                else:
                    logger.warning(f"⚠️ Attempt {attempt + 1}/{max_attempts}: Code rejected (has functions/classes or too long)")
                    if attempt < max_attempts - 1:
                        continue  # Try again
                    else:
                        # Last attempt - try to simplify the complex code
                        logger.warning("⚠️ All attempts generated complex code, attempting to simplify...")
                        simplified = self._simplify_to_beginner(code, task)
                        if simplified:
                            logger.info("✅ Successfully simplified complex code to beginner level")
                            return simplified
                        else:
                            logger.error("❌ Could not simplify code, returning original")
                            return code
            else:
                # Not beginner level
                return code
        
        logger.error("❌ All generation attempts failed")
        return ""
    
    def _enforce_beginner_simplicity(self, code: str) -> str:
        """Enforce beginner-level simplicity by removing complex constructs"""
        lines = code.split('\n')
        
        # Check if code has classes or functions - if so, reject it
        has_class = any('class ' in line for line in lines)
        has_function = any(line.strip().startswith('def ') for line in lines)
        
        # If code is too complex, return empty to trigger simplification
        if has_class or has_function:
            logger.warning("⚠️ Beginner code has class/function - needs simplification")
            return ""
        
        # Check line count
        non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        if len(non_empty_lines) > 20:
            logger.warning(f"⚠️ Beginner code too long ({len(non_empty_lines)} lines)")
            return ""
        
        return code
    
    def _simplify_to_beginner(self, complex_code: str, task: str) -> str:
        """Convert complex code to simple beginner-level code"""
        simplify_prompt = f"""The following code is TOO COMPLEX for a beginner. Simplify it to absolute beginner level.

Complex code:
```python
{complex_code}
```

Task: {task}

REQUIREMENTS FOR SIMPLIFIED CODE:
1. NO functions (remove all "def")
2. NO classes (remove all "class")
3. NO type hints
4. Just: input() -> calculate -> print()
5. Maximum 10 lines
6. Keep it EXTREMELY simple

Write the simplified beginner code:

```python"""
        
        try:
            simplified = self.generate(simplify_prompt, max_tokens=300)
            code = self._extract_code(simplified)
            
            # Validate it's actually simple now
            if code:
                validated = self._enforce_beginner_simplicity(code)
                if validated:
                    return validated
            
            logger.warning("⚠️ Simplification still produced complex code")
            return ""
            
        except Exception as e:
            logger.error(f"Simplification failed: {e}")
            return ""
    
    def generate_mermaid(self, code: str) -> str:
        """
        Generate Mermaid flowchart diagram from Python code
        
        Args:
            code: Python code to analyze and create diagram from
        
        Returns:
            Mermaid flowchart syntax
        """
        # Analyze code to extract key elements
        analysis = self._analyze_code_structure(code)
        
        prompt = f"""Convert this Python code to Mermaid flowchart syntax.

Python code:
```python
{code}
```

Output the Mermaid flowchart starting with "flowchart TD":

flowchart TD
    Start([Start])"""
        
        try:
            logger.info("🎨 Generating Mermaid diagram from code logic")
            
            # Use stricter parameters for Mermaid generation
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Low for structured output
                    "num_predict": 800,  # Increased for complex diagrams
                    "top_p": 0.9,
                    "top_k": 40,
                    "stop": ["Explanation:", "Note:", "This flowchart", "The above", "Here is"]  # Stop at explanations only
                }
            }
            
            logger.info(f"🤖 Calling Ollama with {self.model_name}")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=90
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return ""
            
            result = response.json()
            generated_text = result.get("response", "")
            
            if not generated_text:
                logger.warning("⚠️ Ollama returned empty Mermaid response")
                return ""
            
            logger.info(f"✅ Ollama generated {len(generated_text)} chars")
            logger.info(f"Raw Mermaid output: {generated_text[:300]}...")  # Log first 300 chars
            
            response = generated_text
            
            if response and len(response) > 20:
                # Clean and validate Mermaid syntax
                mermaid_code = response.strip()
                
                # First, try to extract from markdown code blocks
                if '```mermaid' in mermaid_code:
                    start = mermaid_code.find('```mermaid') + 10
                    end = mermaid_code.find('```', start)
                    if end > start:
                        mermaid_code = mermaid_code[start:end].strip()
                elif '```' in mermaid_code and 'flowchart' in mermaid_code:
                    # Generic code block with flowchart inside
                    start = mermaid_code.find('```') + 3
                    end = mermaid_code.find('```', start)
                    if end > start:
                        mermaid_code = mermaid_code[start:end].strip()
                
                # Remove leading explanatory text before flowchart
                if 'flowchart' in mermaid_code:
                    flowchart_pos = mermaid_code.find('flowchart')
                    if flowchart_pos > 0:
                        # Check if there's explanatory text before flowchart
                        before_text = mermaid_code[:flowchart_pos].strip()
                        if before_text and not before_text.endswith('```'):
                            # Remove everything before flowchart
                            mermaid_code = mermaid_code[flowchart_pos:]
                
                # Remove any trailing explanations after the Mermaid code
                explanation_markers = [
                    'Explanation:', 'Note:', 'This flowchart', 'This diagram',
                    'This is the', 'The flowchart', 'The diagram', 'In this',
                    'Here is', 'Above is', 'This Mermaid', 'This code',
                    'The above', 'As you can see'
                ]
                
                for marker in explanation_markers:
                    if marker in mermaid_code:
                        # Only split if marker appears after some Mermaid content
                        parts = mermaid_code.split(marker)
                        if '-->' in parts[0] or '---' in parts[0]:
                            mermaid_code = parts[0].strip()
                
                # Ensure it starts with flowchart
                if not mermaid_code.startswith('flowchart'):
                    if 'flowchart' in mermaid_code:
                        # Extract from flowchart onwards
                        flowchart_pos = mermaid_code.find('flowchart')
                        mermaid_code = mermaid_code[flowchart_pos:]
                    else:
                        mermaid_code = 'flowchart TD\n' + mermaid_code
                
                # Remove any trailing explanations (lines that don't look like Mermaid)
                lines = mermaid_code.split('\n')
                clean_lines = []
                found_flowchart = False
                
                for line in lines:
                    stripped = line.strip()
                    
                    # Track if we've found the flowchart declaration
                    if stripped.startswith('flowchart'):
                        found_flowchart = True
                        clean_lines.append(line)
                        continue
                    
                    # Skip lines before flowchart declaration
                    if not found_flowchart:
                        continue
                    
                    # Keep lines that look like Mermaid syntax
                    if (stripped and (
                        '-->' in stripped or 
                        '---' in stripped or
                        '==>' in stripped or
                        stripped.startswith(tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) or
                        '([' in stripped or  # Terminal nodes
                        '[' in stripped or   # Process nodes
                        '{' in stripped or   # Decision nodes
                        '(' in stripped or   # Various node types
                        not stripped)):      # Empty lines
                        clean_lines.append(line)
                    else:
                        # Stop at explanation text (sentences with spaces and no Mermaid syntax)
                        if len(stripped.split()) > 3 and '-->' not in stripped:
                            break
                
                mermaid_code = '\n'.join(clean_lines).strip()
                
                # Fix common Mermaid syntax errors
                mermaid_code = self._fix_mermaid_syntax(mermaid_code)
                
                # Basic validation - check for arrows
                if '-->' in mermaid_code or '---' in mermaid_code:
                    logger.info(f"✅ Generated clean Mermaid diagram ({len(mermaid_code)} chars)")
                    return mermaid_code
                else:
                    logger.warning("⚠️ Generated Mermaid missing flow arrows")
                    return ""
            else:
                logger.warning("⚠️ Ollama returned empty Mermaid response")
                return ""
                
        except Exception as e:
            logger.error(f"Mermaid generation error: {e}")
            return ""
    
    def _analyze_code_structure(self, code: str) -> dict:
        """Analyze code to extract key structural elements"""
        lines = code.split('\n')
        analysis = {
            'inputs': [],
            'operations': [],
            'conditions': [],
            'outputs': []
        }
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Detect inputs
            if 'input(' in stripped:
                # Extract variable name
                if '=' in stripped:
                    var_name = stripped.split('=')[0].strip()
                    analysis['inputs'].append(var_name)
                else:
                    analysis['inputs'].append('user_input')
            
            # Detect operations (assignments with calculations)
            elif '=' in stripped and 'input(' not in stripped and 'def ' not in stripped:
                # Extract variable and operation
                parts = stripped.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    operation = parts[1].strip()
                    # Skip if it's just a simple assignment without calculation
                    if any(op in operation for op in ['+', '-', '*', '/', '%', '//']):
                        analysis['operations'].append(f"{var_name} = {operation}")
            
            # Detect conditions
            elif stripped.startswith('if ') or stripped.startswith('elif '):
                condition = stripped.replace('if ', '').replace('elif ', '').replace(':', '').strip()
                analysis['conditions'].append(condition)
            
            # Detect outputs
            elif 'print(' in stripped:
                # Extract what's being printed
                start = stripped.find('print(') + 6
                end = stripped.rfind(')')
                if end > start:
                    print_content = stripped[start:end]
                    analysis['outputs'].append(print_content)
            
            # Detect return statements
            elif stripped.startswith('return '):
                return_val = stripped.replace('return ', '').strip()
                analysis['outputs'].append(f"return {return_val}")
        
        # If no specific elements found, provide generic description
        if not any(analysis.values()):
            analysis['operations'].append('process data')
        
        return analysis
    
    def _fix_mermaid_syntax(self, mermaid_code: str) -> str:
        """Fix common Mermaid syntax errors"""
        lines = mermaid_code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip flowchart declaration
            if line.strip().startswith('flowchart'):
                fixed_lines.append(line)
                continue
            
            # Fix decision nodes: single braces to double braces
            # Pattern: {condition} -> {{condition}}
            if '{' in line and not '{{' in line:
                # Replace single braces with double braces for decision nodes
                line = line.replace('{', '{{').replace('}', '}}')
            
            # Fix node definitions with spaces in IDs and special characters
            if '-->' in line or '---' in line:
                # Split by arrow
                parts = line.split('-->') if '-->' in line else line.split('---')
                fixed_parts = []
                
                for part in parts:
                    part = part.strip()
                    
                    # Handle edge labels like |Yes| or |No|
                    if part.startswith('|') and part.endswith('|'):
                        fixed_parts.append(part)
                        continue
                    
                    # If part has a node definition with label
                    if '[' in part or '{' in part or '(' in part:
                        # Find the node ID (before the bracket)
                        bracket_chars = ['[', '{', '(']
                        bracket_pos = len(part)
                        for char in bracket_chars:
                            if char in part:
                                pos = part.find(char)
                                if pos < bracket_pos:
                                    bracket_pos = pos
                        
                        if bracket_pos < len(part):
                            node_id = part[:bracket_pos].strip()
                            node_def = part[bracket_pos:]
                            
                            # Remove spaces from node ID
                            node_id_fixed = node_id.replace(' ', '')
                            
                            # Fix special characters in node labels
                            # Remove parentheses from conditions in decision nodes
                            if '{{' in node_def and '}}' in node_def:
                                # Extract condition
                                start = node_def.find('{{') + 2
                                end = node_def.find('}}')
                                if end > start:
                                    condition = node_def[start:end]
                                    # Remove parentheses and simplify
                                    condition_fixed = condition.replace('(', '').replace(')', '')
                                    # Replace operators that might cause issues
                                    condition_fixed = condition_fixed.replace('>=', ' gte ').replace('<=', ' lte ')
                                    condition_fixed = condition_fixed.replace('==', ' eq ').replace('!=', ' ne ')
                                    node_def = '{{' + condition_fixed + '}}'
                            
                            fixed_parts.append(node_id_fixed + node_def)
                        else:
                            fixed_parts.append(part.replace(' ', ''))
                    else:
                        # Just a node ID reference, remove spaces
                        fixed_parts.append(part.replace(' ', ''))
                
                # Reconstruct line
                arrow = ' --> ' if '-->' in line else ' --- '
                fixed_line = arrow.join(fixed_parts)
                fixed_lines.append('    ' + fixed_line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _detect_user_level(self, task: str) -> str:
        """Detect user level from task description - defaults to intermediate"""
        task_lower = task.lower()
        
        # Check for explicit level keywords
        if any(word in task_lower for word in ['advanced', 'professional', 'production', 'complex', 'oop', 'class-based', 'enterprise']):
            return 'advanced'
        
        if any(word in task_lower for word in ['beginner', 'simple', 'basic', 'easy', 'learning', 'tutorial']):
            return 'beginner'
        
        # Default to intermediate when no level specified
        return 'intermediate'
    
    def _create_meta_prompt(self, task: str, user_level: str) -> str:
        """Create meta-prompt based on user level"""
        
        if user_level == 'beginner':
            return f"""You are writing code for an absolute beginner who just started learning Python TODAY.

CRITICAL - THESE ARE FORBIDDEN:
❌ NO "def" keyword anywhere
❌ NO "class" keyword anywhere
❌ NO functions of any kind
❌ NO classes of any kind
❌ NO type hints (no ":")
❌ NO complex logic

REQUIRED STRUCTURE (copy this pattern):
1. Get input with input()
2. Do ONE calculation
3. Print result with print()
4. Maximum 8 lines total

CORRECT EXAMPLE for "check if even":
num = int(input("Enter number: "))
if num % 2 == 0:
    print("Even")
else:
    print("Odd")

WRONG EXAMPLE (DO NOT DO THIS):
def is_even(num):  # ❌ NO FUNCTIONS!
    return num % 2 == 0

Task: {task}

Write ONLY the simplest possible code (NO functions, NO classes):

```python"""

        elif user_level == 'intermediate':
            return f"""You are writing intermediate Python code.

RULES:
- Use 1-2 simple functions with docstrings
- Add try-except for input validation
- NO classes
- NO menus or while loops
- Keep under 30 lines
- Make it interactive with input() and print()

Task: {task}

Write intermediate Python code:

```python"""

        else:  # advanced
            return f"""You are writing advanced Python code.

RULES:
- Use class-based design with proper OOP
- Add type hints from typing module
- Create interactive menu (run, stats, quit)
- Track statistics in class attributes
- Professional structure with docstrings
- Use if __name__ == "__main__"

Task: {task}

Write advanced Python code:

```python"""
    
    def _extract_code(self, text: str) -> str:
        """Extract Python code from generated text"""
        if not text:
            return ""
        
        # Remove markdown code blocks if present
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            if end != -1:
                code = text[start:end].strip()
            else:
                code = text[start:].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end != -1:
                code = text[start:end].strip()
            else:
                code = text[start:].strip()
        else:
            # No markdown, use the text as-is
            code = text.strip()
        
        # Clean up - remove leading explanatory text before code starts
        lines = code.split('\n')
        cleaned = []
        code_started = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip explanatory text at the beginning
            if not code_started:
                # Look for code indicators
                if (stripped.startswith(('import ', 'from ', 'def ', 'class ', '#')) or 
                    'def ' in stripped or 'class ' in stripped or 'import ' in stripped):
                    code_started = True
                    cleaned.append(line)
                # Skip explanatory lines
                elif stripped.startswith(('Here', 'This code', 'The above', 'Note:', 'Example:', 'Output:', 'Sure,')):
                    continue
                elif stripped.startswith(('Generate', 'REQUIREMENTS', 'Write', 'Requirements:')):
                    continue
                elif not stripped:  # Empty line before code starts
                    continue
                else:
                    # Might be code without def/class/import, include it
                    cleaned.append(line)
                    code_started = True
            else:
                # Once code started, include everything
                cleaned.append(line)
        
        # If no code found with the above method, try to find any Python-like content
        if not cleaned:
            for i, line in enumerate(lines):
                if 'def ' in line or 'import ' in line or 'class ' in line or '=' in line:
                    # Found code, take everything from here
                    cleaned = lines[i:]
                    break
        
        # Remove leading/trailing empty lines
        while cleaned and not cleaned[0].strip():
            cleaned.pop(0)
        while cleaned and not cleaned[-1].strip():
            cleaned.pop()
        
        result = '\n'.join(cleaned).strip()
        
        # If still empty or too short, return empty
        if not result or len(result) < 15:
            return ""
        
        return result


# Test function
if __name__ == "__main__":
    import sys
    import logging
    
    # Enable logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    service = OllamaService()
    
    if service.is_available():
        print("✅ Ollama is running!\n")
        
        # Test generation
        print("Testing code generation...")
        try:
            code = service.generate_code("linear search")
            
            if code:
                print("✅ Code generated successfully!\n")
                print("=" * 60)
                print(code)
                print("=" * 60)
            else:
                print("❌ Generated code is empty")
                
        except Exception as e:
            print(f"❌ Error during generation: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Ollama is not running")
        print("Start it with: ollama serve")
