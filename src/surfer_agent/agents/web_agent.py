import requests
from bs4 import BeautifulSoup


class WebAgent:
    def __init__(self):
        pass

    def surf_web(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text content from the webpage
        text_content = soup.get_text(separator=" ", strip=True)

        return text_content
