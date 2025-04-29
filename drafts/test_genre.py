
from BookScraper import *
import pandas as pd
import numpy as np

import time


file = 'book_urls/Psychology.txt'

def get_urls_from_txt_file(file):
    with open(file, 'r') as file:
        urls = file.readlines()

    urls = [url.strip() for url in urls]
    return urls

urls = get_urls_from_txt_file(file)

book_metadatas = [dict()] * len(urls)
book_reviews = [dict()] * len(urls)

for i, url in enumerate(urls[:5]):
    print("Parsing url", url)

    start_time = time.time()  # Start time for each iteration

    book = BookMetaData(url)

    # metadata
    book.get_metadata()
    book_metadata = book.retrieve_metadata()
    book_metadatas[i] = book_metadata

    # reviews
    book.get_review_info()
    book_reviews = book.retrieve_reviews()
    book_reviews[i] = book_reviews

    end_time = time.time()  # End time for each iteration
    loop_time = end_time - start_time  # Time taken for this iteration
    print(f"Time taken for iteration {i}: {loop_time:.2f} seconds")
    print()

metadata_df = pd.DataFrame(book_metadatas)
reviews_df = pd.DataFrame(book_reviews)

print(metadata_df.head(20), len(metadata_df))
print(reviews_df.head(20), len(reviews_df))