from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv
import os
from rich import print

load_dotenv()   

tavily = TavilyClient()

@tool
def web_search(query : str)-> str:
    """Search the web for the given query and return a  information on a topic . Returns Titles , URLs and snippets."""
    result = tavily.search(query=query, max_results=3)
    output = []
    for r in result['results']:
        title = r['title']
        url = r['url']
        content  = r['content']
        output.append(f"Title: {title}\nURL: {url}\nContent: {content}\n")
    return "\n".join(output)


# print(web_search.invoke("Give me the latest news on the war"))

@tool
def web_scrape(url: str) -> str:
    """Scrape the content of a web page given its URL and return the text content."""
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator="", strip=True)[:2000]

    except Exception as e:
        return f"Couldnot scrape url : {str(e)}"


# print(web_scrape.invoke("https://timesofindia.indiatimes.com/"))


