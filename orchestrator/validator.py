from agents.planner.schema import PlannerOutput
from agents.coder.schema import CodeOutput


def validate_plan(state):
    plan = state.get("plan")

    if plan is None:
        raise ValueError("Planner did not produce any output")

    if not isinstance(plan, PlannerOutput):
        raise TypeError(
            f"Expected PlannerOutput, got {type(plan)}"
        )

    if not plan.project_name.strip():
        raise ValueError("project_name cannot be empty")

    if not plan.project_type.strip():
        raise ValueError("project_type cannot be empty")

    if not plan.features:
        raise ValueError("features list cannot be empty")

    if not isinstance(plan.components, dict) or not plan.components:
        raise ValueError("components must be a non-empty dict")

    if not isinstance(plan.files, dict) or not plan.files:
        raise ValueError("files must be a non-empty dict")

    if not isinstance(plan.constraints, dict):
        raise ValueError("constraints must be a dict")

    if not plan.success_criteria:
        raise ValueError("success_criteria cannot be empty")

    return state


def validate_code(state):
    code = state.get("code")

    if code is None:
        raise ValueError("Coder did not produce code")

    if not isinstance(code, CodeOutput):
        raise TypeError("Code output is not CodeOutput")

    if not code.files or not isinstance(code.files, dict):
        raise ValueError("CodeOutput.files must be a non-empty dict")

    for fname, content in code.files.items():
        if not isinstance(fname, str) or not isinstance(content, str):
            raise TypeError("Invalid file structure in code output")

    return state
