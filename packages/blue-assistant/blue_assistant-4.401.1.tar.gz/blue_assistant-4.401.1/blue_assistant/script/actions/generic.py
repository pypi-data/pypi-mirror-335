from blueness import module

from blue_assistant import NAME
from blue_assistant.script.repository.base.root import RootScript
from blue_assistant.logger import logger

NAME = module.name(__file__, NAME)


def generic_action(
    script: RootScript,
    node_name: str,
) -> bool:
    logger.info(f"{NAME}: @ {node_name} ...")
    return True
