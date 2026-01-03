import requests
from bs4 import BeautifulSoup
from google.adk.agents.llm_agent import Agent
from loguru import logger


def extract_webpage(url: str) -> dict:
    try:
        response = requests.get(url, timeout=25)
        logger.info(f"fetched url={url}, status code={response.status_code}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all meta tags
        meta_tags = {}
        for tag in soup.find_all("meta"):
            # Prefer 'name', then 'property', then 'http-equiv'
            key = tag.get("name") or tag.get("property") or tag.get("http-equiv")
            value = tag.get("content")
            if key and value:
                meta_tags[key] = value

        metadata = {"title": soup.title.string if soup.title else "", **meta_tags}

        # Extract body text
        body = soup.body.get_text(separator="\n", strip=True) if soup.body else ""

        return {"status": "success", "body": body, "url": url, "metadata": metadata}
    except requests.RequestException as e:
        return {"status": "error", "error": str(e)}


root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A helpful assistant for user questions.",
    instruction="Answer user questions to the best of your knowledge",
    tools=[extract_webpage],
)
