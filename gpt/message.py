from pydantic import BaseModel

from enum import Enum
from typing import Dict


class RoleType(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class GPTMessage(BaseModel):
    role: RoleType
    content: str