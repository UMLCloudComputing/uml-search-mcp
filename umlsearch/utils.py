"""
Utils
"""

import os
import httpx
import logging
from playwright.async_api import async_playwright

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


async def process_url(client: httpx.AsyncClient, url: str, docling_base_address: str):
    """
    Processes a URL into markdown data using Docling
    """
    payload = {
        "options": {
            "from_formats": ["html"],
            "to_formats": ["md"],
            "pipeline": "standard",
            "do_table_structure": "true",
        },
        "sources": [{"url": url, "kind": "http"}],
    }

    logger.debug("Making URL processing request to Docling...")
    response = await client.post(
        f"http://{docling_base_address}/v1/convert/source", json=payload
    )

    if response.status_code == 200:
        content = response.json()
        if content["status"] == "success":
            logger.debug("Docling response successfully processed")
            return content["document"].get("md_content")
        else:
            logger.error(f"Docling failed to process the url: {content['errors']}")
            return ""
    else:
        logger.error(f"Error in docling response: status code: {response.status_code}")
        return ""
