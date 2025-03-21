from typing import Dict, Callable

from blue_assistant.script.repository.base.root import RootScript
from blue_assistant.script.actions.generic import generic_action
from blue_assistant.script.actions.generate_image import generate_image
from blue_assistant.script.actions.generate_text import generate_text
from blue_assistant.script.actions.web_crawl import web_crawl


dict_of_actions: Dict[str, Callable[[RootScript, str], bool]] = {
    "generic": generic_action,
    "generate_image": generate_image,
    "generate_text": generate_text,
    "web_crawl": web_crawl,
}
