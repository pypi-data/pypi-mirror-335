import re
import json
from typing import List, Tuple, Union, Any

from scrapy.utils.url import parse_url

_URL_PATTERN = r"^https?://[^:/\s]+(:\d{1,5})?(/[^\s]*)*(#[^\s]*)?$"


def get_domain(url: str) -> str:
    return re.sub(r"^www\d*\.", "", parse_url(url).netloc)


def load_url_list(urls: str) -> List[Union[str, Tuple[str, Any]]]:
    result = []
    bad_urls = []
    for line in urls.split("\n"):
        if not (line := line.strip()):
            continue
        
        # Split the line by tab, multiple spaces, or comma
        parts = re.split(r'\t|\s{2,}|,', line, 1)
        url = parts[0].strip()
        
        if not re.search(_URL_PATTERN, url):
            bad_urls.append(url)
            continue
        
        if len(parts) > 1 and parts[1].strip():
            # If there's a second column, try to parse it as JSON
            try:
                metadata = json.loads(parts[1].strip())
                result.append((url, metadata))
            except json.JSONDecodeError:
                # If parsing as JSON fails, use the raw string as metadata
                result.append((url, parts[1].strip()))
        else:
            # If there's only one column, use the URL alone with no metadata
            result.append(url)
    
    if bad_urls:
        bad_url_list = "\n".join(bad_urls)
        raise ValueError(
            f"URL list contained the following invalid URLs:\n{bad_url_list}"
        )
    return result
