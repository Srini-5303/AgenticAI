import subprocess
import tempfile
import os
import ast
import json
from typing import Dict, List
from utils.logger import setup_logger


class DebuggerAgent:
    """
    Agent 4: Validates generated code through:
    1. JSON parsing validation (checks if coder output is valid)
    2. Syntax checking (AST parsing)
    3. Static analysis (import checking, basic linting)
    4. Runtime execution testing
    """

    def __init__(self):
        self.logger = setup_logger("DebuggerAgent", "debugger.log")

    def run(self, code, raw_coder_output=None) -> Dict:
        """
        code: CodeOutput (Pydantic) or None if parsing failed
        raw_coder_output: Raw string output from coder (for JSON validation)
        Returns: {
            "correct": bool,
            "errors": List[Dict] (if any)
        }
        """
        self.logger.info("Starting code validation")
        errors = []
        
        # Step 0: Validate JSON parsing if raw output provided
        if raw_coder_output:
            self.logger.debug("Checking JSON parsing")
            json_errors = self._check_json_parsing(raw_coder_output)
            errors.extend(json_errors)
            if json_errors:
                self.logger.error(f"JSON parsing failed with {len(json_errors)} error(s)")
                return {
                    "correct": False,
                    "errors": errors,
                    "stage": "json_parsing"
                }
            self.logger.debug("JSON parsing successful")
        
        # If code is None, return early
        if code is None:
            self.logger.error("Code object is None - invalid output from coder")
            errors.append({
                "error_type": "InvalidOutput",
                "error": "Coder produced invalid or unparseable output",
                "suggestion": "Generate valid JSON with 'files' key containing Python files"
            })
            return {
                "correct": False,
                "errors": errors,
                "stage": "code_validation"
            }
        
        files = code.files
        self.logger.info(f"Validating {len(files)} file(s): {list(files.keys())}")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            self.logger.debug(f"Created temporary directory: {tmpdir}")
            
            # Write files temporarily
            for fname, content in files.items():
                path = os.path.join(tmpdir, fname)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.logger.debug(f"Written file: {fname} ({len(content)} chars)")

            # Step 1: Syntax check ALL files
            self.logger.info("Step 1: Checking syntax")
            syntax_errors = self._check_syntax(files)
            errors.extend(syntax_errors)

            # If syntax errors exist, don't bother executing
            if syntax_errors:
                self.logger.error(f"Syntax check failed with {len(syntax_errors)} error(s)")
                for err in syntax_errors:
                    self.logger.error(f"  - {err['file']}:{err.get('line', '?')} {err['error_type']}: {err['error']}")
                return {
                    "correct": False,
                    "errors": errors,
                    "stage": "syntax_check"
                }
            self.logger.info("Syntax check passed")

            # Step 2: Check imports
            self.logger.info("Step 2: Checking imports")
            import_errors = self._check_imports(files, tmpdir)
            errors.extend(import_errors)
            
            if import_errors:
                self.logger.warning(f"Found {len(import_errors)} import issue(s)")
                for err in import_errors:
                    self.logger.warning(f"  - {err['file']}: {err['error']}")
            else:
                self.logger.info("Import check passed")

            # Step 3: Try executing main file
            self.logger.info("Step 3: Attempting code execution")
            main_file = self._find_entry_file(files)
            
            if main_file:
                self.logger.info(f"Entry point identified: {main_file}")
                exec_errors = self._execute_code(tmpdir, main_file)
                errors.extend(exec_errors)
                
                if exec_errors:
                    self.logger.error(f"Execution failed with {len(exec_errors)} error(s)")
                    for err in exec_errors:
                        self.logger.error(f"  - {err['error_type']}: {err['error']}")
                else:
                    self.logger.info("Execution test passed")
            else:
                self.logger.warning("No entry point found, skipping execution test")

        if errors:
            self.logger.error(f"Validation FAILED with {len(errors)} total error(s)")
            return {
                "correct": False,
                "errors": errors
            }

        self.logger.info("All validation checks PASSED")
        return {
            "correct": True,
            "message": "All validation checks passed"
        }

    # ==================== Validation Methods ====================

    def _check_json_parsing(self, raw_output: str) -> List[Dict]:
        """
        Validate if the coder's raw output is valid JSON
        """
        errors = []
        
        try:
            cleaned = raw_output.strip()
            
            # Remove markdown code fences if present
            if cleaned.startswith("```"):
                self.logger.debug("Removing markdown code fences")
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:-1]) if len(lines) > 2 else cleaned
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
            
            json.loads(cleaned)
            self.logger.debug("JSON structure is valid")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e.msg} at line {e.lineno}, col {e.colno}")
            errors.append({
                "error_type": "JSONDecodeError",
                "error": f"Invalid JSON output: {e.msg} at line {e.lineno}, column {e.colno}",
                "suggestion": "Ensure output is valid JSON format with proper quotes and brackets. Do not include any text outside the JSON structure."
            })
        except Exception as e:
            self.logger.error(f"Unexpected parsing error: {str(e)}")
            errors.append({
                "error_type": "ParseError",
                "error": f"Failed to parse output: {str(e)}",
                "suggestion": "Generate valid JSON with 'files' key"
            })
        
        return errors

    def _check_syntax(self, files: Dict[str, str]) -> List[Dict]:
        """
        Parse each Python file using AST to catch syntax errors.
        """
        errors = []
        
        for fname, content in files.items():
            if not fname.endswith('.py'):
                self.logger.debug(f"Skipping non-Python file: {fname}")
                continue
            
            self.logger.debug(f"Parsing {fname} with AST")
            try:
                ast.parse(content)
                self.logger.debug(f"{fname} syntax is valid")
            except SyntaxError as e:
                self.logger.error(f"Syntax error in {fname} at line {e.lineno}: {e.msg}")
                errors.append({
                    "file": fname,
                    "line": e.lineno,
                    "error_type": "SyntaxError",
                    "error": f"{e.msg} at line {e.lineno}",
                    "traceback": str(e)
                })
            except Exception as e:
                self.logger.error(f"Failed to parse {fname}: {str(e)}")
                errors.append({
                    "file": fname,
                    "error_type": "ParseError",
                    "error": f"Failed to parse: {str(e)}",
                    "traceback": str(e)
                })
        
        return errors

    def _check_imports(self, files: Dict[str, str], tmpdir: str) -> List[Dict]:
        """
        Check if all imports can be resolved.
        This catches missing standard library or third-party imports.
        """
        errors = []
        
        for fname, content in files.items():
            if not fname.endswith('.py'):
                continue
            
            try:
                tree = ast.parse(content)
                imports_found = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports_found.append(alias.name)
                            if not self._can_import(alias.name, tmpdir):
                                self.logger.warning(f"{fname}: Cannot import '{alias.name}'")
                                errors.append({
                                    "file": fname,
                                    "error_type": "ImportError",
                                    "error": f"Cannot import '{alias.name}' - module not available",
                                    "suggestion": "Remove this import or ensure it's a standard library module"
                                })
                    
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module
                        if module:
                            imports_found.append(module)
                            if not self._can_import(module, tmpdir):
                                self.logger.warning(f"{fname}: Cannot import from '{module}'")
                                errors.append({
                                    "file": fname,
                                    "error_type": "ImportError",
                                    "error": f"Cannot import from '{module}' - module not available",
                                    "suggestion": "Use only standard library modules"
                                })
                
                if imports_found:
                    self.logger.debug(f"{fname} imports: {', '.join(set(imports_found))}")
                            
            except Exception as e:
                # Skip import checking if AST parsing fails
                self.logger.debug(f"Skipping import check for {fname} due to parse error")
                pass
        
        return errors

    def _can_import(self, module_name: str, tmpdir: str) -> bool:
        """
        Check if a module can be imported.
        Allows standard library and local files.
        """
        # Standard library and common built-ins
        stdlib_modules = {
            'os', 'sys', 'json', 'math', 'random', 'datetime', 'time',
            'collections', 're', 'itertools', 'functools', 'pathlib',
            'typing', 'dataclasses', 'enum', 'abc', 'copy', 'io'
        }
        
        base_module = module_name.split('.')[0]
        
        if base_module in stdlib_modules:
            return True
        
        # Check if it's a local file
        if os.path.exists(os.path.join(tmpdir, f"{module_name}.py")):
            return True
        
        return False

    def _execute_code(self, tmpdir: str, main_file: str) -> List[Dict]:
        """
        Execute the main file and capture errors.
        """
        errors = []
        
        self.logger.debug(f"Executing {main_file} in {tmpdir}")
        
        main_path = os.path.join(tmpdir, main_file)
        with open(main_path, "r", encoding="utf-8") as f:
            code_content = f.read()
            self.logger.debug(f"Main file content (first 200 chars): {code_content[:200]}")

            if "input(" in code_content:
                self.logger.warning("Code contains input() calls which may cause execution to hang")
                return []

        try:
            result = subprocess.run(
                ["python", main_file],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=5,
                input=""  # Provide empty stdin to avoid hanging
            )

            if result.returncode != 0:
                self.logger.error(f"Execution failed with return code {result.returncode}")
                # Parse the error to provide better feedback
                stderr = result.stderr.strip()
                error_info = self._parse_execution_error(stderr, main_file)
                errors.append(error_info)
            else:
                self.logger.info(f"Execution successful (return code 0)")
                # Execution succeeded, but check for warnings
                if result.stderr:
                    self.logger.warning(f"Execution had warnings: {result.stderr[:200]}")
                if result.stdout:
                    self.logger.debug(f"Execution output: {result.stdout[:200]}")

        except subprocess.TimeoutExpired:
            self.logger.error("Code execution timed out after 5 seconds")
            errors.append({
                "file": main_file,
                "error_type": "TimeoutError",
                "error": "Code execution timed out after 5 seconds",
                "suggestion": "Check for infinite loops or blocking input() calls"
            })
        except Exception as e:
            self.logger.error(f"Unexpected execution error: {str(e)}")
            errors.append({
                "file": main_file,
                "error_type": "RuntimeError",
                "error": str(e),
                "traceback": ""
            })
        
        return errors

    def _parse_execution_error(self, stderr: str, filename: str) -> Dict:
        """
        Parse stderr to extract useful error information.
        """
        self.logger.debug(f"Parsing execution error from stderr")
        lines = stderr.split('\n')
        
        # Try to extract error type and message
        error_type = "ExecutionError"
        error_msg = stderr
        line_num = None
        
        for line in reversed(lines):
            if ':' in line and any(err in line for err in ['Error', 'Exception']):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    error_type = parts[0].strip()
                    error_msg = parts[1].strip()
                break
        
        # Try to find line number
        for line in lines:
            if 'File' in line and 'line' in line:
                try:
                    line_num = int(line.split('line')[1].split(',')[0].strip())
                except:
                    pass
        
        result = {
            "file": filename,
            "error_type": error_type,
            "error": error_msg,
            "traceback": stderr
        }
        
        if line_num:
            result["line"] = line_num
            self.logger.debug(f"Error identified: {error_type} at line {line_num}")
        else:
            self.logger.debug(f"Error identified: {error_type}")
        
        return result

    def _find_entry_file(self, files: Dict[str, str]) -> str:
        """
        Find the main entry point file.
        Priority: main.py > app.py > any file with if __name__ == "__main__"
        """
        # Check for common entry point names
        for candidate in ["main.py", "app.py", "run.py"]:
            if candidate in files:
                self.logger.debug(f"Entry point found by convention: {candidate}")
                return candidate
        
        # Look for file with __main__ block
        for fname, content in files.items():
            if not fname.endswith('.py'):
                continue
            if 'if __name__ == "__main__"' in content or "if __name__ == '__main__'" in content:
                self.logger.debug(f"Entry point found by __main__ check: {fname}")
                return fname
        
        # Fallback: return first .py file
        for fname in files:
            if fname.endswith('.py'):
                self.logger.debug(f"Entry point fallback to first .py file: {fname}")
                return fname
        
        self.logger.warning("No entry point file found")
        return None