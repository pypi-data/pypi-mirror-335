import copy

from blueness import module
from blue_objects import file, path

from blue_assistant import NAME
from blue_assistant.script.repository.base.root import RootScript
from blue_assistant.script.actions import dict_of_actions
from blue_assistant.logger import logger


NAME = module.name(__file__, NAME)


class BaseScript(RootScript):
    name = path.name(file.path(__file__))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dict_of_actions = copy.deepcopy(dict_of_actions)
