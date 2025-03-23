import re
from urllib.parse import urlparse, urlunparse


# https://chatgpt.com/c/67d733a0-4be4-8005-bf52-fb9ba32487c2
def normalize_url(url: str) -> str:
    return urlunparse(
        urlparse(url)._replace(
            query="",
            fragment="",
        ),
    )


def url_to_filename(
    url: str,
    max_length: int = 255,
) -> str:
    # Remove the URL scheme (http://, https://)
    filename = re.sub(r"^https?://", "", url)

    # Replace unwanted characters with an underscore
    filename = re.sub(r"[^\w\s-]", "_", filename)

    # Replace slashes with a hyphen to preserve some structure
    filename = re.sub(r"\/", "-", filename)

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")

    # Ensure the filename length is not too long
    if len(filename) > max_length:
        filename = filename[:max_length]

    return filename
