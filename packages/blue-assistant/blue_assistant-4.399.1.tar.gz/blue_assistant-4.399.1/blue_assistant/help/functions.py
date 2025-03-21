from typing import List

from blue_options.terminal import show_usage, xtra
from abcli.help.generic import help_functions as generic_help_functions

from blue_assistant import ALIAS
from blue_assistant.help.hue import help_functions as help_hue
from blue_assistant.help.RAG import help_functions as help_RAG
from blue_assistant.help.script import help_functions as help_script
from blue_assistant.help.web import help_functions as help_web


def help_browse(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "actions|repo"

    return show_usage(
        [
            "@assistant",
            "browse",
            f"[{options}]",
        ],
        "browse blue_assistant.",
        mono=mono,
    )


help_functions = generic_help_functions(plugin_name=ALIAS)

help_functions.update(
    {
        "browse": help_browse,
        "hue": help_hue,
        "RAG": help_RAG,
        "script": help_script,
        "web": help_web,
    }
)
