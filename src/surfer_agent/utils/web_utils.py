import requests
import sys
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os


def fetch_page(url, headers=None):
    """Fetch the page content from the given URL."""
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def prettify_and_print(html_content):
    """Prettify and print the fetched page."""
    soup = BeautifulSoup(html_content, "html.parser")
    print(soup.prettify())


def get_links_with_context(html_content):
    """Identify links on the fetched page and return them as a list with context."""
    soup = BeautifulSoup(html_content, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        link = {
            "url": a["href"],
            "text": a.get_text(strip=True),
            "context": a.parent.get_text(strip=True),
        }
        links.append(link)
    return links


def save_page_to_json(url, html_content, headers=None):
    """Save browsed pages to JSON files with metadata."""
    data = {
        "url": url,
        "date_accessed": datetime.now().isoformat(),
        "browser_agent": headers.get("User-Agent") if headers else None,
        "content": html_content,
    }

    filename = f"page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("saved_pages", exist_ok=True)
    filepath = os.path.join("saved_pages", filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Page saved to {filepath}")


def get_images(html_content):
    """Identify and list images on the fetched page."""
    soup = BeautifulSoup(html_content, "html.parser")
    images = []
    for img in soup.find_all("img"):
        image = {
            "src": img.get("src"),
            "alt": img.get("alt"),
            "title": img.get("title"),
        }
        images.append(image)
    return images


# Example usage
if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    html_content = fetch_page(url, headers)

    print("Prettified HTML:")
    prettify_and_print(html_content)

    print("\nLinks with context:")
    links = get_links_with_context(html_content)
    for link in links:
        print(f"URL: {link['url']}")
        print(f"Text: {link['text']}")
        print(f"Context: {link['context']}")
        print()

    save_page_to_json(url, html_content, headers)

    print("\nImages:")
    images = get_images(html_content)
    for image in images:
        print(f"Source: {image['src']}")
        print(f"Alt text: {image['alt']}")
        print(f"Title: {image['title']}")
        print()
