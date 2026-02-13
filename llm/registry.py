from llm.local import OllamaLLM


MODEL_REGISTRY = {
    "planner": OllamaLLM("llama3.1:8b"),
    "coder": OllamaLLM("deepseek-coder:6.7b"),
    "verifier": OllamaLLM("mistral:7b"),
    "documenter": OllamaLLM("qwen2.5:7b")
}


def get_model(agent_name: str):
    if agent_name not in MODEL_REGISTRY:
        raise ValueError(f"No model registered for agent: {agent_name}")
    return MODEL_REGISTRY[agent_name]
