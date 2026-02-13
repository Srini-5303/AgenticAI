import json
from agents.planner.prompt import (
    PLANNER_SYSTEM_PROMPT,
    PLANNER_FEW_SHOTS
)
from agents.planner.schema import PlannerOutput
from agents.planner.config import AGENT_NAME
from llm.registry import get_model


class PlannerAgent:

    def __init__(self):
        self.llm = get_model(AGENT_NAME)

    def run(self, user_prompt: str) -> PlannerOutput:
        messages = []

        for example in PLANNER_FEW_SHOTS:
            messages.append({"role": "user", "content": example["user"]})
            messages.append({"role": "assistant", "content": example["assistant"]})

        messages.append({"role": "user", "content": user_prompt})

        raw_output = self.llm.generate(
            system_prompt=PLANNER_SYSTEM_PROMPT,
            messages=messages
        )

        try:
            parsed = json.loads(raw_output)
            return PlannerOutput(**parsed)
        except Exception:
            raise ValueError(
                f"Planner produced invalid JSON:\n{raw_output}"
            )
