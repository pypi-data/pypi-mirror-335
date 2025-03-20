from uuid import UUID
from typing import Any, Optional

from vellum.client.core import UniversalBaseModel
from vellum.workflows.context import ExecutionContext
from vellum.workflows.events.types import ParentContext

DEFAULT_TIMEOUT_SECONDS = 60 * 30


class BaseExecutorContext(UniversalBaseModel):
    inputs: dict
    state: Optional[dict] = None
    timeout: int = DEFAULT_TIMEOUT_SECONDS
    files: dict[str, str]
    workspace_api_key: str
    execution_id: UUID
    trace_id: UUID
    module: str
    parent_context: Optional[ParentContext] = None
    execution_context: Optional[ExecutionContext] = None
    request_start_time: int
    stream_start_time: int = 0
    vembda_public_url: Optional[str] = None
    node_output_mocks: Optional[list[Any]] = None

    @property
    def container_overhead_latency(self) -> int:
        return self.stream_start_time - self.request_start_time if self.stream_start_time else -1

    def __hash__(self) -> int:
        # do we think we need anything else for a unique hash for caching?
        return hash(str(self.execution_id))


class WorkflowExecutorContext(BaseExecutorContext):
    pass


class NodeExecutorContext(BaseExecutorContext):
    node_module: str
    node_name: str
