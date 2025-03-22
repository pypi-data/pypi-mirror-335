import copy
from typing import TypeVar

from valohai_yaml.objs.base import Item
from valohai_yaml.objs.config import Config
from valohai_yaml.objs.step import Step
from valohai_yaml.utils.merge import merge_dicts, merge_simple

from valohai.consts import DEFAULT_DOCKER_IMAGE

MergeT = TypeVar("MergeT", Config, Step, Item)


def python_to_yaml_merge_strategy(original: MergeT, parsed: MergeT) -> MergeT:
    """Merging strategy in the valohai-utils AST parser use-case

    :param original: Original Item from an existing valohai.yaml
    :param parsed: New Item parsed from a .py file using valohai-utils AST parser
    :return: Merged Item
    """
    if isinstance(parsed, Config) and isinstance(original, Config):
        return _merge_config(original, parsed)
    if isinstance(parsed, Step) and isinstance(original, Step):
        return _merge_step(original, parsed)
    return original.merge_with(parsed)


def _merge_config(original: Config, parsed: Config) -> Config:
    """Merging strategy for Configs in the valohai-utils AST parser use-case

    :param original: Original Config from an existing valohai.yaml
    :param parsed: New Config parsed from a .py file using valohai-utils AST parser
    :return: Merged Config
    """
    result = copy.deepcopy(original)
    for key, step in parsed.steps.items():
        if key in result.steps:
            original_step = original.steps[key]
            result.steps[key] = original_step.merge_with(
                step, python_to_yaml_merge_strategy
            )
        else:
            result.steps[key] = step
    return result


def _merge_step(original: Step, parsed: Step) -> Step:
    """Merging strategy for Steps in the valohai-utils AST parser use-case

    :param original: Original Step from an existing valohai.yaml
    :param parsed: New Step parsed from a .py file using valohai-utils AST parser
    :return: Merged Step
    """

    # AST parser overrides parameters, inputs, source-path and step name.
    # Respect the original values for everything else.
    result = Step(
        name=parsed.name,
        image=original.image,
        command=original.command,
        environment=original.environment,
        description=original.description,
        outputs=original.outputs,
        mounts=original.mounts,
        source_path=parsed.source_path,
    )

    # If user first types "learning_rage", creates config, and finally fixes the typo,
    # they don't want to end up with both "learning_rage" and "learning_rate" after the merge.
    # So only merge parameters and inputs that are part of the new config (skip_missing_b=True)
    result.parameters = merge_dicts(
        a=original.parameters,
        b=parsed.parameters,
        merger=merge_simple,
        copier=copy.deepcopy,
        skip_missing_b=True,
    )
    result.inputs = merge_dicts(
        a=original.inputs,
        b=parsed.inputs,
        merger=merge_simple,
        copier=copy.deepcopy,
        skip_missing_b=True,
    )

    if parsed.image is not None and parsed.image != DEFAULT_DOCKER_IMAGE:
        result.image = parsed.image

    if parsed.environment is not None:
        result.environment = parsed.environment

    return result
