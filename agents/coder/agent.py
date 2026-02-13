import json
from agents.coder.schema import CodeOutput
from agents.coder.prompt import (
    CODER_SYSTEM_PROMPT,
    CODER_INSTRUCTIONS
)
from agents.coder.config import AGENT_NAME
from llm.registry import get_model


class CoderAgent:

    def __init__(self):
        self.llm = get_model(AGENT_NAME)

    def run(self, plan) -> CodeOutput:
        messages = [
            {
                "role": "user",
                "content": f"""
Specification:
{plan.model_dump_json(indent=2)}

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
                cleaned = cleaned.split("```")[1]

            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            return CodeOutput(**parsed)
        except Exception:
            raise ValueError(
                f"Coder produced invalid output:\n{raw_output}"
            )
