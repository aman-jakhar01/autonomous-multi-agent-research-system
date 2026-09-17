from urllib.parse import urlparse
import hashlib

from models.schemas import Source


def create_source(
    title: str,
    url: str,
    content: str
) -> Source:

    """
    Convert a raw Tavily result into
    our standardized Source object.
    """

    # ---------------------------------------------------------
    # Extract domain
    # ---------------------------------------------------------

    parsed_url = urlparse(url)

    domain = parsed_url.netloc


    # ---------------------------------------------------------
    # Create a stable ID from the URL
    # ---------------------------------------------------------

    source_id = hashlib.md5(
        url.encode("utf-8")
    ).hexdigest()[:12]


    # ---------------------------------------------------------
    # Create Source object
    # ---------------------------------------------------------

    return Source(

        id=source_id,

        title=title,

        url=url,

        content=content,

        domain=domain
    )