import json
from agents.planner.prompt import (
    PLANNER_SYSTEM_PROMPT,
    PLANNER_FEW_SHOTS
)
from agents.planner.schema import PlannerOutput
from agents.planner.config import AGENT_NAME
from llm.registry import get_model
from utils.logger import setup_logger

class PlannerAgent:

    def __init__(self):
        self.llm = get_model(AGENT_NAME)
        self.logger = setup_logger("PlannerAgent", "planner.log")

    def run(self, user_prompt: str) -> PlannerOutput:
        self.logger.info(f"Starting planning for: {user_prompt[:100]}...")

        messages = []

        for example in PLANNER_FEW_SHOTS:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})

        messages.append({"role": "user", "content": user_prompt})

        self.logger.debug("Sending request to LLM")
        raw_output = self.llm.generate(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            messages=messages
        )

        try:
            parsed = json.loads(raw_output)
            result = PlannerOutput(**parsed)
            self.logger.info(f"Plan generated: {result.project_name}")
            return result
        
        except Exception as e:
            self.logger.error(f"Failed to parse planner output: {str(e)}")
            self.logger.debug(f"Raw output: {raw_output}")
            raise ValueError(
                f"Planner produced invalid JSON:\n{raw_output}"
            )
