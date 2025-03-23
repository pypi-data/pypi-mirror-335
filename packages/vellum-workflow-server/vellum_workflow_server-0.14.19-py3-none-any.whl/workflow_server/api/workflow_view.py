from datetime import datetime
import json
import logging
from multiprocessing import Queue, set_start_method
from queue import Empty
import time
import traceback
from uuid import uuid4
from typing import Generator, Iterator

from flask import Blueprint, Response, current_app as app, request, stream_with_context
from pydantic import ValidationError

from workflow_server.core.events import (
    VEMBDA_EXECUTION_FULFILLED_EVENT_NAME,
    VembdaExecutionFulfilledBody,
    VembdaExecutionFulfilledEvent,
    VembdaExecutionInitiatedBody,
    VembdaExecutionInitiatedEvent,
)
from workflow_server.core.executor import (
    execute_workflow_pebble_timeout,
    execute_workflow_process_timeout,
    stream_node_pebble_timeout,
    stream_workflow_pebble_timeout,
    stream_workflow_process_timeout,
)
from workflow_server.core.workflow_executor_context import (
    DEFAULT_TIMEOUT_SECONDS,
    NodeExecutorContext,
    WorkflowExecutorContext,
)
from workflow_server.utils.utils import convert_json_inputs_to_vellum, get_version

bp = Blueprint("exec", __name__)

set_start_method("fork", force=True)

logger = logging.getLogger(__name__)


@bp.route("/execute", methods=["POST"])
def exec_route() -> tuple[dict, int]:
    data = request.get_json()
    context = get_workflow_request_context(data)

    app.logger.debug(f"Request received {data.get('execution_id')}")

    try:
        # Pebble uses some sort of managed process pool with timeouts and is like 80ms faster [on live not local]
        # than doing a process yourself. Pebble didn't like it when I used their timeout helper a bunch of times in a
        # big loop and when I used their process pool manually it did other stuff wrong so only used when timeout
        # is the default one
        if context.timeout != DEFAULT_TIMEOUT_SECONDS:
            output = execute_workflow_process_timeout(context)
        else:
            output = execute_workflow_pebble_timeout(context).result()

        resp = {
            "log": output["log"],
            "result": output["result"],
            "stderr": output["stderr"],
            "exit_code": output["exit_code"],
            "timed_out": False,
        }

        app.logger.debug(f"Request complete {data.get('execution_id')}")
        return resp, 200

    except TimeoutError:
        resp = {
            "log": "",
            "result": "",
            "stderr": "",
            "exit_code": -1,
            "timed_out": True,
        }
        return resp, 200
    except Exception as e:
        app.logger.exception(e)

        return {
            "result": "",
            "stderr": traceback.format_exc(),
            "exit_code": -1,
            "timed_out": False,
        }, 200


@bp.route("/stream", methods=["POST"])
def stream_workflow_route() -> Response:
    data = request.get_json()

    try:
        context = get_workflow_request_context(data)
    except ValidationError as e:
        error_message = e.errors()[0]["msg"]
        error_location = e.errors()[0]["loc"]

        return Response(
            json.dumps({"detail": f"Invalid context: {error_message} at {error_location}"}),
            status=400,
            content_type="application/json",
        )

    # Create this event up here so timestamps are fully from the start to account for any unknown overhead
    vembda_initiated_event = VembdaExecutionInitiatedEvent(
        id=uuid4(),
        timestamp=datetime.now(),
        trace_id=context.trace_id,
        span_id=context.execution_id,
        body=VembdaExecutionInitiatedBody(
            sdk_version=get_version().get("sdk_version"),
            server_version=get_version().get("server_version"),
        ),
        parent=None,
    )

    app.logger.debug(f"Stream received {context.execution_id}")

    if context.timeout != DEFAULT_TIMEOUT_SECONDS:
        process_queue: Queue[dict] = Queue()
        stream_workflow_process_timeout(
            executor_context=context,
            queue=process_queue,
        )

        def process_events() -> Iterator[dict]:
            while True:
                try:
                    event = process_queue.get(timeout=context.timeout)
                    yield event

                    if event.get("name") == VEMBDA_EXECUTION_FULFILLED_EVENT_NAME:
                        break
                except Empty:
                    continue
                except Exception as e:
                    # This happens when theres a problem with process execution itself not the workflow runner
                    vembda_fulfilled_event = VembdaExecutionFulfilledEvent(
                        id=uuid4(),
                        timestamp=datetime.now(),
                        trace_id=context.trace_id,
                        span_id=context.execution_id,
                        body=VembdaExecutionFulfilledBody(
                            exit_code=-1,
                            stderr="Internal Server Error",
                            container_overhead_latency=context.container_overhead_latency,
                        ),
                        parent=None,
                    )
                    yield vembda_fulfilled_event.model_dump(mode="json")
                    app.logger.exception(e)
                    break

        workflow_events = process_events()
    else:
        pebble_queue: Queue[dict] = Queue()
        stream_future = stream_workflow_pebble_timeout(
            executor_context=context,
            queue=pebble_queue,
        )

        def pebble_events() -> Iterator[dict]:
            while True:
                try:
                    event = pebble_queue.get(timeout=context.timeout)
                except Empty:
                    if stream_future.exception() is not None:
                        # This happens when theres a problem with the stream function call
                        # itself not the workflow runner
                        vembda_fulfilled_event = VembdaExecutionFulfilledEvent(
                            id=uuid4(),
                            timestamp=datetime.now(),
                            trace_id=context.trace_id,
                            span_id=context.execution_id,
                            body=VembdaExecutionFulfilledBody(
                                exit_code=-1,
                                stderr="Internal Server Error",
                                container_overhead_latency=context.container_overhead_latency,
                            ),
                            parent=None,
                        )
                        yield vembda_fulfilled_event.model_dump(mode="json")
                        app.logger.exception(stream_future.exception())
                        break
                    else:
                        continue

                yield event
                if event.get("name") == VEMBDA_EXECUTION_FULFILLED_EVENT_NAME:
                    break

        workflow_events = pebble_events()

    def generator() -> Generator[str, None, None]:
        yield "\n"
        yield vembda_initiated_event.model_dump_json()
        yield "\n"
        for index, row in enumerate(workflow_events):
            yield "\n"
            yield json.dumps(row)
            yield "\n"

    resp = Response(stream_with_context(generator()), status=200, content_type='application/x-ndjson"')
    return resp


@bp.route("/stream-node", methods=["POST"])
def stream_node_route() -> Response:
    data = request.get_json()

    try:
        context = get_node_request_context(data)
    except ValidationError as e:
        error_message = e.errors()[0]["msg"]
        error_location = e.errors()[0]["loc"]
        return Response(
            json.dumps({"detail": f"Invalid context: {error_message} at {error_location}"}),
            status=400,
            content_type="application/json",
        )

    # Create this event up here so timestamps are fully from the start to account for any unknown overhead
    vembda_initiated_event = VembdaExecutionInitiatedEvent(
        id=uuid4(),
        timestamp=datetime.now(),
        trace_id=context.trace_id,
        span_id=context.execution_id,
        body=VembdaExecutionInitiatedBody(
            sdk_version=get_version().get("sdk_version"),
            server_version=get_version().get("server_version"),
        ),
        parent=None,
    )

    app.logger.debug(f"Node stream received {data.get('execution_id')}")

    pebble_queue: Queue[dict] = Queue()
    stream_future = stream_node_pebble_timeout(
        executor_context=context,
        queue=pebble_queue,
    )

    def node_events() -> Iterator[dict]:
        while True:
            try:
                event = pebble_queue.get(timeout=context.timeout)
            except Empty:
                if stream_future.exception() is not None:
                    # This happens when theres a problem with the stream function call
                    # itself not the workflow runner
                    vembda_fulfilled_event = VembdaExecutionFulfilledEvent(
                        id=uuid4(),
                        timestamp=datetime.now(),
                        trace_id=context.trace_id,
                        span_id=context.execution_id,
                        body=VembdaExecutionFulfilledBody(
                            exit_code=-1,
                            stderr="Internal Server Error",
                            container_overhead_latency=context.container_overhead_latency,
                        ),
                        parent=None,
                    )
                    yield vembda_fulfilled_event.model_dump(mode="json")
                    app.logger.exception(stream_future.exception())
                    break
                else:
                    continue

            yield event
            if event.get("name") == VEMBDA_EXECUTION_FULFILLED_EVENT_NAME:
                break

    def generator() -> Generator[str, None, None]:
        yield json.dumps(vembda_initiated_event.model_dump(mode="json"))

        for index, row in enumerate(node_events()):
            yield "\n"
            yield json.dumps(row)

    resp = Response(stream_with_context(generator()), status=200, content_type='application/x-ndjson"')
    return resp


@bp.route("/version", methods=["GET"])
def get_version_route() -> tuple[dict, int]:
    resp = get_version()

    return resp, 200


def get_workflow_request_context(data: dict) -> WorkflowExecutorContext:
    # not sure if this is the filter we want to pass forward?
    context_data = {
        **data,
        "inputs": convert_json_inputs_to_vellum(data["inputs"]),
        "trace_id": uuid4(),
        "request_start_time": time.time_ns(),
    }

    return WorkflowExecutorContext.model_validate(context_data)


def get_node_request_context(data: dict) -> NodeExecutorContext:
    context_data = {
        **data,
        "inputs": convert_json_inputs_to_vellum(data["inputs"]),
        "trace_id": uuid4(),
        "request_start_time": time.time_ns(),
    }

    return NodeExecutorContext.model_validate(context_data)
