from typing import Tuple, Type

from blue_assistant.script.repository import list_of_script_classes
from blue_assistant.script.repository.base.classes import BaseScript
from blue_assistant.logger import logger


def load_script(
    script_name: str,
    object_name: str,
    script_version: str = "base",
    test_mode: bool = False,
    log: bool = True,
    verbose: bool = False,
    save_graph: bool = True,
) -> Tuple[bool, BaseScript]:
    found: bool = False
    script_class: Type[BaseScript] = BaseScript
    for script_class_option in list_of_script_classes:
        if script_class_option.name == script_name:
            found = True
            script_class = script_class_option
            break

    if not found:
        logger.error(f"{script_name}: script not found.")

    script = script_class(
        script_version=script_version,
        object_name=object_name,
        test_mode=test_mode,
        log=log,
        verbose=verbose,
        save_graph=save_graph,
    )

    return found and script.valid, script
