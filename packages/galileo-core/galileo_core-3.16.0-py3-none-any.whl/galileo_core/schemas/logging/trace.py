from typing import Literal, Optional

from pydantic import Field

from galileo_core.schemas.logging.span import (
    Span,  # noqa: F401  # to solve forward reference issues
    StepWithChildSpans,
)
from galileo_core.schemas.logging.step import BaseStep, StepType


class BaseTrace(BaseStep):
    type: Literal[StepType.trace] = Field(default=StepType.trace, description="Type: must be `trace`")
    input: str = Field(description="Input to the step.")
    output: Optional[str] = Field(default=None, description="Output of the step.")


class Trace(BaseTrace, StepWithChildSpans):
    pass
