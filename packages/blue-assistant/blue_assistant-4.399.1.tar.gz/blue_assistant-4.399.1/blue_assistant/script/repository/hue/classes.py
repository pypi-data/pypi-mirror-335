from blue_objects import file, path

from blue_assistant.script.repository.base.classes import BaseScript


class HueScript(BaseScript):
    name = path.name(file.path(__file__))
