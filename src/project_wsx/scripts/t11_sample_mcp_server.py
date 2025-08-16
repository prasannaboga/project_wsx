#!/usr/bin/env python

import argparse
import asyncio
import logging
import os
import sys
from email import parser
from pathlib import Path

import aiohttp
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

log_dir = Path(__file__).resolve().parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / "development.log"
logging.basicConfig(
    filename=log_file,
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.DEBUG,
)

mcp = FastMCP(
    "sample_mcp_server", host="127.0.0.1", port=8001, log_level="DEBUG", debug=True
)


@mcp.tool()
async def greet(name: str) -> dict:
    """Greet a user by name."""
    return {"message": f"Hello, {name}! Welcome to MCP....!"}


@mcp.tool()
async def add_numbers(a: float, b: float) -> dict:
    """Add two numbers and return the result."""
    result = a + b + 2
    return {"a": a, "b": b, "sum": result}


@mcp.tool()
async def extract_metadata(url: str) -> dict:
    logging.info(f"extract_metadata called with params: {{'url': {url}}}")
    """Extract metadata from the specified URL."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                title = (
                    soup.title.string.strip()
                    if soup.title and soup.title.string
                    else "No title found"
                )

                description = "No description found"
                meta_desc = soup.find(
                    "meta", attrs={"name": "description"}
                ) or soup.find("meta", attrs={"property": "og:description"})
                if meta_desc and meta_desc.get("content"):
                    description = meta_desc.get("content")

                keywords = None
                meta_keywords = soup.find("meta", attrs={"name": "keywords"})
                if meta_keywords and meta_keywords.get("content"):
                    keywords = meta_keywords.get("content").strip()

                og_data = {}
                for tag in soup.find_all("meta"):
                    if tag.get("property", "").startswith("og:"):
                        og_data[tag.get("property")] = tag.get("content", "").strip()

                favicon = None
                icon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
                if icon_link and icon_link.get("href"):
                    favicon = icon_link.get("href")

                canonical = None
                canonical_link = soup.find("link", rel="canonical")
                if canonical_link and canonical_link.get("href"):
                    canonical = canonical_link.get("href")

                return {
                    "url": url,
                    "title": title,
                    "description": description,
                    "keywords": keywords,
                    "favicon": favicon,
                    "canonical": canonical,
                    "open_graph": og_data,
                }
            else:
                return {
                    "url": url,
                    "error": f"Failed to fetch URL: HTTP {response.status}",
                }


@mcp.tool()
def send_email(mail_subject: str, mail_body: str, to_email: str):
    logging.info(
        f"send_email called with params: {{'mail_subject': {mail_subject}, 'mail_body': {mail_body}, 'to_email': {to_email}}}"
    )
    try:
        mailgun_domain = os.getenv("MAILGUN_DOMAIN")
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        from_email = os.getenv("FROM_EMAIL")

        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": from_email,
                "to": [to_email],
                "subject": mail_subject,
                "text": mail_body,
            },
        )
        response.raise_for_status()
        logging.info("Email sent successfully")
        return {"status": "success"}

    except Exception as e:
        logging.exception("Failed to send email")
        return {"status": "error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", help="Transport method.")
    args = parser.parse_args()
    transport = "stdio"
    if args.transport == "streamable-http":
        print(f"Options provided: {args.transport}", file=sys.stderr)
        transport = "streamable-http"

    logging.info(f"Starting MCP server with transport: {transport}")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
