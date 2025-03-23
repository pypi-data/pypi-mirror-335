from typing import List

from blue_options.terminal import show_usage, xtra


def help_query_pdf(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "".join(
        [
            xtra("~download,dryrun,", mono=mono),
            "filename=<filename.pdf>",
            xtra(",~upload", mono=mono),
        ]
    )

    return show_usage(
        [
            "@RAG",
            "query_pdf",
            f"[{options}]",
            "[.|<object-name>]",
            "<question>",
        ],
        "query <question> in <object-name>/<filename.pdf>.",
        mono=mono,
    )


help_functions = {
    "query_pdf": help_query_pdf,
}
