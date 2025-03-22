import os
from typing import Any, Dict, List, Optional

from valohai_yaml.objs import Config, Parameter, Step
from valohai_yaml.objs.input import Input, KeepDirectories
from valohai_yaml.utils import listify

from valohai.consts import DEFAULT_DOCKER_IMAGE
from valohai.internals.notebooks import (
    get_notebook_command,
    get_notebook_source_code,
    parse_ipynb,
)
from valohai.internals.parsing import parse
from valohai.types import InputDict, ParameterDict
from valohai.internals.utils import is_local_file_path


def generate_step(
    *,
    relative_source_path: str,
    step: str,
    image: str,
    parameters: Dict[str, Any],
    inputs: Dict[str, Any],
    environment: Optional[str] = None,
    multifile: bool = False,
    upload_store: Optional[str] = None,
) -> Step:
    # We need to generate a POSIX-compliant command, even if we are running this method in Windows
    # The path separator must be forced to POSIX
    relative_source_path = relative_source_path.replace(os.sep, "/")
    config_step = Step(
        name=step,
        image=image,
        command=get_command(relative_source_path, multifile=multifile),
        source_path=relative_source_path if multifile else None,
        environment=environment,
        upload_store=upload_store,
    )

    for key, value in parameters.items():
        config_step.parameters[key] = parse_parameter(key, value)

    for key, value in inputs.items():
        config_step.inputs[key] = parse_input(key, value)
    return config_step


def parse_parameter(key: str, value: Any) -> Parameter:
    if isinstance(value, dict):
        value["name"] = key
        if "default" in value and "type" not in value:
            value["type"] = get_parameter_type_name(key, value["default"])
        return Parameter.parse(value)

    parameter = Parameter(
        name=key,
        type=get_parameter_type_name(key, value),
        default=value,
    )

    if parameter.type == "flag":
        parameter.pass_true_as = f"--{parameter.name}=true"
        parameter.pass_false_as = f"--{parameter.name}=false"

    return parameter


def parse_input(key: str, value: Any) -> Input:
    if isinstance(value, dict):
        value["name"] = key
        return Input.parse(value)

    # Check and ignore the local path file
    checked_value = [val for val in listify(value) if not is_local_file_path(val)]

    has_wildcards = any("*" in uri for uri in checked_value)

    keep_directories = KeepDirectories.SUFFIX if has_wildcards else KeepDirectories.NONE
    return Input(
        name=key,
        default=checked_value if checked_value else None,
        optional=not checked_value,
        keep_directories=keep_directories,
    )


def generate_config(
    *,
    relative_source_path: str,
    step: str,
    image: str,
    parameters: ParameterDict,
    inputs: InputDict,
    environment: Optional[str] = None,
    multifile: bool = False,
    upload_store: Optional[str] = None,
) -> Config:
    step_obj = generate_step(
        relative_source_path=relative_source_path,
        step=step,
        image=image,
        parameters=parameters,
        inputs=inputs,
        environment=environment,
        multifile=multifile,
        upload_store=upload_store,
    )
    config = Config()
    config.steps[step_obj.name] = step_obj
    return config


def get_source_relative_path(source_path: str, config_path: str) -> str:
    """Return path of a source file relative to config file path
    :param source_path: Path of the Python source code file
    :param config_path: Path of the valohai.yaml config file
    :return: Path of the source code file relative to the config file
    Example:
        config_file_path: /herpderp/valohai.yaml
        source_file_path: /herpderp/somewhere/underneath/test.py
        return: ./somewhere/underneath/test.py
    Ultimately used for creating command with correct relative path in valohai.yaml:
        python ./somewhere/underneath/test.py {parameters}
    """
    relative_source_dir = os.path.relpath(
        os.path.dirname(os.path.abspath(source_path)),
        os.path.dirname(os.path.abspath(config_path)),
    )
    return os.path.join(relative_source_dir, os.path.basename(source_path))


def parse_config_from_source(source_path: str, config_path: str) -> Config:
    parsed = parse(get_source_code(source_path))
    if not parsed.step:
        raise ValueError("Source is missing a call to valohai.prepare()")
    relative_source_path = get_source_relative_path(source_path, config_path)
    return generate_config(
        relative_source_path=relative_source_path,
        step=parsed.step,
        image=parsed.image or DEFAULT_DOCKER_IMAGE,
        environment=parsed.environment,
        parameters=parsed.parameters,
        inputs=parsed.inputs,
        multifile=parsed.multifile,
        upload_store=parsed.upload_store,
    )


def get_parameter_type_name(name: str, value: Any) -> str:
    if isinstance(value, bool):
        return "flag"
    if isinstance(value, float):
        return "float"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, str):
        return "string"

    raise ValueError(
        f"Unrecognized parameter type for {name}={value}. "
        f"Supported Python types are float, int, string and bool."
    )


def get_command(relative_source_path: str, multifile: bool) -> List[str]:
    if is_notebook_path(relative_source_path):
        return get_notebook_command(relative_source_path)

    if multifile:
        python_invoke = "python {source-path} {parameters}"
    else:
        python_invoke = f"python {relative_source_path} {{parameters}}"

    return [
        "pip install -r requirements.txt",
        python_invoke,
    ]


def get_source_code(source_path: str) -> str:
    with open(source_path) as source_file:
        file_contents = source_file.read()
        if is_notebook_path(source_path):
            notebook_content = parse_ipynb(file_contents)
            return get_notebook_source_code(notebook_content)
        return file_contents


def is_notebook_path(source_path: str) -> bool:
    filename, extension = os.path.splitext(source_path)
    return extension == ".ipynb"
