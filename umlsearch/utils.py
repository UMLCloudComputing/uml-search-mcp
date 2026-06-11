"""
Utils
"""

import os
import httpx
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

DOCLING_BASE_URL = os.getenv("DOCLING_BASE_URL")

logger = logging.getLogger(__name__)


# Return html from a rendered webpage
async def get_html(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()
    return html


async def process_url(client: httpx.AsyncClient, url: str):
    """
    Processes a URL into markdown data using Docling
    """
    payload = {
        "options": {
            "from_formats": ["html"],
            "to_formats": ["md"],
            "table_mode": "accurate",
            "pipeline": "standard",
            "do_table_structure": "true",
        },
        "sources": [{"url": url, "kind": "http"}],
        "target": "inbody",
    }
    logger.debug("Making URL processing request to Docling...")
    response = await client.post(
        f"http://{DOCLING_BASE_URL}/v1/convert/source", payload
    )

    if response.status == 200:
        if response["status"] == "success":
            logger.debug("Docling response successfully processed")
            return response["document"].get("md_content")
        else:
            logger.error(f"Docling failed to process the url: {response['errors']}")
            return ""
    else:
        logger.error(f"Error in docling response: status code: {response.status}")
        return ""
