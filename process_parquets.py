
import numpy as np  
import pandas as pd
import glob
import os

from static import *

import pandas as pd
import glob
import os

def combine_files(suffix, output_filename, file_type='parquet', input_dir=''):
    parquet_files = glob.glob(os.path.join(input_dir, f'*_{suffix}.{file_type}'))
    
    dfs = []
    for file in parquet_files:
        df = pd.read_parquet(file, engine='pyarrow')

        # Detect columns of dtype datetime64 and cast them to string
        for col in df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
            df[col] = df[col].astype(str)

        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.to_parquet(output_filename, index=False)
    
    print(f'Combined {len(parquet_files)} files into {output_filename}')


original_users_filename = 'final_aggregated_results/new_books.parquet'
user_reviews_filename = 'final_aggregated_results/user_new_book_reviews.parquet'

combine_files(suffix = 'data', output_filename = original_users_filename, input_dir = 'new_titles_scraper_results')
combine_files(suffix = 'reviews', output_filename = user_reviews_filename, input_dir = 'new_titles_scraper_results')