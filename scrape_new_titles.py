from BookScraper import *

import pandas as pd
import numpy as np
import time

from joblib import Parallel, delayed


def get_urls_from_txt_file(file):
    with open(file, 'r') as file:
        urls = file.readlines()

    urls = [url.strip() for url in urls]
    return urls

def book_data_generator(urls, n):
    for i, url in enumerate(urls[:n]):
        print("Parsing url", url)
    
        start_time = time.time()  # Start time for each iteration
    
        book = BookMetaData(url)
    
        # metadata
        book.get_metadata()
        book_metadata = book.retrieve_metadata()
    
        # reviews
        book.get_review_info()
        book_review_dict = book.retrieve_reviews()
    
        end_time = time.time()  # End time for each iteration
        loop_time = end_time - start_time  # Time taken for this iteration
        print(f"Time taken for iteration {i}: {loop_time:.2f} seconds")
        print()
    
        yield book_metadata, book_review_dict


def scrape_books_from_genre(j, n = None):
    print(f"Initializing group {j}")
    file = f'new_titles_urls/new_titles_group_{j}.txt'
    urls = get_urls_from_txt_file(file)

    if not n:
        n = len(urls)
        print(f"FULL SEND: size {n}")

    book_data_gen = book_data_generator(urls, n)
    
    book_metadatas = [dict()] * n
    book_reviews = []

    for i, data in enumerate(book_data_gen):
        book_metadata, book_review_dict = data
        
        book_metadatas[i] = book_metadata
        book_reviews.extend(book_review_dict)

    book_metadata_df = pd.DataFrame(book_metadatas)
    book_review_df = pd.DataFrame(book_reviews)

    book_metadata_df.to_parquet(f'new_titles_scraper_results/group_{j}_new_books_data.parquet', index=False)
    book_review_df.to_parquet(f'new_titles_scraper_results/group_{j}_new_books_reviews.parquet', index=False)
    

group_numbers = [i for i in range(1, 59)]
Parallel(n_jobs=min(10, len(group_numbers)))(delayed(scrape_books_from_genre)(j) for j in group_numbers)

