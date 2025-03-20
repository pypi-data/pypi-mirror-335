from enum import Enum


class AIProvider(str, Enum):
    ANTHROPIC = "anthropic"
    CUSTOMAI = "customai"
    DEEPSEEK = "deepseek"
    GOOGLEAI = "googleai"
    GROQ = "groq"
    MISTRAL = "mistral"
    OPENAI = "openai"
    OPENROUTER = "openrouter"

    def __str__(self) -> str:
        return str(self.value)
