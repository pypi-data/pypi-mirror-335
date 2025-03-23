from blue_objects import file, path

from blue_assistant.script.repository.base.classes import BaseScript
from blue_assistant.script.repository.orbital_data_explorer.actions import (
    dict_of_actions,
)


class OrbitalDataExplorerScript(BaseScript):
    name = path.name(file.path(__file__))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dict_of_actions.update(dict_of_actions)
