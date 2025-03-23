from typing import List

from blue_options.terminal import show_usage, xtra


def help_crawl(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("~download,dryrun,~upload", mono=mono)

    args = [
        "[--max_iterations <100000>]",
    ]

    return show_usage(
        [
            "@web",
            "crawl",
            f"[{options}]",
            "<url-1>+<url-2>+<url-3>",
            "[-|<object-name>]",
        ]
        + args,
        "crawl the urls.",
        mono=mono,
    )


def help_fetch(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("dryrun,~upload", mono=mono)

    return show_usage(
        [
            "@web",
            "fetch",
            f"[{options}]",
            "<url>",
            "[-|<object-name>]",
        ],
        "fetch <url>.",
        mono=mono,
    )


help_functions = {
    "crawl": help_crawl,
    "fetch": help_fetch,
}
