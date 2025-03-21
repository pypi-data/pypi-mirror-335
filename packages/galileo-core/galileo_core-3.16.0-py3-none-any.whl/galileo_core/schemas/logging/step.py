from datetime import datetime, timezone
from enum import Enum
from json import dumps
from typing import Any, Dict, List, Optional, Sequence, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from pydantic_core.core_schema import ValidationInfo

from galileo_core.schemas.logging.llm import Message
from galileo_core.schemas.shared.document import Document
from galileo_core.utils.json import PydanticJsonEncoder

StepAllowedInputType = Union[str, Sequence[Message]]
StepAllowedOutputType = Union[None, str, Message, Sequence[Document]]


class StepType(str, Enum):
    llm = "llm"
    retriever = "retriever"
    tool = "tool"
    workflow = "workflow"
    trace = "trace"


class Metrics(BaseModel):
    duration_ns: Optional[int] = Field(default=None, description="Duration of the step in milliseconds.")

    model_config = ConfigDict(extra="allow")


class BaseStep(BaseModel):
    type: StepType = Field(
        default=StepType.workflow, description="Type of the step. By default, it is set to workflow."
    )
    input: StepAllowedInputType = Field(description="Input to the step.", union_mode="left_to_right")
    output: StepAllowedOutputType = Field(default=None, description="Output of the step.", union_mode="left_to_right")
    name: str = Field(default="", description="Name of the step.", validate_default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc), description="Timestamp of the step's creation"
    )
    user_metadata: Dict[str, str] = Field(default_factory=dict, description="Metadata associated with this step.")
    tags: List[str] = Field(default_factory=list, description="Tags associated with this step.")
    status_code: Optional[int] = Field(
        default=None, description="Status code of the step. Used for logging failed/errored steps."
    )
    metrics: Metrics = Field(default_factory=Metrics, description="Metrics associated with this step.")

    model_config = ConfigDict(validate_assignment=True)

    def __init__(self, **data: Any):
        for k, v in list(data.items()):
            if v is None:
                del data[k]
        super().__init__(**data)

    @field_validator("name", mode="before")
    def set_name(cls, value: Optional[str], info: ValidationInfo) -> str:
        if value is not None:
            return value
        if "type" in info.data:
            return info.data["type"]
        raise ValidationError("could not set step name from type since type is missing")

    @field_validator("input", mode="after")
    def validate_input_serializable(cls, val: StepAllowedInputType) -> StepAllowedInputType:
        # Make sure we can dump input/output to json string.
        dumps(val, cls=PydanticJsonEncoder)
        return val

    @field_validator("output", mode="after")
    def validate_output_serializable(cls, val: StepAllowedOutputType) -> StepAllowedOutputType:
        # Make sure we can dump input/output to json string.
        dumps(val, cls=PydanticJsonEncoder)
        return val
