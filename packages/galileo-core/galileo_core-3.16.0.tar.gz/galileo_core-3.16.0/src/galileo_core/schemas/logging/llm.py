from enum import Enum
from typing import Generator, List, Optional

from pydantic import BaseModel, RootModel


class MessageRole(str, Enum):
    agent = "agent"
    assistant = "assistant"
    developer = "developer"
    function = "function"
    system = "system"
    tool = "tool"
    user = "user"


class Message(BaseModel):
    content: str
    role: MessageRole
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List["ToolCall"]] = None


class Messages(RootModel[List[Message]]):
    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self) -> Generator[Message, None, None]:  # type: ignore[override]
        yield from self.root

    def __getitem__(self, item: int) -> Message:
        return self.root[item]


class ToolCall(BaseModel):
    id: str
    function: "ToolCallFunction"


class ToolCallFunction(BaseModel):
    name: str
    arguments: str
