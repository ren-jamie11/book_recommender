from BookScraper import *
from UserScraper import *

import pandas as pd
import numpy as np
import time

from joblib import Parallel, delayed


def get_urls_from_txt_file(file):
    with open(file, 'r') as file:
        urls = file.readlines()

    urls = [url.strip() for url in urls]
    return urls

def user_data_generator(urls, n):
    for i, url in enumerate(urls[:n]):
        print("Parsing user url", url)
        start_time = time.time()  # Start time for each iteration

        user = UserMetaData(url)

        # metadata
        user.get_metadata()
        user_metadata = user.retrieve_metadata()

        # reviews
        user.get_review_info()
        user_reviews = user.retrieve_reviews()

        end_time = time.time()  # End time for each iteration
        loop_time = end_time - start_time  # Time taken for this iteration
        print(f"Time taken for iteration {i}: {loop_time:.2f} seconds")
        print()

        yield user_metadata, user_reviews

def scrape_user_info_from_urls(j, n = None):
    file = f'user_id_urls/usergroup_{j}.txt'
    urls = get_urls_from_txt_file(file)
    
    if not n:
        print("HALLELUYAH")
        n = len(urls)

    user_data_gen = user_data_generator(urls, n)

    user_metadatas = [dict()] * n
    user_reviews = []

    for i, data in enumerate(user_data_gen):
        user_metadata, user_review_dict = data

        user_metadatas[i] = user_metadata
        user_reviews.extend(user_review_dict)        

    user_metadata_df = pd.DataFrame(user_metadatas)
    user__review_df = pd.DataFrame(user_reviews)

    user_metadata_df.to_parquet(f'user_scraper_results/group_{j}_user_data.parquet', index=False)
    user__review_df.to_parquet(f'user_scraper_results/group_{j}_user_reviews.parquet', index=False)



group_numbers = [i for i in range(1, 31)]
Parallel(n_jobs=min(10, len(group_numbers)))(delayed(scrape_user_info_from_urls)(j) for j in group_numbers)