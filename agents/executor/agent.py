# import requests
# from utils.logger import setup_logger


# class ExecutorAgent:
#     """
#     Agent 5: Executes code using Piston API (open source)
#     """
    
#     PISTON_URL = "https://emkc.org/api/v2/piston"

#     def __init__(self):
#         self.logger = setup_logger("ExecutorAgent", "executor.log")

    
#     def run(self, code) -> dict:
#         """
#         code: CodeOutput (Pydantic)
#         Returns: {
#             "success": bool,
#             "stdout": str,
#             "stderr": str
#         }
#         """
#         main_file = self._find_main_file(code.files)
        
#         if not main_file:
#             return {
#                 "success": False,
#                 "error": "No main file found to execute"
#             }
        
#         source_code = code.files[main_file]
        
#         # Collect user input
#         print("\n" + "="*50)
#         print("Enter inputs for your program :")
#         print("="*50)
        
#         user_input_lines = []
#         try:
#             while True:
#                 line = input()
#                 if line.strip().upper() == 'DONE':
#                     break

#                 user_input_lines.append(line)
#         except EOFError:
#             pass
        
#         stdin = "\n".join(user_input_lines)
        
#         return self._execute_with_piston(source_code, stdin)
    
#     def _execute_with_piston(self, source_code: str, stdin: str) -> dict:
#         """Execute code using Piston API"""
        
#         payload = {
#             "language": "python",
#             "version": "3.10.0",
#             "files": [
#                 {
#                     "content": source_code
#                 }
#             ],
#             "stdin": stdin
#         }
        
#         try:
#             response = requests.post(
#                 f"{self.PISTON_URL}/execute",
#                 json=payload,
#                 timeout=10
#             )
#             result = response.json()

#             exit_code = result.get("run", {}).get("code", 1)
#             self.logger.info(f"Execution completed with code: {exit_code}")

#             output = result.get("run", {}).get("output", "")

            
#             print("EXECUTION OUTPUT:")
#             print(output)
            
#             return {
#                 "success": result.get("run", {}).get("code", 1) == 0,
#                 "stdout": result.get("run", {}).get("stdout", ""),
#                 "stderr": result.get("run", {}).get("stderr", ""),
#                 "output": output
#             }
            
#         except Exception as e:
#             return {
#                 "success": False,
#                 "error": str(e)
#             }
    
#     def _find_main_file(self, files: dict) -> str:
#         """Find the main entry point file"""
#         for candidate in ["main.py", "app.py", "run.py"]:
#             if candidate in files:
#                 return candidate
        
#         for fname, content in files.items():
#             if not fname.endswith('.py'):
#                 continue
#             if 'if __name__ == "__main__"' in content:
#                 return fname
        
#         for fname in files:
#             if fname.endswith('.py'):
#                 return fname
        
#         return None

import subprocess
import tempfile
import os
from pathlib import Path
from utils.logger import setup_logger


class ExecutorAgent:
    """
    Agent 5: Executes code locally using subprocess
    """
    
    def __init__(self):
        self.logger = setup_logger("ExecutorAgent", "executor.log")
    
    def run(self, code) -> dict:
        """
        code: CodeOutput (Pydantic)
        Returns: {
            "success": bool,
            "stdout": str,
            "stderr": str
        }
        """
        self.logger.info("Starting code execution")
        
        main_file = self._find_main_file(code.files)
        
        if not main_file:
            self.logger.error("No main file found")
            return {
                "success": False,
                "error": "No main file found to execute"
            }
        
        self.logger.info(f"Executing: {main_file}")
        source_code = code.files[main_file]

        print("\n" + "="*50)
        print("GENERATED CODE:")
        print(source_code)
        print("="*50)
        
        # Collect user input
        print("\n" + "="*50)
        print("Enter inputs for your program")
        print("Type 'DONE' on a new line when finished:")
        print("="*50)
        
        user_input_lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'DONE':
                    break
                user_input_lines.append(line)
            except (EOFError, KeyboardInterrupt):
                break
        
        stdin = "\n".join(user_input_lines)
        
        self.logger.info(f"Collected {len(user_input_lines)} lines of input")
        if stdin:
            self.logger.debug(f"Input: {stdin}")
        
        return self._execute_locally(source_code, stdin)
    
    def _execute_locally(self, source_code: str, stdin: str) -> dict:
        """Execute code locally using subprocess"""
        
        self.logger.info("Executing code locally")
        
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write the code to a file
            code_file = Path(tmpdir) / "main.py"
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(source_code)
            
            self.logger.debug(f"Code written to temporary file: {code_file}")
            
            try:
                # Execute the code
                result = subprocess.run(
                    ["python", str(code_file)],
                    input=stdin,
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                    cwd=tmpdir
                )
                
                exit_code = result.returncode
                stdout = result.stdout
                stderr = result.stderr
                
                self.logger.info(f"Execution completed with exit code: {exit_code}")
                
                if stdout:
                    self.logger.debug(f"Stdout ({len(stdout)} chars): {stdout[:200]}...")
                if stderr:
                    self.logger.warning(f"Stderr ({len(stderr)} chars): {stderr[:200]}...")
                
                # Display output
                print("\n" + "="*50)
                print("EXECUTION OUTPUT:")
                print("="*50)
                
                if stdout:
                    print(stdout)
                else:
                    print("(no output)")
                
                if stderr:
                    print("\n--- STDERR ---")
                    print(stderr)
                
                print("="*50)
                print(f"Exit Code: {exit_code}")
                print("="*50)
                
                return {
                    "success": exit_code == 0,
                    "stdout": stdout,
                    "stderr": stderr,
                    "output": stdout,
                    "exit_code": exit_code
                }
                
            except subprocess.TimeoutExpired:
                self.logger.error("Execution timed out after 30 seconds")
                print("\n" + "="*50)
                print("EXECUTION FAILED - TIMEOUT")
                print("="*50)
                print("The code execution timed out after 30 seconds")
                print("="*50)
                
                return {
                    "success": False,
                    "error": "Execution timed out after 30 seconds"
                }
                
            except Exception as e:
                self.logger.error(f"Execution error: {str(e)}", exc_info=True)
                print("\n" + "="*50)
                print("EXECUTION FAILED - ERROR")
                print("="*50)
                print(f"Error: {str(e)}")
                print("="*50)
                
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def _find_main_file(self, files: dict) -> str:
        """Find the main entry point file"""
        for candidate in ["main.py", "app.py", "run.py"]:
            if candidate in files:
                return candidate
        
        for fname, content in files.items():
            if not fname.endswith('.py'):
                continue
            if 'if __name__ == "__main__"' in content:
                return fname
        
        for fname in files:
            if fname.endswith('.py'):
                return fname
        
        return None