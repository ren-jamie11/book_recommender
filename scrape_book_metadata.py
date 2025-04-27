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
        self.main_content = None
        
        # basic info
        self.title = None 
        self.author = None
        self.genres = []
        self.pages = 0
        self.publish_date = None 
        
        # ratings info
        self.overall_ratings = dict()
        self.ratings_histogram = dict()

    def get_html_from_url(self, url):
        try: 
            source = requests.get(url)
            source.raise_for_status() 
        except Exception as e:
            raise RequestFailedException(f"Failed to fetch URL: {url}. Reason: {e}")
        
        source_text = source.text
        soup = BeautifulSoup(source_text, "lxml") 
        
        main_content = soup.find('div', class_='BookPage__mainContent')
        
        if main_content:
            return main_content

        raise SoupNotFoundException(f"Could not find metadata html content for: {url}")
        
    

