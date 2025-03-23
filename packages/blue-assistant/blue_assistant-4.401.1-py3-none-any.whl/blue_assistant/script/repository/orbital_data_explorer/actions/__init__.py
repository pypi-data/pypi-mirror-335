from typing import Dict, Callable

from blue_assistant.script.repository.base.classes import BaseScript
from blue_assistant.script.repository.orbital_data_explorer.actions import (
    expanding_the_extractions,
)


dict_of_actions: Dict[str, Callable[[BaseScript, str], bool]] = {
    "expanding_the_extractions": expanding_the_extractions.expanding_the_extractions,
}
