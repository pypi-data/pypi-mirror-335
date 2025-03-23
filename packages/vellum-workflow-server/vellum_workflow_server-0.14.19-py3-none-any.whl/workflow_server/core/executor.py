from contextlib import redirect_stdout
from datetime import datetime
import importlib
from io import StringIO
import json
import logging
from multiprocessing import Manager, Process, Queue
import os
import random
import string
import sys
from threading import Event as ThreadingEvent
import time
from traceback import format_exc
from uuid import uuid4
from typing import Any, Callable, Generator, Iterator, Optional, Tuple

from pebble import concurrent
from vellum_ee.workflows.display.workflows import BaseWorkflowDisplay
from vellum_ee.workflows.server.virtual_file_loader import VirtualFileFinder

from vellum import Vellum, VellumEnvironment
from vellum.workflows import BaseWorkflow
from vellum.workflows.errors import WorkflowError, WorkflowErrorCode
from vellum.workflows.events.types import BaseEvent
from vellum.workflows.events.workflow import WorkflowEventDisplayContext
from vellum.workflows.exceptions import WorkflowInitializationException
from vellum.workflows.inputs import BaseInputs
from vellum.workflows.nodes import BaseNode
from vellum.workflows.nodes.mocks import MockNodeExecution
from vellum.workflows.state.base import BaseState, StateMeta
from vellum.workflows.state.context import WorkflowContext
from vellum.workflows.workflows.event_filters import all_workflow_event_filter
from workflow_server.core.cancel_workflow import CancelWorkflowWatcherThread
from workflow_server.core.events import VembdaExecutionFulfilledBody, VembdaExecutionFulfilledEvent
from workflow_server.core.workflow_executor_context import (
    DEFAULT_TIMEOUT_SECONDS,
    BaseExecutorContext,
    NodeExecutorContext,
    WorkflowExecutorContext,
)
from workflow_server.utils.log_proxy import redirect_log

logger = logging.getLogger(__name__)


@concurrent.process(timeout=DEFAULT_TIMEOUT_SECONDS)
def execute_workflow_pebble_timeout(executor_context: WorkflowExecutorContext) -> dict:
    return execute_workflow(executor_context, output={})


def execute_workflow_process_timeout(executor_context: WorkflowExecutorContext) -> dict:
    try:
        with Manager() as manager:
            output = manager.dict()

            p = Process(
                target=execute_workflow,
                args=(
                    executor_context,
                    output,
                ),
            )
            p.start()
            p.join(executor_context.timeout)
            if p.is_alive():
                p.kill()

            if output.get("exit_code") is None:
                return {
                    "log": "",
                    "result": {},
                    "stderr": "",
                    "exit_code": -1,
                    "timed_out": True,
                }

            return {
                "log": output["log"],
                "result": output["result"],
                "stderr": output["stderr"],
                "exit_code": output["exit_code"],
                "timed_out": False,
            }

    except Exception as e:
        logger.exception(e)

        return {
            "result": {},
            "stderr": format_exc(),
            "exit_code": -1,
            "timed_out": False,
        }


def execute_workflow(executor_context: WorkflowExecutorContext, output: dict) -> dict:
    log_redirect = StringIO()

    try:
        # We need to namespace to avoid any collisions with the pebble managed process pool that may or may not
        # reuse processes and also this avoids collisions with local packages and also fixes the virtual loader
        # not working with relative import paths. We also do this renaming on the fly in the virtual file finder
        # to avoid copying the files dict and costing extra latency and ram.
        namespace = _get_file_namespace(executor_context)
        sys.meta_path.append(VirtualFileFinder(executor_context.files, namespace))
        inputs = importlib.import_module(f"{namespace}.inputs")

        with redirect_stdout(log_redirect):
            result = _create_workflow(
                executor_context=executor_context,
                namespace=namespace,
            ).run(
                inputs=inputs.Inputs(**executor_context.inputs),
            )

        log = log_redirect.getvalue()

        exec_output = result
        output["result"] = exec_output.model_dump(mode="json")
        output["log"] = log
        output["stderr"] = ""
        output["exit_code"] = 0
    except Exception:
        output["result"] = ""
        output["exit_code"] = -1
        output["log"] = log_redirect.getvalue()
        output["stderr"] = format_exc()

    return output


@concurrent.process(timeout=DEFAULT_TIMEOUT_SECONDS)
# type ignore since pebble annotation changes return type
def stream_workflow_pebble_timeout(
    executor_context: WorkflowExecutorContext,
    queue: Queue,
) -> None:
    _stream_workflow_wrapper(
        executor_context=executor_context,
        output={},
        queue=queue,
    )


@concurrent.process(timeout=DEFAULT_TIMEOUT_SECONDS)
# type ignore since pebble annotation changes return type
def stream_node_pebble_timeout(
    executor_context: NodeExecutorContext,
    queue: Queue,
) -> None:
    _stream_node_wrapper(
        executor_context=executor_context,
        output={},
        queue=queue,
    )


def _stream_node_wrapper(executor_context: NodeExecutorContext, output: dict, queue: Queue) -> None:
    try:
        for event in stream_node(executor_context=executor_context, output=output):
            queue.put(event)
    except Exception as e:
        logger.exception(e)
        queue.put(
            VembdaExecutionFulfilledEvent(
                id=uuid4(),
                timestamp=datetime.now(),
                trace_id=executor_context.trace_id,
                span_id=executor_context.execution_id,
                body=VembdaExecutionFulfilledBody(
                    exit_code=-1,
                    stderr="Internal Server Error",
                    container_overhead_latency=executor_context.container_overhead_latency,
                ),
                parent=None,
            ).model_dump(mode="json")
        )


def _stream_workflow_wrapper(executor_context: WorkflowExecutorContext, output: dict, queue: Queue) -> None:
    try:
        for event in stream_workflow(executor_context=executor_context, output=output):
            queue.put(event)
    except WorkflowInitializationException as e:
        queue.put(
            VembdaExecutionFulfilledEvent(
                id=uuid4(),
                timestamp=datetime.now(),
                trace_id=executor_context.trace_id,
                span_id=executor_context.execution_id,
                body=VembdaExecutionFulfilledBody(
                    exit_code=-1,
                    stderr=str(e),
                    container_overhead_latency=executor_context.container_overhead_latency,
                ),
                parent=None,
            ).model_dump(mode="json")
        )
    except Exception as e:
        logger.exception(e)
        queue.put(
            VembdaExecutionFulfilledEvent(
                id=uuid4(),
                timestamp=datetime.now(),
                trace_id=executor_context.trace_id,
                span_id=executor_context.execution_id,
                body=VembdaExecutionFulfilledBody(
                    exit_code=-1,
                    stderr="Internal Server Error",
                    container_overhead_latency=executor_context.container_overhead_latency,
                ),
                parent=None,
            ).model_dump(mode="json")
        )


def stream_workflow_process_timeout(executor_context: WorkflowExecutorContext, queue: Queue) -> None:
    try:
        with Manager() as manager:
            output = manager.dict()

            p = Process(
                target=_stream_workflow_wrapper,
                args=(
                    executor_context,
                    output,
                    queue,
                ),
            )
            p.start()
            p.join(executor_context.timeout)
            if p.is_alive():
                p.kill()

            if output.get("exit_code") is None:
                vembda_fulfilled_event = VembdaExecutionFulfilledEvent(
                    id=uuid4(),
                    timestamp=datetime.now(),
                    trace_id=executor_context.trace_id,
                    span_id=executor_context.execution_id,
                    body=VembdaExecutionFulfilledBody(
                        exit_code=-1,
                        timed_out=True,
                        container_overhead_latency=executor_context.container_overhead_latency,
                    ),
                    parent=None,
                )
                queue.put(vembda_fulfilled_event.model_dump(mode="json"))

    except Exception as e:
        logger.exception(e)

        vembda_fulfilled_event = VembdaExecutionFulfilledEvent(
            id=uuid4(),
            timestamp=datetime.now(),
            trace_id=executor_context.trace_id,
            span_id=executor_context.execution_id,
            body=VembdaExecutionFulfilledBody(
                exit_code=-1,
                stderr=format_exc(),
                container_overhead_latency=executor_context.container_overhead_latency,
            ),
            parent=None,
        )
        queue.put(vembda_fulfilled_event.model_dump(mode="json"))


def stream_workflow(
    executor_context: WorkflowExecutorContext,
    output: dict,
    disable_redirect: bool = False,
) -> Iterator[dict]:
    workflow, namespace = _gather_workflow(executor_context)
    workflow_inputs = _get_workflow_inputs(executor_context)
    display_context = _gather_display_context(workflow, namespace)
    node_output_mocks = MockNodeExecution.validate_all(
        executor_context.node_output_mocks,
        workflow.__class__,
    )

    def call_workflow() -> Generator[dict[str, Any], Any, None]:
        cancel_watcher_kill_switch = ThreadingEvent()
        cancel_signal = ThreadingEvent()
        cancel_watcher = CancelWorkflowWatcherThread(
            kill_switch=cancel_watcher_kill_switch,
            execution_id=executor_context.execution_id,
            timeout_seconds=executor_context.timeout,
            vembda_public_url=executor_context.vembda_public_url,
            cancel_signal=cancel_signal,
        )

        try:
            if executor_context.vembda_public_url:
                cancel_watcher.start()

            stream = workflow.stream(
                inputs=workflow_inputs,
                node_output_mocks=node_output_mocks,
                event_filter=all_workflow_event_filter,
                cancel_signal=cancel_signal,
            )

            first = True
            for event in stream:
                if first:
                    executor_context.stream_start_time = time.time_ns()
                    first = False
                    if event.name == "workflow.execution.initiated":
                        event.body.display_context = display_context

                if event.name.endswith("rejected") and event.body.error.code.name == "INTERNAL_ERROR":  # type: ignore
                    logger.exception(event.body.error.message)  # type: ignore
                    event.body.error = WorkflowError(  # type: ignore
                        code=WorkflowErrorCode.INTERNAL_ERROR.value, message="Internal Error"  # type: ignore
                    )

                yield _dump_event(
                    event=event,
                    executor_context=executor_context,
                )
        finally:
            cancel_watcher_kill_switch.set()

    return _call_stream(
        executor_context=executor_context,
        output=output,
        stream_generator=call_workflow,
        disable_redirect=disable_redirect,
    )


def stream_node(
    executor_context: NodeExecutorContext,
    output: dict,
    disable_redirect: bool = False,
) -> Iterator[dict]:
    namespace = _get_file_namespace(executor_context)

    def call_node() -> Generator[dict[str, Any], Any, None]:
        sys.meta_path.append(VirtualFileFinder(executor_context.files, namespace))
        workflow_context = _create_workflow_context(executor_context)
        node_module = importlib.import_module(f"{namespace}.{executor_context.node_module}")

        Node = getattr(node_module, executor_context.node_name)

        workflow_inputs = _get_workflow_inputs(executor_context)

        State = (
            importlib.import_module(f"{namespace}.state").State if executor_context.files.get("state.py") else BaseState
        )

        if executor_context.state:
            state = State.parse_raw(executor_context.state)
        else:
            state = State(
                meta=StateMeta(workflow_inputs=workflow_inputs),
            )

        node = Node(
            state=state,
            context=workflow_context,
        )

        executor_context.stream_start_time = time.time_ns()
        node_outputs = node.run()

        if isinstance(node_outputs, (Iterator)):
            for node_output in node_outputs:
                yield json.loads(json.dumps(node_output, default=vars))
        else:
            yield json.loads(json.dumps(node_outputs, default=vars))

    return _call_stream(
        executor_context=executor_context,
        output=output,
        stream_generator=call_node,
        disable_redirect=disable_redirect,
    )


def _call_stream(
    executor_context: BaseExecutorContext,
    output: dict,
    stream_generator: Callable[[], Generator[dict[str, Any], Any, None]],
    disable_redirect: bool = False,
) -> Iterator[dict]:
    log_redirect: Optional[StringIO] = None

    if not disable_redirect:
        log_redirect = redirect_log()

    try:
        yield from stream_generator()

        output["exit_code"] = 0
        vembda_fulfilled_event = VembdaExecutionFulfilledEvent(
            id=uuid4(),
            timestamp=datetime.now(),
            trace_id=executor_context.trace_id,
            span_id=executor_context.execution_id,
            body=VembdaExecutionFulfilledBody(
                exit_code=0,
                log=log_redirect.getvalue() if log_redirect else "",
                stderr="",
                container_overhead_latency=executor_context.container_overhead_latency,
            ),
            parent=None,
        )
        yield vembda_fulfilled_event.model_dump(mode="json")

    except Exception:
        output["exit_code"] = -1
        vembda_fulfilled_event = VembdaExecutionFulfilledEvent(
            id=uuid4(),
            timestamp=datetime.now(),
            trace_id=executor_context.trace_id,
            span_id=executor_context.execution_id,
            body=VembdaExecutionFulfilledBody(
                exit_code=-1,
                log=log_redirect.getvalue() if log_redirect else "",
                stderr=format_exc(),
                container_overhead_latency=executor_context.container_overhead_latency,
            ),
            parent=None,
        )
        yield vembda_fulfilled_event.model_dump(mode="json")


def _create_workflow(executor_context: WorkflowExecutorContext, namespace: str) -> BaseWorkflow:
    workflow_context = _create_workflow_context(executor_context)
    Workflow = BaseWorkflow.load_from_module(namespace)
    VembdaExecutionFulfilledEvent.model_rebuild(
        # Not sure why this is needed, but it is required for the VembdaExecutionFulfilledEvent to be
        # properly rebuilt with the recursive types.
        _types_namespace={
            "BaseWorkflow": BaseWorkflow,
            "BaseNode": BaseNode,
        },
    )

    return Workflow(context=workflow_context)


def _create_workflow_context(executor_context: BaseExecutorContext) -> WorkflowContext:
    if os.getenv("USE_LOCAL_VELLUM_API") == "true":
        VELLUM_API_URL = "http://localhost:8000"
        environment = VellumEnvironment(
            default=VELLUM_API_URL,
            documents=VELLUM_API_URL,
            predict=VELLUM_API_URL,
        )
    else:
        environment = VellumEnvironment.PRODUCTION

    return WorkflowContext(
        vellum_client=Vellum(
            api_key=executor_context.workspace_api_key,
            environment=environment,
        ),
        execution_context=executor_context.execution_context,
    )


def _get_file_namespace(executor_context: BaseExecutorContext) -> str:
    return str(executor_context.execution_id) or "".join(
        random.choice(string.ascii_letters + string.digits) for i in range(14)
    )


def _dump_event(event: BaseEvent, executor_context: BaseExecutorContext) -> dict:
    module_base = executor_context.module.split(".")
    dump = event.model_dump(mode="json")
    if dump["name"] in {
        "workflow.execution.initiated",
        "workflow.execution.fulfilled",
        "workflow.execution.rejected",
        "workflow.execution.streaming",
        "workflow.execution.paused",
        "workflow.execution.resumed",
    }:
        dump["body"]["workflow_definition"]["module"] = module_base + dump["body"]["workflow_definition"]["module"][1:]
    elif dump["name"] in {
        "node.execution.initiated",
        "node.execution.fulfilled",
        "node.execution.rejected",
        "node.execution.streaming",
        "node.execution.paused",
        "node.execution.resumed",
    }:
        dump["body"]["node_definition"]["module"] = module_base + dump["body"]["node_definition"]["module"][1:]

    return dump


def _get_workflow_inputs(executor_context: BaseExecutorContext) -> Optional[BaseInputs]:
    if not executor_context.inputs:
        return None

    if not executor_context.files.get("inputs.py"):
        return None

    namespace = _get_file_namespace(executor_context)
    inputs_module_path = f"{namespace}.inputs"
    try:
        inputs_module = importlib.import_module(inputs_module_path)
    except Exception as e:
        raise WorkflowInitializationException(f"Failed to initialize workflow inputs: {e}") from e

    if not hasattr(inputs_module, "Inputs"):
        raise WorkflowInitializationException(
            f"Inputs module {inputs_module_path} does not have a required Inputs class"
        )

    if not issubclass(inputs_module.Inputs, BaseInputs):
        raise WorkflowInitializationException(
            f"""The class {inputs_module_path}.Inputs was expected to be a subclass of BaseInputs, \
but found {inputs_module.Inputs.__class__.__name__}"""
        )

    return inputs_module.Inputs(**executor_context.inputs)


def _gather_workflow(context: WorkflowExecutorContext) -> Tuple[BaseWorkflow, str]:
    try:
        namespace = _get_file_namespace(context)
        sys.meta_path.append(VirtualFileFinder(context.files, namespace))
        workflow = _create_workflow(
            executor_context=context,
            namespace=namespace,
        )
        return workflow, namespace
    except Exception as e:
        raise WorkflowInitializationException(f"Failed to initialize workflow: {e}") from e


def _gather_display_context(workflow: BaseWorkflow, namespace: str) -> Optional["WorkflowEventDisplayContext"]:
    try:
        return BaseWorkflowDisplay.gather_event_display_context(namespace, workflow.__class__)
    except Exception:
        logger.exception("Unable to Parse Workflow Display Context")
        return None
