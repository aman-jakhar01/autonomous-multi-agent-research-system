from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    groq_api_key: str
    tavily_api_key: str