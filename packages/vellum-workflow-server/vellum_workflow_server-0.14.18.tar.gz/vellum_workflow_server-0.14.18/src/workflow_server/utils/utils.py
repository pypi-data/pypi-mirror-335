from importlib.metadata import version
import re
from typing import Any, List

from vellum import (
    ArrayInput,
    ChatHistoryInput,
    ErrorInput,
    FunctionCallInput,
    SearchResultsInput,
    VellumAudio,
    VellumImage,
)
from workflow_server.config import is_development


def convert_json_inputs_to_vellum(inputs: List[dict]) -> dict:
    vellum_inputs: dict[str, Any] = {}

    for input in inputs:
        value = input["value"]
        name = to_python_safe_snake_case(input["name"])
        type = input["type"]

        if type == "CHAT_HISTORY":
            vellum_inputs[name] = ChatHistoryInput.model_validate(input).value
        elif type == "FUNCTION_CALL":
            vellum_inputs[name] = FunctionCallInput.model_validate(input).value
        elif type == "SEARCH_RESULTS":
            vellum_inputs[name] = SearchResultsInput.model_validate(input).value
        elif type == "ERROR":
            vellum_inputs[name] = ErrorInput.model_validate(input).value
        elif type == "ARRAY":
            vellum_inputs[name] = ArrayInput.model_validate(input).value
        # Once we export *Input classes for these two cases, we can add the union to the WorkflowExecutorContext
        # model and simplify this method to just a {to_python_safe_snake_case(input.name): input.value} mapping
        elif type == "IMAGE":
            vellum_inputs[name] = VellumImage.model_validate(value)
        elif type == "AUDIO":
            vellum_inputs[name] = VellumAudio.model_validate(value)
        else:
            vellum_inputs[name] = value

    return vellum_inputs


def get_version() -> dict:
    return {
        "sdk_version": version("vellum-ai"),
        "server_version": "local" if is_development() else version("vellum-workflow-server"),
    }


def to_python_safe_snake_case(string: str, safety_prefix: str = "_") -> str:
    # Strip special characters from start of string
    cleaned_str = re.sub(r"^[^a-zA-Z0-9_]+", "", string)

    # Check if cleaned string starts with a number
    starts_with_unsafe = bool(re.match(r"^\d", cleaned_str))

    # Convert to snake case
    snake_case = re.sub(r"([a-z])([A-Z])", r"\1_\2", cleaned_str)  # Insert underscore between lower and upper case
    snake_case = re.sub(r"[^a-zA-Z0-9]+", "_", snake_case)  # Replace any non-alphanumeric chars with underscore
    snake_case = re.sub(r"^_+|_+$", "", snake_case)  # Remove leading/trailing underscores
    snake_case = snake_case.lower()

    # Add safety prefix if needed
    cleaned_safety_prefix = (
        "_" if safety_prefix == "_" else f"{safety_prefix}{'_' if not safety_prefix.endswith('_') else ''}"
    )
    return f"{cleaned_safety_prefix}{snake_case}" if starts_with_unsafe else snake_case
