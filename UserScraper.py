from bs4 import BeautifulSoup
from datetime import datetime
import requests
import re

from static import *
from CustomExceptions import *

def regex_match(pattern, text):
    match = re.search(pattern, text)
    if match:
        return match.group(1)

    raise RegexPatternNotFoundException(f"Pattern '{pattern}' not found in the text: {text[:40]}...") 

def remove_comma_from_number(num_str):
    num = num_str.replace(",", "")
    return int(num)


def get_int_from_str(text):
        pattern = r'([\d,]+)'
        match = regex_match(pattern, text)

        num = remove_comma_from_number(match)
        return num

def get_number_from_text(text, dtype = int):
    pattern = r'([\d.]+)'
    match = regex_match(pattern, text)

    if dtype == int:
        return int(match)
    elif dtype == float:
        return float(match)
    else:
        return match


class UserMetaData:
     
    def __init__(self, url):
        self.url = url
        self.soup = None

        # intermediate steps
        self.user_stats_html = None

        # basic info
        self.name = None
        self.num_ratings = 0
        self.avg_rating = 0.0
        self.num_reviews = 0

        self.is_best_reviewer = False
        self.reviewer_rank = 0
        
        self.is_most_followed = False
        self.follow_rank = 0    

        # reviews
        self.review_cards = []
        self.reviews = []


    def get_soup(self, headers_list = headers_list):
        for header in headers_list:
            response = requests.get(self.url, headers=header)
            source = response.text

            if len(source) > 10000:
                soup = BeautifulSoup(source, "lxml")

                if soup:
                    self.soup = soup
                    return True
                
                else:
                    continue

        raise RequestFailedException(f"Failed to fetch URL: {self.url}")

    
    def get_name_from_html(self):
        soup = self.soup
        name_html = soup.find('h1', class_ = 'userProfileName')
        
        if name_html:
            name = name_html.text
            name = re.sub(r'\n', '', name).strip()
            self.name = name
            return True
        
        raise SoupNotFoundException(f"Couldn't find (h1, class_ = 'userProfileName') from soup")
    

    def get_user_stats_html(self):
        soup = self.soup
        user_stats_html = soup.find('div', class_ = 'profilePageUserStatsInfo')

        if user_stats_html:
            self.user_stats_html = user_stats_html
            return True
        
        raise SoupNotFoundException(f"Couldn't find (div, class_ = 'profilePageUserStatsInfo') from soup")
    

    def get_stats_from_user_stats_html(self):
        links = self.user_stats_html.find_all('a')
        
        if links and len(links) >= 3:
            # ratings
            num_ratings_text = links[0].text
            avg_ratings_text = links[1].text
            num_reviews_text = links[2].text

            self.num_ratings = get_number_from_text(num_ratings_text)
            self.avg_rating = get_number_from_text(avg_ratings_text, dtype = float)
            self.num_reviews = get_number_from_text(num_reviews_text)

        raise SoupNotFoundException(f"Couldn't find any 'a' links in user_stats_html")
    

    def verify_is_best_reviewer(self):
        best_reviewer_html = self.user_stats_html.find('a', id='tl_best_reviewers')
        
