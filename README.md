# Book Recommender with Goodreads Scraper

### Get relevant and interesting recommendations instantly from your Goodreads account!

This recommender uses a vast amount of data scraped from Goodreads to provide quality personalized recommendations for you. It uses data from:
1. 16,578 books
2. 175,576 users
3. 476,199 ratings

#### How it works

All you need is to enter your Goodreads user_id, and it will:

1. Automatically pull your book ratings from the Goodreads website  
2. Provide 3 types of recommendations from:
   - Informed users with similar genre reading patterns as you  
   - Informed users with similar ratings opinions as you  
   - Top readers of your favorite genre
  
#### Why it works

The recommender leverages the expertise and experience of readers who are both *similar to you* and *informed*. 
When deciding on which book to read, you would probably look at the overall ratings and ratings count. However, not every rating from every reader is relevant to you, as people have different tastes.
Specifically, you would value the suggestions avid readers who exhibit the same reading choices/taste as you, as their opinions are likely to be much more informed and relevant to you.</br>

## The math 

#### User item matrix

One of the most intuitive (and well-established) ways to encode user ratings of books is via a *user-item matrix*, where $M_{ij}$ is the rating of user $i$ for item $j$. From the tuple (title, user_id, rating) and the genre tags of each book, it is easy to construct both the *user-item matrix* as well as a *genre-user matrix*, where $G_{ij}$ is the number of books that that user $j$ has from genre $i$.   



#### User similarity

#### Relative expertise



## The data



