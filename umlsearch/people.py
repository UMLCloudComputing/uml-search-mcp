from bs4 import BeautifulSoup
from typing import TypedDict
from .utils import get_html

SEARCH_URL = "https://www.uml.edu/search/?type=people"


class PeopleSearchResultItem(TypedDict):
    name: str
    role: str
    department: str
    building: str
    email: str
    phone_number: str


async def query_people(query: str, top_k: int):
    """Process search query from a provided url"""
    url = SEARCH_URL + f"&query={query}"

    responses = {"total": 0, "results": {}}

    # Get the html response
    html = await get_html(url)
    soup = BeautifulSoup(html, "lxml")

    if top_k > 0:
        elements = soup.select("div.c-search-result-item-people", limit=top_k)
    else:
        elements = soup.select("div.c-search-result-item-people")

    for element in elements:
        name_div = element.find("div", class_="title")
        name = name_div.get_text(strip=True) if name_div else None

        role_div = element.find("div", class_="subtitle")
        role = role_div.get_text(strip=True) if role_div else None

        detail_divs = element.find_all("div", class_="detail")

        department = None
        building = None
        email = None
        phone = None

        # Process the first detail block (Department and Building)
        if len(detail_divs) > 0:
            dept_bldg_divs = detail_divs[0].find_all("div")
            if len(dept_bldg_divs) > 0:
                department = dept_bldg_divs[0].get_text(strip=True)
            if len(dept_bldg_divs) > 1:
                building = dept_bldg_divs[1].get_text(strip=True)

        # Process the second detail block (Email and Phone)
        if len(detail_divs) > 1:
            contact_divs = detail_divs[1].find_all("div")
            if len(contact_divs) > 0:
                email_link = contact_divs[0].find("a")
                email = (
                    email_link.get_text(strip=True)
                    if email_link
                    else contact_divs[0].get_text(strip=True)
                )
            if len(contact_divs) > 1:
                phone_link = contact_divs[1].find("a")
                phone = (
                    phone_link.get_text(strip=True)
                    if phone_link
                    else contact_divs[1].get_text(strip=True)
                )
        responses["results"][responses["total"]] = {
            "name": name,
            "role": role,
            "department": department,
            "building": building,
            "email": email,
            "phone_number": phone,
        }
        responses["total"] += 1

    return responses
