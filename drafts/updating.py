import numpy as np  
import pandas as pd
import os

from static import *

def update_genre_parquets(genres, input_dir='scraper_results', output_dir='scraper_results'):
    for genre in genres:
        input_file = os.path.join(input_dir, f'{genre}_books.parquet')
        output_file = os.path.join(output_dir, f'{genre}_books_updated.parquet')
        
        # Load the existing parquet
        df = pd.read_parquet(input_file)
        
        # Insert the new column at the very beginning
        df.insert(0, 'original_genre', genre)
        
        # Save the updated DataFrame
        df.to_parquet(output_file, index=False)
        
        print(f'Processed {genre}: saved to {output_file}')


update_genre_parquets(genres)