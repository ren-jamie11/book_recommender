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

### User item matrix

One of the most intuitive (and well-established) ways to encode user ratings of books is via a *user-item matrix*, where $M_{ij}$ is the rating of user $i$ for item $j$. From the tuple (title, user_id, rating) and the genre tags of each book, it is easy to construct both the *user-item matrix* as well as a *genre-user matrix*, where $G_{ij}$ is the number of books that that user $j$ has from genre $i$.   

### Normalizing ratings

The problem with directly using ratings its true information content depends on both
1. The average ratings that the user gives
2. The average rating that the book received </br>

For instance, a 5-star review from a user who always gives 5 stars means something very different from a 5-star review by a more critical user with an average rating of 3.2 stars. The same applies to a 5-star review for a book that everyone loves versus a book with an average of 2.5 stars across 8,546 ratings.

**Z-score normalization**

We first normalize the ratings by each book using the formula 

$$ 
z_{ub} = \frac{r_{ub} - \mu_{b}}{\sigma_b} 
$$

where $r_{ub}$ is user $u$'s rating of book $b$, with $\mu_b$ and $\sigma_{b}$ being the mean and standard deviation of each book's ratings, respectively. $\mu_b$ and $\sigma_{b}$ can be computed from the number of ratings given from 1-star to 5-stars. 

**Mean-centered ratings**

We then compute the mean-centered z-score rating $\( s_{uj} \)$ of user $u$ for book $b$ using the expression:

$$
s_{ub} = z_{ub} - \mu_u  
$$

where the average rating for user $u$, denoted $\( \mu_u \)$, is defined by:

$$
\mu_u = \frac{\sum_{b \in B_u} z_{ub}}{|I_u|} 
$$

where $B_u$ is the set of all books that user $u$ has rated.

This normalization procedure will make comparison between ratings for different books and users significantly more meaningful.

### User similarity

Having constructed the normalized user-item matrix, we can compare similarity between 2 users using *cosine similarity*, which is 

$$
\frac{
\sum_{k \in B_u \cap B_v} s_{ub} \cdot s_{vb}
}{
\sqrt{\sum_{k \in B_u \cap B_v} s_{ub}^2} \cdot \sqrt{\sum_{k \in B_u \cap B_v} s_{vb}^2}
}
$$

Intuitively, if we treated the ratings (or genre reading pct) for users $u$ and $v$ as 2 vectors, the above finds the cosine of the "angle" between the 2, which is a value from -1 to 1. Note that we are only using books that both these 2 users have read. 

**Example**

For instance, this is a snapshot of the genre reading pcts of me vs. another user with a genre cosine similarity of 0.94. 


### Relative expertise



## The data



