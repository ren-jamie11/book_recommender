from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re

class RequestFailedException(Exception):
    """Raised when a request to a URL fails."""
    pass

class RegexPatternNotFoundException(Exception):
    """Exception raised when a regex pattern is not found."""
    pass

class SoupNotFoundException(Exception):
    """Exception raised when bs4 html pattern not found"""
    pass

def regex_match(pattern, text):
    match = re.search(pattern, text)
    if match:
        return match.group(1)

    raise RegexPatternNotFoundException(f"Pattern '{pattern}' not found in the text: {text[:40]}...") 


class BookMetaData:
    def __init__(self, url):
        self.url = url
        self.html_content = None
        
        # basic info
        self.title = None 
        self.author = None
        self.genres = []
        self.pages = 0
        self.publish_date = None 
        
        # ratings info
        self.overall_ratings = dict()
        self.ratings_histogram = dict()

    def get_html_from_url(self):
        try:
            source = requests.get(self.url)
            source.raise_for_status()
        except Exception as e:
            raise RequestFailedException(f"Failed to fetch URL: {self.url}")
        
        soup = BeautifulSoup(source.text, "lxml")
        html_content = soup.find('div', class_='BookPage__mainContent')
        
        if html_content:
            return html_content

        raise SoupNotFoundException(f"Could not find metadata html content for: {self.url}")
        
    def get_title(self):
        try:
            content = self.html_content
            title = content.find('h1', class_ ="Text Text__title1").text
        except Exception as e:
            raise SoupNotFoundException(f"Could not find title from html content ({e})")
        
        return title
    
    def get_author(self):
        try:
            content = self.html_content
            author_div = content.find('div', class_="ContributorLinksList")
            author = author_div.find('a', class_ = 'ContributorLink').text

        except Exception as e:
            raise SoupNotFoundException(f"Could not find author from html content ({e})")
        
        return author
    
    

        
