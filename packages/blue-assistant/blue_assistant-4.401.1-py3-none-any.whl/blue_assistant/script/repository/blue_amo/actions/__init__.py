from typing import Dict, Callable

from blue_assistant.script.repository.base.classes import BaseScript
from blue_assistant.script.repository.blue_amo.actions import (
    setting_frame_prompts,
    stitching_the_frames,
)


dict_of_actions: Dict[str, Callable[[BaseScript, str], bool]] = {
    "setting_frame_prompts": setting_frame_prompts.setting_frame_prompts,
    "stitching_the_frames": stitching_the_frames.stitching_the_frames,
}
