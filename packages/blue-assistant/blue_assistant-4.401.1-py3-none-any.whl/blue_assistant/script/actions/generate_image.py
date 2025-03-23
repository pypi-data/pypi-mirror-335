from blueness import module
from openai_commands.image_generation import api

from blue_assistant import NAME
from blue_assistant.env import (
    BLUE_ASSISTANT_IMAGE_DEFAULT_MODEL,
    BLUE_ASSISTANT_IMAGE_DEFAULT_SIZE,
    BLUE_ASSISTANT_IMAGE_DEFAULT_QUALITY,
)
from blue_assistant.script.repository.base.root import RootScript
from blue_assistant.logger import logger

NAME = module.name(__file__, NAME)


# https://platform.openai.com/docs/guides/images
def generate_image(
    script: RootScript,
    node_name: str,
) -> bool:
    logger.info(f"{NAME}: @ {node_name} ...")

    filename = f"{node_name}.png"

    success, _ = api.generate_image(
        prompt=script.apply_vars(script.nodes[node_name]["prompt"]),
        filename=filename,
        object_name=script.object_name,
        model=BLUE_ASSISTANT_IMAGE_DEFAULT_MODEL,
        quality=(BLUE_ASSISTANT_IMAGE_DEFAULT_QUALITY if script.test_mode else "hd"),
        size=(BLUE_ASSISTANT_IMAGE_DEFAULT_SIZE if script.test_mode else "1792x1024"),
        sign_with_prompt=False,
        footer=[
            script.nodes[node_name].get(
                "summary_prompt",
                script.nodes[node_name]["prompt"],
            )
        ],
        verbose=script.verbose,
    )

    if success:
        script.nodes[node_name]["filename"] = filename

    return success
