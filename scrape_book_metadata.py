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
        self.soup = None

        # intermediate steps
        self.html_content = None
        self.publish_page_text = None
        
        # basic info
        self.title = None 
        self.author = None
        self.genres = []
        self.page_count = 0
        self.publish_date = None 
        
        # ratings info
        self.overall_ratings = dict()
        self.ratings_histogram = dict()

    def get_soup(self):
        try:
            source = requests.get(self.url)
            source.raise_for_status()
        except Exception as e:
            raise RequestFailedException(f"Failed to fetch URL: {self.url}")
        
        
        soup = BeautifulSoup(source.text, "lxml") 
        
        if soup:
            return soup
        
        raise SoupNotFoundException(f"Fetched URL successfully but failed to get any text from it")

    def get_html_content_from_url(self):
        soup = self.get_soup()
        html_content = soup.find('div', class_='BookPage__mainContent')
        
        if html_content:
            self.html_content = html_content
            return True

        raise SoupNotFoundException(f"Could not find metadata html content for: {self.url}")
        
    def get_title(self):
        try:
            content = self.html_content
            title = content.find('h1', class_ ="Text Text__title1").text

            if title:
                self.title = title
                return True
            
            raise SoupNotFoundException(f"Could not find author from html content")

        except Exception as e:
            raise SoupNotFoundException(f"Could not find title from html content ({e})")
        

    def get_author(self):
        try:
            content = self.html_content
            author_div = content.find('div', class_="ContributorLinksList")
            author = author_div.find('a', class_ = 'ContributorLink').text

            if author:
                self.author = author
                return True
            
            raise SoupNotFoundException(f"Could not find author from html content")

        except Exception as e:
            raise SoupNotFoundException(f"Could not find author from html content ({e})")
    
    def get_genres(self):
        try:
            content = self.html_content
            genre_spans = content.find_all('span', class_ = 'BookPageMetadataSection__genreButton')
            
            if genre_spans:
                genres = [g.text for g in genre_spans]
                self.genres = genres
                return True
            
            raise SoupNotFoundException(f"Could not find genres from html content")
            
        except Exception as e:
            raise SoupNotFoundException(f"Could not find genres from html content ({e})")
        
    
    def get_publish_page_text(self):
        try:
            soup = self.get_soup()
            publish_page_text = soup.find('span', class_ = 'Text Text__body3').text

            if publish_page_text:
                self.publish_page_text = publish_page_text
                return True
            
            raise SoupNotFoundException(f"Could not find publish/page text from html content")

        except Exception as e:
            raise SoupNotFoundException(f"Could not find publish/page text from html content: ({e})")

        
    def get_page_count(self):
        pattern = r"(\d+)\s+pages"
        text = self.publish_page_text

        self.page_count = int(regex_match(pattern, text))
    
    
    def get_publish_date_from_str(self):

        # Helper function specific to this date/str format
        def date_str_to_datetime(date_str):
            match = re.search(r'(\w+ \d{1,2}), (\d+)', date_str)
            
            if match:
                month_day = match.group(1)  # 'January 1'
                year = match.group(2).zfill(4)  # '0401'
                padded_date_str = f"{month_day}, {year}"
            
                date_obj = datetime.strptime(padded_date_str, "%B %d, %Y")
                return date_obj

            raise RegexPatternNotFoundException(f"Unable to convert date_str {date_str} into datetime object") 
        
        pattern = r"published\s+(.*)"
        text = self.publish_page_text

        date_str = regex_match(pattern, text)
        date = date_str_to_datetime(date_str)

        self.publish_date = date


    

