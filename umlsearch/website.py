import logging
from typing import TypedDict
from fastmcp.server.context import Context

from bs4 import BeautifulSoup
from .utils import get_html

SEARCH_URL = "https://www.uml.edu/search/"

logger = logging.getLogger(__name__)


class SearchResultItem(TypedDict):
    title: str
    detail: str
    url: str


async def query_website(query: str, top_k: int):
    """
    Query the UMass Lowell Website
    """
    responses = {"total": 0, "results": {}}
    html = await get_html(SEARCH_URL + f"?query={query}")
    soup = BeautifulSoup(html, "lxml")

    if top_k > 0:
        elements = soup.select("div.c-search-result-item__inside", limit=top_k)
    else:
        elements = soup.select("div.c-search-result-item__inside")

    for element in elements:
        title_div = element.find("div", class_="title")
        title = title_div.get_text(strip=True) if title_div else None

        detail_div = element.find("div", class_=lambda x: x == "detail")
        detail = detail_div.get_text(strip=True) if title_div else None

        url_div = element.find("div", class_="detail url")
        if url_div and url_div.find("a"):
            url = url_div.find("a")["href"]
        elif title_div and title_div.find("a"):
            url = title_div.find("a")["href"]
        else:
            url = None

        responses["results"][responses["total"]] = {
            "title": title,
            "detail": detail,
            "url": url,
        }
        responses["total"] += 1

    return responses
