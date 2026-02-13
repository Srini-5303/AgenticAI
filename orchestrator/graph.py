from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from agents.planner.agent import PlannerAgent
from agents.coder.agent import CoderAgent
from agents.checker.agent import RequirementCheckerAgent


# -------- Shared State --------
class AgentState(TypedDict):
    user_input: str
    plan: Optional[object]
    code: Optional[object]
    check_result: Optional[dict]
    iteration: int


# -------- Agents --------
planner = PlannerAgent()
coder = CoderAgent()
checker = RequirementCheckerAgent()


# -------- Node Functions --------
def planner_node(state: AgentState):
    plan = planner.run(state["user_input"])
    return {"plan": plan, "iteration": 0}


def coder_node(state: AgentState):
    code = coder.run(state["plan"])
    return {"code": code}


def checker_node(state: AgentState):
    result = checker.run(state["plan"], state["code"])
    return {"check_result": result}


# -------- Routing Logic --------
def should_continue(state: AgentState):
    if state["check_result"]["complete"]:
        return END

    if state["iteration"] >= 2:
        raise RuntimeError("Failed to satisfy requirements after retries")

    # feed missing requirements back into plan
    state["plan"]["missing_requirements"] = state["check_result"]["missing_requirements"]
    state["iteration"] += 1
    return "coder"


# -------- Graph Definition --------
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("checker", checker_node)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "checker")

    graph.add_conditional_edges(
        "checker",
        should_continue,
        {
            "coder": "coder",
            END: END,
        },
    )

    return graph.compile()
