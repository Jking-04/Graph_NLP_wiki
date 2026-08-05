
import os
import wikipediaapi

from urllib.parse import urlparse,unquote


PROJECT_NAME = "Graph_NLP_wiki"
EMAIL = os.getenv("WIKIMEDIA_API_EMAIL")


def url_to_title(http_url):
    path = urlparse(http_url).path
    title = path.split("/wiki/")[-1]
    return unquote(title)

def scrape_wiki(http_url):
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent=f'{PROJECT_NAME} ({EMAIL})' if EMAIL else PROJECT_NAME,
        language='en'
        )

    title = url_to_title(http_url)

    page_py = wiki_wiki.page(title=title)

    text = page_py.summary

    for section in page_py.sections:
        if section.title not in ["References","Bibliography","External links"]:
            text += section.text

    return text