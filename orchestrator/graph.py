from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from utils.logger import setup_logger

from agents.planner.agent import PlannerAgent
from agents.coder.agent import CoderAgent
from agents.checker.agent import RequirementCheckerAgent
from agents.debugger.agent import DebuggerAgent
from agents.executor.agent import ExecutorAgent

class AgentState(TypedDict):
    user_input: str
    plan: Optional[object]
    code: Optional[object]
    raw_coder_output: Optional[str]
    check_result: Optional[dict]
    debug_result: Optional[dict]
    execution_result: Optional[dict]
    iteration: int

planner = PlannerAgent()
coder = CoderAgent()
checker = RequirementCheckerAgent()
debugger = DebuggerAgent()
executor = ExecutorAgent()

graph_logger = setup_logger("GraphOrchestrator", "graph.log")

def planner_node(state: AgentState):
    graph_logger.info("=== PLANNER NODE ===")
    plan = planner.run(state["user_input"])
    return {"plan": plan, "iteration": 0}

def coder_node(state: AgentState):
    graph_logger.info(f"=== CODER NODE (Iteration {state.get('iteration', 0)}) ===")
    code, raw_output = coder.run(state["plan"], state.get("debug_result"))
    return {"code": code, "raw_coder_output": raw_output}

def checker_node(state: AgentState):
    graph_logger.info("=== CHECKER NODE ===")
    result = checker.run(state["plan"], state["code"])
    graph_logger.info(f"Check complete: {result['complete']}")
    return {"check_result": result}

def debugger_node(state: AgentState):
    graph_logger.info("=== DEBUGGER NODE ===")
    result = debugger.run(state["code"], state.get("raw_coder_output"))
    graph_logger.info(f"Debug result: {'PASS' if result['correct'] else 'FAIL'}")
    return {"debug_result": result}

def executor_node(state: AgentState):
    graph_logger.info("=== EXECUTOR NODE ===")
    result = executor.run(state["code"])
    graph_logger.info(f"Execution: {'SUCCESS' if result['success'] else 'FAILED'}")
    return {"execution_result": result}

def should_check_or_debug(state: AgentState):
    next_node = "debugger" if state["code"] is None else "checker"
    graph_logger.info(f"Routing to: {next_node}")
    return next_node

def should_continue_after_checker(state: AgentState):
    if state["check_result"]["complete"]:
        graph_logger.info("Requirements complete, moving to debugger")
        return "debugger"

    if state["iteration"] >= 2:
        graph_logger.error("Max iterations reached in checker loop")
        raise RuntimeError("Failed to satisfy requirements after retries")

    graph_logger.warning(f"Requirements incomplete, retry {state['iteration'] + 1}")
    state["iteration"] += 1
    return "coder"

def prepare_retry_node(state: AgentState):
    """Increment iteration counter before retry"""
    graph_logger.warning(f"Preparing retry, iteration {state['iteration']} -> {state['iteration'] + 1}")
    return {"iteration": state["iteration"] + 1}


def should_continue_after_debugger(state: AgentState):
    if state["debug_result"]["correct"]:
        graph_logger.info("Code correct, moving to executor")
        return "executor"
    
    if state["iteration"] >= 5:
        graph_logger.error("Max iterations reached in debugger loop")
        raise RuntimeError("Failed to fix errors after retries")
    
    graph_logger.warning(f"Code has errors, needs retry")
    return "prepare_retry"

def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("checker", checker_node)
    graph.add_node("debugger", debugger_node)
    graph.add_node("executor", executor_node)
    graph.add_node("prepare_retry", prepare_retry_node)  

    graph.set_entry_point("planner")

    graph.add_edge("planner", "coder")
    
    graph.add_conditional_edges(
        "coder",
        should_check_or_debug,
        {
            "checker": "checker",
            "debugger": "debugger",
        },
    )

    graph.add_conditional_edges(
        "checker",
        should_continue_after_checker,
        {
            "coder": "coder",
            "debugger": "debugger",
        },
    )

    graph.add_conditional_edges(
        "debugger",
        should_continue_after_debugger,
        {
            "prepare_retry": "prepare_retry",  
            "executor": "executor",
        },
    )

    graph.add_edge("prepare_retry", "coder")  

    return graph.compile()