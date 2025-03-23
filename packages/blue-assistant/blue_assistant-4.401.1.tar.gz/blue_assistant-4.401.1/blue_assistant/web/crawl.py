from typing import List, Dict, Tuple

from blueness import module
from blue_options.logger import log_dict, log_list
from blue_objects import file
from blue_objects import objects
from blue_objects.metadata import get_from_object, post_to_object

from blue_assistant import NAME
from blue_assistant.web.fetch import fetch_links_and_text
from blue_assistant.web.functions import url_to_filename
from blue_assistant.logger import logger

NAME = module.name(__file__, NAME)


def crawl_list_of_urls(
    seed_urls: List[str],
    object_name: str,
    max_iterations: int = 10,
    verbose: bool = False,
    cache_prefix: str = "",
) -> Tuple[bool, Dict[str, str]]:
    logger.info(
        "{}.crawl_list_of_urls({}): {} -> {}".format(
            NAME,
            len(seed_urls),
            ", ".join(seed_urls),
            object_name,
        )
    )

    queue: List[str] = list(
        set(
            seed_urls
            + get_from_object(
                object_name,
                f"{cache_prefix}_queue",
                [],
            )
        )
    )
    log_list(logger, "queue:", queue, "url(s)")

    crawl_cache: Dict[str, str] = get_from_object(
        object_name,
        f"{cache_prefix}_cache",
        {},
    )
    log_dict(logger, "loaded cache:", crawl_cache, "url(s)")

    iteration: int = 0
    while queue:
        url = queue[0]
        queue = queue[1:]

        logger.info(
            "{} [#{:,}/{:,}]: {} ".format(
                "✅ " if url in crawl_cache else "🔗 ",
                iteration,
                len(queue),
                url,
            )
        )
        if url in crawl_cache:
            continue

        url_summary = fetch_links_and_text(
            url=url,
            verbose=verbose,
        )
        content_type = url_summary.get("content_type", "unknown")

        if "html" in content_type:
            if not file.save_yaml(
                filename=objects.path_of(
                    object_name=object_name,
                    filename="{}_cache/{}.yaml".format(
                        cache_prefix,
                        url_to_filename(url),
                    ),
                ),
                data=url_summary,
            ):
                return False, {}

        crawl_cache[url] = content_type

        queue = (
            queue
            + url_summary.get("list_of_urls", [])
            + [
                url
                for url in url_summary.get("list_of_ignored_urls", [])
                if any(url.startswith(url_prefix) for url_prefix in seed_urls)
            ]
        )
        queue = list({url for url in queue if url not in crawl_cache.keys()})

        iteration += 1
        if max_iterations != -1 and iteration >= max_iterations:
            logger.warning(f"max iteration of {max_iterations} reached.")
            break

    if queue:
        logger.warning(f"queue: {len(queue)}")

    if not (
        post_to_object(
            object_name,
            f"{cache_prefix}_cache",
            crawl_cache,
        )
        and post_to_object(
            object_name,
            f"{cache_prefix}_queue",
            queue,
        )
    ):
        return False, {}

    log_dict(logger, "crawled", crawl_cache, "url(s)")
    log_list(logger, "queue:", queue, "url(s)")

    return True, crawl_cache
