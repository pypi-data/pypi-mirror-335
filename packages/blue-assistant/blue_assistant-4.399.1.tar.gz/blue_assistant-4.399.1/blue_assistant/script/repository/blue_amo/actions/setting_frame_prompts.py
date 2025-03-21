from blueness import module

from blue_assistant import NAME
from blue_assistant.script.repository.base.classes import BaseScript
from blue_assistant.logger import logger

NAME = module.name(__file__, NAME)


def setting_frame_prompts(
    script: BaseScript,
    node_name: str,
) -> bool:
    logger.info(NAME)

    list_of_frame_prompts = script.nodes["slicing_into_frames"]["output"].split("---")
    if len(list_of_frame_prompts) != script.vars["frame_count"]:
        logger.warning(
            "{} != {}, frame count doesn't match, bad AI! 😁".format(
                len(list_of_frame_prompts),
                script.vars["frame_count"],
            )
        )

    list_of_frame_prompts += script.vars["frame_count"] * [""]

    for index in range(script.vars["frame_count"]):
        node_name = f"generating_frame_{index+1:03d}"

        script.nodes[node_name]["summary_prompt"] = list_of_frame_prompts[index]

        script.nodes[node_name]["prompt"] = (
            script.nodes[node_name]["prompt"]
            .replace(":::story_so_far", " ".join(list_of_frame_prompts[:index]))
            .replace(":::story_of_this_frame", list_of_frame_prompts[index])
        )

    return True
