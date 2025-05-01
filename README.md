# Book Recommender with Goodreads Scraper

### Get relevant and interesting recommendations instantly from your Goodreads account!

This recommender uses a vast amount of data scraped from Goodreads to provide quality personalized recommendations for you. It uses data from:
1. 16,578 books
2. 175,576 users
3. 476,199 ratings

### Example: My recs

<img src="https://github.com/ren-jamie11/book_recommender/blob/main/assets/my_recs_updated.png" alt="Alt text" width="1200">

### How it works

All you need is to enter your Goodreads user_id, and it will:

1. Automatically pull your book ratings from the Goodreads website  
2. Provide 3 types of recommendations from:
   - Informed users with similar genre reading patterns as you  
   - Informed users with similar ratings opinions as you  
   - Top readers of your favorite genre
  
### Why it works

The recommender leverages the expertise and experience of readers who are both *similar to you* and *informed*. 
When deciding on which book to read, you would probably look at the overall ratings and ratings count. However, not every rating from every reader is relevant to you, as people have different tastes.
Specifically, you would value the suggestions avid readers who exhibit the same reading choices/taste as you, as their opinions are likely to be much more informed and relevant to you.</br>

## The math 

### User item matrix

One of the most intuitive (and well-established) ways to encode user ratings of books is via a *user-item matrix*, where $M_{ij}$ is the rating of user $i$ for item $j$. From the tuple (title, user_id, rating) and the genre tags of each book, it is easy to construct both the *user-item matrix* as well as a *genre-user matrix*, where $G_{ij}$ is the number of books that user $j$ has read from genre $i$.   

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
\mu_u = \frac{\sum_{b \in I_u} z_{ub}}{|I_u|} 
$$

where $I_u$ is the set of all books that user $u$ has rated.

This normalization procedure will make comparison between ratings for different books and users significantly more meaningful.

### User similarity

Having constructed the normalized user-item matrix, we can compare similarity between 2 users using *cosine similarity*, which is 

$$
q_{uv} = \frac{
\sum_{k \in I_u \cap I_v} s_{ub} \cdot s_{vb}
}{
\sqrt{\sum_{k \in I_u \cap I_v} s_{ub}^2} \cdot \sqrt{\sum_{k \in I_u \cap I_v} s_{vb}^2}
}
$$

Intuitively, if we treated the ratings (or genre reading pct) for users $u$ and $v$ as 2 vectors, the above finds the cosine of the "angle" between the 2, which is a value from -1 to 1. Note that we are only using books that both these 2 users have read. 

**Example**

For instance, this is a snapshot of the genre reading pcts of me vs. another user with a genre cosine similarity of 0.94. Pretty alike, right!?

<img src="https://github.com/ren-jamie11/book_recommender/blob/main/assets/cos_similarity.png" alt="Alt text" width="250">

I did not include all 40 genres in this image, and the probabilities do not add up to 1 because each book has multiple genre tags.

### Using similar users to recommend books

Having measured the similarity of each user relative to the target user, the next steps are:

1. Choose the top \( k \) most similar users (e.g.,  $k = 10$ or $k = 50$).
2. Compute each user's *amount-of-say*, defined as:

$$
w_u = \frac{q_{ut}}{\sum_{i=1}^{k} q_{it}}
$$

where $q_{ut}$ is the simiarity of user $u$ to target user $t$. Intuitvely, it is the normalized similarity score of the k-nearest users.

3. Compute the neighborhood-user score $S_j$ for book $j$, defined as
   
$$
S_{j} = \sum_{u \in B_j} w_u \cdot s_{uj}
$$

where $B_j$ is the set of all k-nearest users who have read book $j$.

Basically, add up the normalized ratings of each of the k-nearest users weighted by their similarity to you. Intuitively, this function favor books:
   - Read by many users similar to you
   - Rated highly by users similar to you

**Example**

These are the books suggested to me based on the top 50 users with similar genre preferences as me.

</br>

<img src="https://github.com/ren-jamie11/book_recommender/blob/main/assets/genre_recs.png" alt="Alt text" width="600">
</br>

I am quite satisfied with these recommendations, as the recommender noticed that I like philosophy/self-help books and suggested books that similar users loved. Notice that the k-nearest users' ratings of these books are significantly higher than the overall ratings (expressing the principle that ratings of similar users are more relevant). 

The counts (of the 50-nearest users who have read each book) are small because the book universe is enormous (relative to amount of data my laptop can efficiently work with), so it is relatively hard to find many users with overlapping books. 

The above recommendation is biased towards highly popular books that many have read. To make the recommendations more "interesting" or "serendipitous", one can adjust the weightings by the inverse frequency of each book to promote books that are both relevant but not known to many people.

### Genre relative preference & expertise

#### Preference

To identify a target user's favorite genres, we again use the z-score idea to find "how much does this user's reading pct of this genre deviate from the mean for that genre?" 

$$ z_{ug} = \frac{p_{ug} - \mu_{g}}{\sigma_g}
$$ 

where $p_{ug}$ is the % of user $u$'s ratings that are from genre $g$, $\mu_{g}$ and $\sigma_g$ being the mean, std of % of ratings that are from genre $g$ for all users.

#### Expertise

Intuitively, a user is considered "specialized" in a genre if:
1. She has read a lot of books from that genre.
2. Most of the books she's read are from this genre

We can easily express this in the expression 

$$
\phi_{ug} = n_{ug} \cdot p_{ug}^\alpha 
$$

- $n_{ug}$: Number of books user $u$ has read from genre $g$
- $p_{ug}$: Pct of user $u$'s ratings that are from genre $g$
- $\alpha$: Hyperparameter

For instance, who is more specialized in fantasy books - someone who has read 48 fantasy books, constituting 30% of his books, or someone who has read 18 fantasy books, constituting 88% of her books? The $\alpha$ hyperparameter tunes this weighting. 

After retrieving the preference/expertise scores of each user for each genre, we can then use the top users for a genre to recommend books for that genre (in similar fashion to how we used k-nearest users to recommend books for a target user).

## The data

Collecting (and cleaning) the data was no easy task. Fortunately, the Goodreads site is very organized, consistent, and lenient when allowing bots to scrape the site. So, thank you!!!

### Data collection

To ensure depth and breadth of genres, we do the following for each of the 40 main genres defined by Goodreads: https://www.goodreads.com/genres
1. Get top 50 books from this genre
2. Get top 30 reviews for each book (title, user_id, rating)
3. Get top 5 most liked reviews for each user_id (5x our book coverage)
4. Get top 30 reviews for each of these new books

Of course, there are overlaps between books that users have rated, and the scraper was unable to load user profiles around 1/4 of the time. However, this was still an effective method to get a wide and high-quality selection of books. After data cleaning (discarding missing user/book values and filtering for English books/reviews only), we ended up with:
1. 16,575 books
2. 175,576 users
3. 476,199 ratings

### Scraping

This data was scraped using *Beautiful Soup*: https://beautiful-soup-4.readthedocs.io/en/latest/
I built the BookScraper and UserScraper from scratch, which I used to retrieve the data from goodreads. Since each webpage takes around 2 seconds to retrieve with requests, I also used joblib to parallelize the task. Otherwise, scraping 4000 x 30 x 5 x 30 = 18M sites would take...around 10,000 hours! (Of course, there is overlap between genres/users, but you get the idea...)

### Efficiency & memory management

Because we would like the recommender to output results in a resonable time frame (<10 seconds), it would be infeasible to use the full user-item matrix (~384GB). Therefore, we only included the 9,396 users that provided the top 30 reviews from the original 4,000 books. Thus, the user-item matrix used was 9,396 x 16,575 (1.3GB). This made computations feasible without loss of quality, because the remaining users contain far less info than users who provided the top reviews for Goodreads' most popular books.






