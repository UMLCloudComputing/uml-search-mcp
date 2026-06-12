from bs4 import BeautifulSoup
from typing import Optional, TypedDict
from .utils import get_html

SEARCH_URL = "https://www.uml.edu/search/?type=places"


class PlaceSearchResultItem(TypedDict):
    name: str
    address: str
    map_url: str
    phone_number: Optional[str]


async def query_place(query: str, top_k: int):
    """Process search query for a place at UMass Lowell"""
    search_url = SEARCH_URL + f"&query={query}"

    responses = {"total": 0, "results": {}}

    # Get the html response
    html = await get_html(search_url)
    soup = BeautifulSoup(html, "lxml")

    if top_k > 0:
        elements = soup.select("div.c-search-result-item-places", limit=top_k)
    else:
        elements = soup.select("div.c-search-result-item-places")

    for element in elements:
        title_link = (
            element.find("div", class_="title").find("a")
            if element.find("div", class_="title")
            else None
        )
        name = title_link.get_text(strip=True) if title_link else None
        url = title_link["href"] if title_link and title_link.has_attr("href") else None

        # 2. Extract Details (Address and Phone)
        # There can be multiple 'detail' divs; we need to distinguish them
        detail_divs = element.find_all("div", class_="detail")

        address = None
        phone = None

        for detail in detail_divs:
            # Check if this detail contains a phone link
            phone_link = detail.find("a", href=lambda x: x and x.startswith("tel:"))
            if phone_link:
                phone = phone_link.get_text(strip=True)
            else:
                # If it's not a phone, it's the address
                # Some addresses are wrapped in <p> tags or escaped HTML
                address_text = detail.get_text(strip=True)
                if address_text:
                    address = address_text

        responses["results"][responses["total"]] = {
            "name": name,
            "address": address,
            "map_url": f"https://uml.edu{url}",
            "phone_number": phone,
        }
        responses["total"] += 1

    return responses
