import json
from agents.coder.schema import CodeOutput
from agents.coder.prompt import (
    CODER_SYSTEM_PROMPT,
    CODER_INSTRUCTIONS
)
from agents.coder.config import AGENT_NAME
from llm.registry import get_model
from utils.logger import setup_logger



class CoderAgent:

    def __init__(self):
        self.llm = get_model(AGENT_NAME)
        self.logger = setup_logger("CoderAgent", "coder.log")

    def run(self, plan, debug_result=None) -> tuple:
        """
        Returns: (CodeOutput or None, raw_output_string)
        """
        error_context = ""
        if debug_result and not debug_result.get("correct"):
            self.logger.info("Retrying code generation with debug feedback")
            error_context = f"\n\nPrevious code had errors:\n{json.dumps(debug_result.get('errors', []), indent=2)}\nPlease fix these errors."
        else:
            self.logger.info(f"Generating code for: {plan.project_name}")

        messages = [
            {
                "role": "user",
                "content": f"""
Specification:
{plan.model_dump_json(indent=2)}
{error_context}

{CODER_INSTRUCTIONS}
"""
            }
        ]

        raw_output = self.llm.generate(
            system_prompt=CODER_SYSTEM_PROMPT,
            messages=messages
        )

        try:
            cleaned = raw_output.strip()

            # Remove markdown code fences if present
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                if len(lines) > 2 and lines[-1].strip() == "```":
                    cleaned = "\n".join(lines[1:-1])
                else:
                    cleaned = cleaned.split("```", 1)[1]
                
                if cleaned.strip().startswith("json"):
                    cleaned = cleaned.strip()[4:].strip()

            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            result = CodeOutput(**parsed)
            self.logger.info(f"Code generated successfully: {len(result.files)} files")

            return result, raw_output
        except Exception:
            # Return None for code, but pass raw output to debugger
            self.logger.error("Failed to parse code output")
            return None, raw_output
        

    def _format_debug_feedback(self, debug_result: dict) -> str:
        """Format debug errors into clear, actionable feedback"""
        errors = debug_result.get('errors', [])
        stage = debug_result.get('stage', 'unknown')
        
        if not errors:
            return "\n\nPrevious code had unspecified errors. Please generate valid code."
        
        feedback = "\n\n=== PREVIOUS CODE HAD ERRORS - PLEASE FIX ===\n"
        feedback += f"Stage: {stage}\n\n"
        
        for i, error in enumerate(errors, 1):
            feedback += f"Error {i}:\n"
            feedback += f"  Type: {error.get('error_type', 'Unknown')}\n"
            
            if 'file' in error:
                feedback += f"  File: {error['file']}\n"
            if 'line' in error:
                feedback += f"  Line: {error['line']}\n"
            
            feedback += f"  Issue: {error.get('error', 'Unknown error')}\n"
            
            if 'suggestion' in error:
                feedback += f"  Fix: {error['suggestion']}\n"
            
            feedback += "\n"
        
        # Add specific instructions based on error stage
        if stage == "json_parsing":
            feedback += "CRITICAL: Your output must be valid JSON.\n"
            feedback += "- Ensure all strings are properly quoted\n"
            feedback += "- No trailing commas\n"
            feedback += "- All brackets/braces properly closed\n"
            feedback += "- Output ONLY the JSON, no explanations before or after\n"
        elif stage == "syntax_check":
            feedback += "CRITICAL: Fix all Python syntax errors.\n"
            feedback += "- Check for unterminated strings (missing quotes)\n"
            feedback += "- Ensure proper indentation\n"
            feedback += "- Close all parentheses and brackets\n"
        
        return feedback
