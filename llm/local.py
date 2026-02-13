import subprocess
import json


class OllamaLLM:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, system_prompt: str, messages: list) -> str:
        prompt = self._build_prompt(system_prompt, messages)

        result = subprocess.run(
            ["ollama", "run", self.model_name],
            input=prompt,
            encoding="utf-8",
            capture_output=True, 
            errors="replace"
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr)

        return result.stdout.strip()

    def _build_prompt(self, system_prompt, messages):
        prompt = f"{system_prompt}\n\n"
        for msg in messages:
            role = msg["role"].upper()
            prompt += f"{role}: {msg['content']}\n\n"
        return prompt
