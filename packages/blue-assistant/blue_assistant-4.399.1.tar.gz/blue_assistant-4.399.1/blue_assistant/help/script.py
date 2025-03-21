from typing import List
from functools import reduce

from blue_options.terminal import show_usage, xtra

from blue_assistant.script.repository import list_of_script_names
from blue_assistant.script.repository.functions import get_script_versions


def help_list(
    tokens: List[str],
    mono: bool,
) -> str:
    args = [
        "[--delim +]",
        "[--log 0]",
    ]

    return show_usage(
        [
            "@assistant",
            "script",
            "list",
        ]
        + args,
        "list scripts.",
        mono=mono,
    )


def help_run(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("~download,dryrun,~upload", mono=mono)

    script_options = "script=<name>,version=<version>"

    args = [
        "[--test_mode 1]",
        "[--verbose 1]",
        "[--runnable <~node_1,~node_2>]",
    ]

    def script_version_details(script_name: str) -> List[str]:
        list_of_script_versions = get_script_versions(script_name)

        return (
            [
                "{}: {}".format(
                    script_name,
                    " | ".join(list_of_script_versions),
                )
            ]
            if list_of_script_versions
            else []
        )

    return show_usage(
        [
            "@assistant",
            "script",
            "run",
            f"[{options}]",
            f"[{script_options}]",
            "[-|<object-name>]",
        ]
        + args,
        "run <script-name>/<script-version> in <object-name>.",
        {
            "name: {}".format(" | ".join(list_of_script_names)): reduce(
                lambda x, y: x + y,
                [
                    script_version_details(script_name)
                    for script_name in list_of_script_names
                ],
                [],
            )
        },
        mono=mono,
    )


help_functions = {
    "list": help_list,
    "run": help_run,
}
