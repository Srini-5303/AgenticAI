from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def generate(self, system_prompt: str, messages: list) -> str:
        pass
