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
        Generate Mermaid flowchart diagram from Python code using code analysis

        Args:
            code: Python code to analyze and create diagram from

        Returns:
            Mermaid flowchart syntax
        """
        try:
            logger.info("🎨 Generating Mermaid diagram from code analysis")

            # Analyze code structure with proper flow tracking
            analysis = self._analyze_code_structure(code)

            # Build Mermaid diagram from flow analysis
            mermaid_lines = ["flowchart TD"]
            mermaid_lines.append("    Start([Start])")

            node_counter = 1
            prev_node = "Start"
            condition_index = 0

            # Process flow sequentially to maintain logic order
            for flow_item in analysis['flow']:
                flow_type = flow_item['type']
                content = flow_item['content']

                if flow_type == 'input':
                    # Input node
                    node_id = f"Input{node_counter}"
                    inp_display = self._clean_display_text(content)
                    mermaid_lines.append(f"    {prev_node} --> {node_id}[\"Get {inp_display}\"]")
                    prev_node = node_id
                    node_counter += 1

                elif flow_type == 'operation':
                    # Operation node
                    node_id = f"Op{node_counter}"
                    op_display = content.replace('=', ':').strip()
                    op_display = self._clean_display_text(op_display)
                    if len(op_display) > 35:
                        op_display = op_display[:32] + "..."
                    mermaid_lines.append(f"    {prev_node} --> {node_id}[\"{op_display}\"]")
                    prev_node = node_id
                    node_counter += 1

                elif flow_type == 'condition':
                    # Decision node with branches
                    if condition_index < len(analysis['conditions']):
                        cond_data = analysis['conditions'][condition_index]
                        check_node = f"Check{node_counter}"
                        cond_display = self._clean_display_text(content)
                        if len(cond_display) > 25:
                            cond_display = cond_display[:22] + "..."

                        # Add decision node
                        mermaid_lines.append(f"    {prev_node} --> {check_node}{{{{{cond_display}}}}}")

                        # Process true branch
                        true_node = f"True{node_counter}"
                        if cond_data['true_branch']:
                            # Show actual operations in true branch
                            true_content = cond_data['true_branch'][0]
                            true_display = self._clean_display_text(true_content)
                            if len(true_display) > 30:
                                true_display = true_display[:27] + "..."
                            mermaid_lines.append(f"    {check_node} -->|Yes| {true_node}[\"{true_display}\"]")
                        else:
                            mermaid_lines.append(f"    {check_node} -->|Yes| {true_node}[\"True Path\"]")

                        # Process false branch
                        false_node = f"False{node_counter}"
                        if cond_data['false_branch']:
                            # Show actual operations in false branch
                            false_content = cond_data['false_branch'][0]
                            false_display = self._clean_display_text(false_content)
                            if len(false_display) > 30:
                                false_display = false_display[:27] + "..."
                            mermaid_lines.append(f"    {check_node} -->|No| {false_node}[\"{false_display}\"]")
                        else:
                            mermaid_lines.append(f"    {check_node} -->|No| {false_node}[\"False Path\"]")

                        # Merge branches
                        merge_node = f"Merge{node_counter}"
                        mermaid_lines.append(f"    {true_node} --> {merge_node}[Continue]")
                        mermaid_lines.append(f"    {false_node} --> {merge_node}")

                        prev_node = merge_node
                        node_counter += 1
                        condition_index += 1

                elif flow_type == 'output':
                    # Output node
                    node_id = f"Output{node_counter}"
                    out_display = self._clean_display_text(content)
                    if len(out_display) > 30:
                        out_display = out_display[:27] + "..."
                    mermaid_lines.append(f"    {prev_node} --> {node_id}[\"{out_display}\"]")
                    prev_node = node_id
                    node_counter += 1

                elif flow_type == 'return':
                    # Return node
                    node_id = f"Return{node_counter}"
                    ret_display = self._clean_display_text(content)
                    if len(ret_display) > 30:
                        ret_display = ret_display[:27] + "..."
                    mermaid_lines.append(f"    {prev_node} --> {node_id}[\"return {ret_display}\"]")
                    prev_node = node_id
                    node_counter += 1

            # Add final end node
            mermaid_lines.append(f"    {prev_node} --> End([End])")

            mermaid_code = '\n'.join(mermaid_lines)

            # Fix any syntax issues
            mermaid_code = self._fix_mermaid_syntax(mermaid_code)

            logger.info(f"✅ Generated Mermaid diagram from code analysis ({len(mermaid_code)} chars)")
            return mermaid_code

        except Exception as e:
            logger.error(f"Mermaid generation error: {e}")
            # Return simple fallback
            return """flowchart TD
    Start([Start])
    Start --> Process[Process Code]
    Process --> End([End])"""

    
    def _analyze_code_structure(self, code: str) -> dict:
        """Analyze code to extract key structural elements with proper flow tracking"""
        lines = code.split('\n')
        analysis = {
            'inputs': [],
            'operations': [],
            'conditions': [],
            'outputs': [],
            'flow': []  # Track sequential flow of operations
        }
        
        indent_stack = []  # Track indentation levels for nested structures
        current_condition = None
        in_true_branch = False
        in_false_branch = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Calculate indentation level
            indent = len(line) - len(line.lstrip())
            
            # Detect inputs
            if 'input(' in stripped:
                if '=' in stripped:
                    var_name = stripped.split('=')[0].strip()
                    analysis['inputs'].append(var_name)
                    analysis['flow'].append({'type': 'input', 'content': var_name, 'indent': indent})
                else:
                    analysis['inputs'].append('user_input')
                    analysis['flow'].append({'type': 'input', 'content': 'user_input', 'indent': indent})
            
            # Detect conditions
            elif stripped.startswith('if ') or stripped.startswith('elif '):
                condition = stripped.replace('if ', '').replace('elif ', '').replace(':', '').strip()
                analysis['conditions'].append({
                    'condition': condition,
                    'true_branch': [],
                    'false_branch': [],
                    'indent': indent
                })
                analysis['flow'].append({'type': 'condition', 'content': condition, 'indent': indent})
                current_condition = len(analysis['conditions']) - 1
                in_true_branch = True
                in_false_branch = False
            
            # Detect else
            elif stripped.startswith('else:'):
                if current_condition is not None:
                    in_true_branch = False
                    in_false_branch = True
                # Don't add else to flow - it's handled by the condition branching
            
            # Detect operations (assignments with calculations)
            elif '=' in stripped and 'input(' not in stripped and 'def ' not in stripped and 'class ' not in stripped:
                parts = stripped.split('=', 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    operation = parts[1].strip()
                    
                    op_info = f"{var_name} = {operation}"
                    
                    # Add to appropriate branch if inside condition
                    if current_condition is not None and indent > analysis['conditions'][current_condition]['indent']:
                        if in_true_branch:
                            analysis['conditions'][current_condition]['true_branch'].append(op_info)
                        elif in_false_branch:
                            analysis['conditions'][current_condition]['false_branch'].append(op_info)
                    else:
                        # Not in a condition, add to main operations
                        if any(op in operation for op in ['+', '-', '*', '/', '%', '//', '**']):
                            analysis['operations'].append(op_info)
                        analysis['flow'].append({'type': 'operation', 'content': op_info, 'indent': indent})
                        # Reset condition tracking if we're back at base indent
                        if current_condition is not None and indent <= analysis['conditions'][current_condition]['indent']:
                            current_condition = None
                            in_true_branch = False
                            in_false_branch = False
            
            # Detect outputs
            elif 'print(' in stripped:
                start = stripped.find('print(') + 6
                end = stripped.rfind(')')
                if end > start:
                    print_content = stripped[start:end]
                    
                    # Add to appropriate branch if inside condition
                    if current_condition is not None and indent > analysis['conditions'][current_condition]['indent']:
                        if in_true_branch:
                            analysis['conditions'][current_condition]['true_branch'].append(f"print {print_content}")
                        elif in_false_branch:
                            analysis['conditions'][current_condition]['false_branch'].append(f"print {print_content}")
                    else:
                        analysis['outputs'].append(print_content)
                        analysis['flow'].append({'type': 'output', 'content': print_content, 'indent': indent})
                        # Reset condition tracking
                        if current_condition is not None and indent <= analysis['conditions'][current_condition]['indent']:
                            current_condition = None
                            in_true_branch = False
                            in_false_branch = False
            
            # Detect return statements
            elif stripped.startswith('return '):
                return_val = stripped.replace('return ', '').strip()
                
                # Add to appropriate branch if inside condition
                if current_condition is not None and indent > analysis['conditions'][current_condition]['indent']:
                    if in_true_branch:
                        analysis['conditions'][current_condition]['true_branch'].append(f"return {return_val}")
                    elif in_false_branch:
                        analysis['conditions'][current_condition]['false_branch'].append(f"return {return_val}")
                else:
                    analysis['outputs'].append(f"return {return_val}")
                    analysis['flow'].append({'type': 'return', 'content': return_val, 'indent': indent})
        
        # If no specific elements found, provide generic description
        if not any([analysis['inputs'], analysis['operations'], analysis['conditions'], analysis['outputs']]):
            analysis['operations'].append('process data')
            analysis['flow'].append({'type': 'operation', 'content': 'process data', 'indent': 0})
        
        return analysis
    
    def _clean_display_text(self, text: str) -> str:
        """Clean text for Mermaid display by removing special characters"""
        text = text.replace('[', '').replace(']', '')
        text = text.replace('{', '').replace('}', '')
        text = text.replace('(', '').replace(')', '')
        text = text.replace('^', '').replace('$', '')
        text = text.replace('+', 'plus').replace('*', 'times')
        text = text.replace('@', 'at').replace('#', 'hash')
        text = text.replace('|', 'or').replace('&', 'and')
        text = text.replace('<', 'lt').replace('>', 'gt')
        text = text.replace('"', '').replace("'", '')
        text = text.replace('\\n', ' ').replace('\\t', ' ')
        return text
    
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
        
        if user_level.lower() == 'beginner':
            return f"""BEGINNER LEVEL - Write the SIMPLEST possible Python code.

Task: {task}

STRICT RULES:
- NO def (no functions)
- NO class (no classes)  
- NO type hints
- NO imports (unless absolutely required)
- Maximum 10 lines
- Use only: input(), print(), if/else, basic math

EXAMPLE for "add two numbers":
a = int(input("First number: "))
b = int(input("Second number: "))
result = a + b
print("Sum:", result)

Now write BEGINNER code for: {task}

```python"""

        elif user_level.lower() == 'intermediate':
            return f"""INTERMEDIATE LEVEL - Write clean, functional Python code.

Task: {task}

REQUIREMENTS:
- Use 1-2 functions with docstrings
- Add error handling (try/except)
- NO classes
- NO complex menus
- 15-30 lines
- Interactive with input/output

EXAMPLE for "add two numbers":
def add_numbers():
    \"\"\"Add two numbers with validation\"\"\"
    try:
        a = float(input("First number: "))
        b = float(input("Second number: "))
        result = a + b
        print(f"Sum: {{result}}")
    except ValueError:
        print("Error: Invalid input")

if __name__ == "__main__":
    add_numbers()

Now write INTERMEDIATE code for: {task}

```python"""

        else:  # advanced
            return f"""ADVANCED LEVEL - Write professional, production-ready Python code.

Task: {task}

REQUIREMENTS:
- Class-based OOP design
- Type hints (from typing import ...)
- Interactive menu system
- Statistics tracking
- Comprehensive docstrings
- Error handling
- if __name__ == "__main__" guard

EXAMPLE for "add two numbers":
from typing import List

class Calculator:
    \"\"\"Professional calculator with history\"\"\"
    
    def __init__(self):
        self.history: List[str] = []
    
    def add(self, a: float, b: float) -> float:
        \"\"\"Add two numbers and track history\"\"\"
        result = a + b
        self.history.append(f"{{a}} + {{b}} = {{result}}")
        return result
    
    def show_history(self):
        \"\"\"Display calculation history\"\"\"
        print("\\nHistory:")
        for calc in self.history:
            print(f"  {{calc}}")

if __name__ == "__main__":
    calc = Calculator()
    while True:
        print("\\n1. Add  2. History  3. Quit")
        choice = input("Choose: ")
        if choice == '1':
            try:
                a = float(input("First: "))
                b = float(input("Second: "))
                print(f"Result: {{calc.add(a, b)}}")
            except ValueError:
                print("Invalid input")
        elif choice == '2':
            calc.show_history()
        elif choice == '3':
            break

Now write ADVANCED code for: {task}

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
