# kradle/__init__.py
from .core import (
    MinecraftAgent,
    Observation,
)
from .models import MinecraftEvent
from .docs import LLMDocsForExecutingCode
from .mc import MC
from .agent_manager import AgentManager
from kradle.memory.standard_memory import StandardMemory

# from kradle.memory.firestore_memory import FirestoreMemory
from kradle.memory.redis_memory import RedisMemory
from kradle.api.client import KradleAPI
from kradle.api.http import KradleAPIError
from kradle.api.resources import ChallengeParticipant
from kradle.models import JSON_RESPONSE_FORMAT
__version__ = "1.0.0"
__all__ = [
    "KradleAPI",
    "KradleAPIError",
    "AgentManager",
    "MinecraftAgent",
    "Observation",
    "MinecraftEvent",
    "LLMDocsForExecutingCode",
    "MC",
    "StandardMemory",
    "ChallengeParticipant",
    ##"FirestoreMemory",
    "RedisMemory",
    "InitParticipantResponse",
    "OnEventResponse",
    "JSON_RESPONSE_FORMAT",
]
