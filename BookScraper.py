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

class BookMetaData:

    def __init__(self, url):
        self.url = url
        self.soup = None

        # intermediate steps
        self.html_content = None
        self.publish_page_text = None
        self.ratings_histogram_html_content = None 
        
        # basic info
        self.title = None 
        self.author = None
        self.genres = []
        self.page_count = 0
        self.publish_date = None 
        
        # ratings info
        self.rating = None
        self.num_ratings = 0
        self.num_reviews = 0
        self.ratings_histogram = dict()

        self.five_star_ratings = 0
        self.four_star_ratings = 0
        self.three_star_ratings = 0
        self.two_star_ratings = 0
        self.one_star_ratings = 0

        # reviews
        self.review_cards = []
        self.reviews = []
        

    def retrieve_metadata(self):
        """Package basic info in a dictionary and return it"""
        return {
            'title': self.title,
            'author': self.author,
            'genres': self.genres,
            'page_count': self.page_count,
            'publish_date': self.publish_date,
            'rating': self.rating,
            'num_ratings': self.num_ratings,
            'num_reviews': self.num_reviews,
            'five_stars': self.five_star_ratings,
            'four_stars': self.four_star_ratings,
            'three_stars': self.three_star_ratings,
            'two_stars': self.two_star_ratings,
            'one_star': self.one_star_ratings
        }
    
    def retrieve_reviews(self):
        return self.reviews


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

    def get_soup_old(self):
        try:
            source = requests.get(self.url)
        except Exception as e:
            raise RequestFailedException(f"Failed to fetch URL: {self.url}")
        
        
        soup = BeautifulSoup(source.text, "lxml") 
        
        if soup:
            self.soup = soup
            return True
        
        raise SoupNotFoundException(f"Fetched URL successfully but failed to get any text from it")

    def get_html_content_from_url(self):
        soup = self.soup
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
            soup = self.soup
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
    
    
    def get_publish_date(self):

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
        
        pattern = r"(?i)published\s+(.*)"
        text = self.publish_page_text

        date_str = regex_match(pattern, text)
        date = date_str_to_datetime(date_str)

        self.publish_date = date


    def get_ratings_info(self):
        soup = self.soup
        rating_statistics = soup.find('div', class_ = 'RatingStatistics')

        def html_to_int(html):
            text = html.text
            return get_int_from_str(text)
        
        if rating_statistics:

            rating_html  = rating_statistics.find('div', class_ = 'RatingStatistics__column')
            num_ratings_html = rating_statistics.find('span', {'data-testid': 'ratingsCount'})
            num_reviews_html = rating_statistics.find('span', {'data-testid': 'reviewsCount'})

           
            if rating_html:
                rating_text = rating_html.text
                self.rating = float(rating_text)

            else:
                raise SoupNotFoundException(f"Could not find rating value html content")

            if num_ratings_html:
                self.num_ratings = html_to_int(num_ratings_html)

            else:
                raise SoupNotFoundException(f"Could not find num ratings html content")

            if num_reviews_html:
                self.num_reviews = html_to_int(num_reviews_html)

            else:
                raise SoupNotFoundException(f"Could not find num reviews html content")
            
        else:
            raise SoupNotFoundException(f"Could not find RatingStatistics html content")
        
    

    def get_ratings_histogram_html_content(self):
        soup = self.soup
        content = soup.find('div', class_ = 'RatingsHistogram RatingsHistogram__interactive')

        if content:
            self.ratings_histogram_html_content = content  
            return True
        
        raise SoupNotFoundException(f"Could not find ratings histogram html content")
    
    def get_rating_qty_from_text(self, text):
        pattern = r"star[s]?([\d,]+)"
        match = regex_match(pattern, text)

        if match:
            return remove_comma_from_number(match)

        return RegexPatternNotFoundException(f"Unable to find qty from ***stars text") 

    
    def get_qty_ratings_for_star(self, n):
        html_content = self.ratings_histogram_html_content

        class_specs = {'data-testid': f'ratingBar-{n}'}
        rating_html = html_content.find('div', class_specs)

        if rating_html:
            rating_text = rating_html.text
            qty = self.get_rating_qty_from_text(rating_text)
            return qty

        raise SoupNotFoundException(f"Could not find qty ratings html for {n} stars")
        
  
    def get_ratings_histogram(self):
        histogram = {r: self.get_qty_ratings_for_star(r) for r in range(5,0,-1)}
        self.ratings_histogram = histogram


    def get_ratings_for_each_star(self):
        self.five_star_ratings = self.ratings_histogram[5]
        self.four_star_ratings = self.ratings_histogram[4]
        self.three_star_ratings = self.ratings_histogram[3]
        self.two_star_ratings = self.ratings_histogram[2]
        self.one_star_ratings = self.ratings_histogram[1]

    def get_metadata(self):
        try:
            self.get_soup()  # Try to fetch the soup
        except Exception as e:
            print(f"Error in get_soup: {e}")
            return  # Exit if get_soup fails
        
        try:
            self.get_html_content_from_url()
        except Exception as e:
            print(f"Error in get_html_content_from_url: {e}")
        
        try:
            self.get_title()
        except Exception as e:
            print(f"Error getting title from html content: {e}")

        # Now that get_soup() worked, proceed to the other methods individually
        methods = [
            self.get_author,
            self.get_genres,
            self.get_publish_page_text,
            self.get_page_count,
            self.get_publish_date,
            self.get_ratings_histogram_html_content,
            self.get_ratings_info,
            self.get_ratings_histogram,
            self.get_ratings_for_each_star
        ]
        
        # Loop through each method and handle exceptions individually
        for method in methods:
            try:
                method()  # Call the method
            except Exception as e:
                print(f"Error in {method.__name__} for {self.title}: {e}")
                continue  # Move on to the next one even if this one fails


    def get_review_cards(self, n = 10):
        soup = self.soup
        if soup:
            review_cards = soup.find_all('article', class_ = 'ReviewCard')

            if review_cards:
                self.review_cards = review_cards[:n]
                return True

            raise SoupNotFoundException(f"Could not find review cards from soup")
        
        raise SoupNotFoundException(f"get_soup() is empty...")


    def get_user_url_from_review_card(self, review_card):
        try:
            profile_html = review_card.find('div', class_ = 'ReviewerProfile__name')
            profile_url = profile_html.a['href']
            
            if profile_url:
                return profile_url
            
            raise SoupNotFoundException(f"Found profile url from review card but it was empty")

        except Exception as e:
            raise SoupNotFoundException(f"Could not find user url from review card")
        
    def get_user_id_from_review_card(self, review_card):
        user_url = self.get_user_url_from_review_card(review_card)
        
        try:
            user_id = user_url.rsplit('/', 1)[-1]
            return user_id
        except Exception as e:
            return RegexPatternNotFoundException(f"Unable to find user_id from user_url")
        

    def get_user_rating_text_from_review_card(self, review_card):

        shelf_html = review_card.find('div', class_ = 'ShelfStatus')
        
        if shelf_html:
            try: 
                rating_text = shelf_html.find('span', {'aria-label': True})['aria-label']
                return rating_text
            
            except Exception as e:
                 raise SoupNotFoundException(f"Could not find rating_text (aria-label) from review shelf")
            
        raise SoupNotFoundException(f"Could not find shelf from review card")

    def get_rating_from_rating_text(self, text):
        pattern = r'Rating (\d+) out of 5'
        match = regex_match(pattern, text)
        
        return int(match)


    def get_user_rating_from_review_card(self, review_card):
        try:
            rating_text = self.get_user_rating_text_from_review_card(review_card)
            rating = self.get_rating_from_rating_text(rating_text)

            return rating
        except Exception as e:
            print(f"Error getting user_rating: {e}")
    
    def get_review_card_dict(self, i, review_card):
        res = {'title': self.title}

        try:
            res['user_id'] = self.get_user_id_from_review_card(review_card)
            res['rating'] = self.get_user_rating_from_review_card(review_card)
        except SoupNotFoundException as e:
            print(f"SoupNotFound error review card {i}: {e}")
            res['user_id'] = None  
            res['rating'] = None  
        except RegexPatternNotFoundException as e:
            print(f"RegexNotFound review card {i}: {e}")
            res['user_id'] = None  
            res['rating'] = None  
        except Exception as e:
            print(f"Unexpected review card {i}: {e}")
            res['user_id'] = None
            res['rating'] = None

        return res

    # make sure it can run even if 1 review fails...
    def get_reviews(self):

        try: 
            reviews = [self.get_review_card_dict(i, r) for i, r in enumerate(self.review_cards)]
            # reviews = {d["user"]: d["rating"] for d in (self.get_review_card_dict(i, r) for i, r in enumerate(self.review_cards))}
            self.reviews = reviews 

        except SoupNotFoundException as e:
            print(f"SoupNotFound error in get_reviews(): {e}")
        except RegexPatternNotFoundException as e:
            print(f"RegexNotFound error in get_reviews(): {e}")
        except Exception as e:
            print(f"Unexpected error in get_reviews(): {e}")

    def get_review_info(self):

        try:
            self.get_review_cards()
        except Exception as e:
            print(f"Error in get_review_cards(): {e}")
        else:
            self.get_reviews()





"""
# ratings info
self.rating = None
self.num_ratings = 0
self.num_reviews = 0
"""


def test(url):
    book = BookMetaData(url)
    book.get_metadata()

    book_metadata = book.retrieve_metadata()
    print("--- Book metadata ---")
    print(book_metadata)
    print()

    book.get_review_info()
    book_reviews = book.retrieve_reviews()
    print("--- Book reviews ---")
    print(book_reviews)



url = 'https://www.goodreads.com/book/show/4406.East_of_Eden'

test(url)