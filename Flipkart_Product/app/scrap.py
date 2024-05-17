import requests
from bs4 import BeautifulSoup
import pandas as pd

# User-Agent and Accept-Language headers
headers = {
    'User-Agent': 'Your_User_Agent_Here',
    'Accept-Language': 'en-us,en;q=0.5'
}

def scrape_reviews_and_save_to_csv(url, product_name):
    customer_names = []
    review_title = []
    ratings = []
    comments = []

    for i in range(1, 44):
        # Construct the URL for the current page
        current_url = f"{url}&page={i}"

        # Send a GET request to the page
        page = requests.get(current_url, headers=headers)

        # Parse the HTML content
        soup = BeautifulSoup(page.content, 'html.parser')

        # Extract customer names
        names = soup.find_all('p', class_='_2sc7ZR')
        for name in names:
            customer_names.append(name.get_text(strip=True))

        # Extract review titles
        titles = soup.find_all('p', class_='_2-N8zT')
        for title in titles:
            review_title.append(title.get_text(strip=True))

        # Extract ratings
        ratings_all = soup.find_all('div', class_='col _2wzgFH K0kLPL')
        for rating in ratings_all:
            ratings.append(rating.div.text.strip())

        # Extract comments
        comments_all = soup.find_all('div', class_='t-ZTKy')
        for comment in comments_all:
            comment_text = comment.div.div.get_text(strip=True)
            comments.append(comment_text)

    # Ensure all lists have the same length
    min_length = min(len(customer_names), len(review_title), len(ratings), len(comments))
    customer_names = customer_names[:min_length]
    review_title = review_title[:min_length]
    ratings = ratings[:min_length]
    comments = comments[:min_length]

    # Create a DataFrame from the collected data
    data = {
        'Customer Name': customer_names,
        'Review Title': review_title,
        'Rating': ratings,
        'Comment': comments
    }

    df = pd.DataFrame(data)

    # Save the DataFrame to a CSV file
    df.to_csv(f'{product_name}_reviews.csv', index=False)

# URLs for scraping reviews
badminton_url = "https://www.flipkart.com/yonex-mavis-350-nylon-shuttle-yellow/product-reviews/itmfcjdyhnghfyey?pid=STLEFJ7UFQGRUUR3&lid=LSTSTLEFJ7UFQGRUUR3SUDA2S&marketplace=FLIPKART"
motorola_url = "https://www.flipkart.com/motorola-g84-5g-viva-magneta-256-gb/product-reviews/itmed938e33ffdf5?pid=MOBGQFX672GDDQAQ&lid=LSTMOBGQFX672GDDQAQSSIAM2&marketplace=FLIPKART"

# Scrape and save reviews for badminton
scrape_reviews_and_save_to_csv(badminton_url, 'badminton')

# Scrape and save reviews for Motorola
scrape_reviews_and_save_to_csv(motorola_url, 'motorola')
