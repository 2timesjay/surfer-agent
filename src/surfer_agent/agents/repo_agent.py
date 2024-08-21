import requests
from bs4 import BeautifulSoup
import openai

class RepoAgent:
    def __init__(self):
        pass

    def summarize_repo(self, repo_url):
        response = requests.get(repo_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract README content
        readme = soup.find('article', class_='markdown-body entry-content container-lg')
        readme_text = readme.get_text(strip=True) if readme else "No README found."
        
        # Extract number of stars
        stars = soup.find('a', class_='social-count js-social-count').get_text(strip=True)
        
        # Summarize README using OpenAI
        summary = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes READMEs."},
                {"role": "user", "content": f"Summarize the following README:\n\n{readme_text}"}
            ],
            max_tokens=50
        ).choices[0].text.strip()
        
        return summary, stars