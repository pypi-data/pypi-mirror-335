from blueness import module

from blue_options.logger import log_list

from blue_assistant import NAME
from blue_assistant.web.crawl import crawl_list_of_urls
from blue_assistant.web.functions import normalize_url
from blue_assistant.script.repository.base.root import RootScript
from blue_assistant.logger import logger


NAME = module.name(__file__, NAME)


def web_crawl(
    script: RootScript,
    node_name: str,
) -> bool:
    logger.info(f"{NAME}: @ {node_name} ...")

    seed_url_var_name = script.nodes[node_name].get("seed_urls", "")
    if not isinstance(seed_url_var_name, str):
        logger.error(f"{node_name}: seed_urls must be a string.")
        return False
    if not seed_url_var_name:
        logger.error(f"{node_name}: seed_urls not found.")
        return False

    # to allow both :::<var-name> and <var-name> - for convenience :)
    if seed_url_var_name.startswith(":::"):
        seed_url_var_name = seed_url_var_name[3:].strip()

    if seed_url_var_name not in script.vars:
        logger.error(f"{node_name}: {seed_url_var_name}: seed_urls not found in vars.")
        return False
    seed_urls = list({normalize_url(url) for url in script.vars[seed_url_var_name]})
    log_list(logger, "using", seed_urls, "seed url(s)")

    success, crawl_cache = crawl_list_of_urls(
        seed_urls=seed_urls,
        object_name=script.object_name,
        max_iterations=script.nodes[node_name]["max_iterations"],
        cache_prefix=node_name,
    )

    script.nodes[node_name]["output"] = crawl_cache

    return success
