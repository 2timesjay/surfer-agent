import requests
import sys
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
from readability import Document
import html2text
from urllib.parse import urlparse, urljoin
from collections import deque

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


def get_simplified_content(html_content):
    """Extract the main content from the HTML and convert it to plain text."""
    doc = Document(html_content)
    main_content = doc.summary()
    
    # Convert HTML to plain text
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    plain_text = h.handle(main_content)
    
    return plain_text


def save_page_to_json(url, html_content, headers=None, save_dir='.'):
    """Save browsed pages to JSON files with metadata."""
    data = {
        "url": url,
        "date_accessed": datetime.now().isoformat(),
        "browser_agent": headers.get("User-Agent") if headers else None,
        "content": html_content,
    }

    filename = f"page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Page saved to {filepath}")


class Crawler:
    def __init__(
        self, 
        start_url: str,
        max_pages: int = 100, 
        save_dir_root: str = 'saved_pages/', 
        headers: dict = None,
        dry_run: bool = False,
    ):
        self.start_url = start_url
        self.max_pages = max_pages
        self.visited = set()
        self.queue = deque()
        self.save_dir_root = save_dir_root
        self.dry_run = dry_run
        self.headers = headers  # Unused

    def url_to_save_dir(self, url):
        """Convert a URL to a directory path for saving."""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        domain = domain.replace('.', '_')
        path = parsed_url.path.strip('/')
        path = path.replace('/', '_')
        if path:
            save_dir = os.path.join(self.save_dir_root, domain, path)
        else:
            save_dir = os.path.join(self.save_dir_root, domain)
        
        return save_dir

    def filter_links(self, links):
        """Filter links to ensure they are within the domain and not already visited."""
        filtered_links = []
        start_domain = urlparse(self.start_url).netloc
        start_path = urlparse(self.start_url).path.rstrip('/')
        
        for link in links:
            parsed_link = urlparse(link)
            link_domain = parsed_link.netloc
            link_path = parsed_link.path.rstrip('/')
            
            if (link_domain == start_domain and 
                link_path.startswith(start_path) and 
                link not in self.visited):
                filtered_links.append(link)
        
        return filtered_links

    def crawl(self):
        start_domain = urlparse(self.start_url).netloc
        start_path = urlparse(self.start_url).path.rstrip('/')
        print(f"Starting crawl from {self.start_url}")
        self.queue.append(self.start_url)
        pages_crawled = 0

        while self.queue and pages_crawled < self.max_pages:
            url = self.queue.popleft()
            if url in self.visited:
                continue

            try:
                html_content = fetch_page(url)
                if self.dry_run:
                    pass
                else:
                    self.save_page(url, html_content)
                self.visited.add(url)
                pages_crawled += 1

                links = get_links_with_context(html_content)
                filtered_links = self.filter_links([link['url'] for link in links])
                self.queue.extend(filtered_links)

                print(f"Crawled: {url}")
            except Exception as e:
                print(f"Error crawling {url}: {str(e)}")

        print(f"Crawling completed. Visited {pages_crawled} pages.")

    # def get_domain_links(self, base_url, html_content, domain):
    #     links_with_context = get_links_with_context(html_content)
    #     domain_links = set()
    #     for link in links_with_context:
    #         full_url = urljoin(base_url, link['url'])
    #         if urlparse(full_url).netloc == domain and full_url not in self.visited:
    #             domain_links.add(full_url)
    #     return domain_links

    def save_page(self, url, html_content):
        save_dir = self.url_to_save_dir(url)
        save_page_to_json(url, html_content, headers={}, save_dir=save_dir)  # Assuming headers are not available in this context


# Example usage
if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # html_content = fetch_page(url, headers)

    # print("Prettified HTML:")
   
    # print("\nSimplified Content:")
    # simplified_content = get_simplified_content(html_content)
    # print(simplified_content)

    # print("\nLinks with context:")
    # links = get_links_with_context(html_content)
    # for link in links:
    #     print(f"URL: {link['url']}")
    #     print(f"Text: {link['text']}")
    #     print(f"Context: {link['context']}")
    #     print()

    # save_page_to_json(url, html_content, headers)

    # print("\nImages:")
    # images = get_images(html_content)
    # for image in images:
    #     print(f"Source: {image['src']}")
    #     print(f"Alt text: {image['alt']}")
    #     print(f"Title: {image['title']}")
    #     print()

    crawler = Crawler(
        start_url=url,
        max_pages=10, 
        save_dir_root='saved_pages/', 
        dry_run=False
    )
    crawler.crawl()