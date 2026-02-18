import subprocess


class OllamaLLM:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, system_prompt: str, messages: list) -> str:
        prompt = self._build_prompt(system_prompt, messages)

        process = subprocess.Popen(
            ["ollama", "run", self.model_name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",     
            errors="replace",
            bufsize=1
        )

        try:
            stdout, stderr = process.communicate(prompt, timeout=120)
        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError("Ollama LLM timed out and was killed")

        if process.returncode != 0:
            raise RuntimeError(stderr.strip())

        return stdout.strip()

    def _build_prompt(self, system_prompt, messages):
        prompt = f"{system_prompt}\n\n"
        for msg in messages:
            role = msg["role"].upper()
            prompt += f"{role}: {msg['content']}\n\n"
        return prompt
