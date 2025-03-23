from typing import Literal

from syrius.commands.LoopInputCommand import loopType
from syrius.commands.abstract import AbstractCommand, Command


class ReplicateClaudeSonnetCommand(Command):
    id: int = 80
    prompt: str | AbstractCommand | loopType
    system_prompt: str | AbstractCommand | loopType = ""
    max_tokens: int | AbstractCommand | loopType = 8192
    api_key: str | AbstractCommand | loopType