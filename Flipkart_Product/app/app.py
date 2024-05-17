import streamlit as st
import pandas as pd
from transformers import pipeline
import plotly.express as px
import requests
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="Sentiment Analysis tool",
    page_icon="😊",
    layout="wide"
)


st.title("Real Time Brand Monitoring and Interactive Analysis💕")

detected_emotions_list = []

emotion = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')

def process_csv_input(file):
    encoding_list = ['utf-8', 'latin-1', 'ISO-8859-1']

    for encoding in encoding_list:
        try:
            df = pd.read_csv(file, encoding=encoding)
            st.success(f"CSV file successfully loaded using encoding: {encoding}")
            st.table(df)  
            sentences = df["Comment"].tolist()
            perform_emotion_analysis(sentences)
            break  
        except UnicodeDecodeError:
            st.warning(f"Failed to decode using encoding: {encoding}")
            continue 
    else:
        st.error("Unable to decode the CSV file using any of the tried encodings. Please check the file encoding.")

def perform_emotion_analysis(sentences):
    detected_emotions_list.clear() 
    for sentence in sentences:
        emotion_labels = emotion(sentence)
        detected_emotion = emotion_labels[0]['label']
        detected_emotions_list.append((sentence, detected_emotion))

    st.write("Emotion Analysis Results:")
    result_df = pd.DataFrame(detected_emotions_list, columns=["Comment", "Detected_Emotion"])
    st.table(result_df)

def plot_emotions(filename, product_name):
    st.header(f"Detected Emotions Distribution for {filename}")

    if detected_emotions_list:
        df_emotions = pd.DataFrame(detected_emotions_list, columns=['Comment', 'Detected_Emotion'])

        emotion_counts = df_emotions['Detected_Emotion'].value_counts().reset_index()
        emotion_counts.columns = ['Emotion', 'Count']

        positive_emotions = ['admiration', 'amusement', 'approval', 'caring', 'desire', 'excitement', 'gratitude', 'joy', 'love', 'optimism', 'pride', 'realization', 'relief']
        negative_emotions = ['anger', 'annoyance', 'disappointment', 'disapproval', 'disgust', 'embarrassment', 'fear', 'grief', 'nervousness', 'remorse', 'sadness']
        df_emotions['Emotion Category'] = df_emotions['Detected_Emotion'].apply(lambda x: 'Positive' if x in positive_emotions else ('Negative' if x in negative_emotions else 'Neutral'))

        emotion_category_counts = df_emotions['Emotion Category'].value_counts().reset_index()
        emotion_category_counts.columns = ['Emotion Category', 'Count']

        fig_bar = px.bar(emotion_category_counts, x='Emotion Category', y='Count', labels={'Emotion Category': 'Emotion Category', 'Count': 'Count'}, color='Emotion Category')
        st.plotly_chart(fig_bar)

        fig_pie = px.pie(emotion_category_counts, values='Count', names='Emotion Category', title=f'Detected Emotions Distribution for {filename}', color='Emotion Category')
        st.plotly_chart(fig_pie)
    else:
        st.info("No emotions detected yet.")

def predict_sentiment(text):
    sentiment_classifier = pipeline('sentiment-analysis')
    result = sentiment_classifier(text)
    return result[0]['label']

def scrape_reviews_and_save_to_csv(product_name, url):
    headers = {
        'User-Agent': 'Your_User_Agent_Here',
        'Accept-Language': 'en-us,en;q=0.5'
    }

    customer_names = []
    review_title = []
    ratings = []
    comments = []

    for i in range(1, 44):
        page = requests.get(url.format(i), headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        names = soup.find_all('p', class_='_2sc7ZR')
        for name in names:
            customer_names.append(name.get_text(strip=True))

        titles = soup.find_all('p', class_='_2-N8zT')
        for title in titles:
            review_title.append(title.get_text(strip=True))

        ratings_all = soup.find_all('div', class_='col _2wzgFH K0kLPL')
        for rating in ratings_all:
            ratings.append(rating.div.text.strip())

        comments_all = soup.find_all('div', class_='t-ZTKy')
        for comment in comments_all:
            comment_text = comment.div.div.get_text(strip=True)
            comments.append(comment_text)

    min_length = min(len(customer_names), len(review_title), len(ratings), len(comments))
    customer_names = customer_names[:min_length]
    review_title = review_title[:min_length]
    ratings = ratings[:min_length]
    comments = comments[:min_length]

    data = {
        'Customer Name': customer_names,
        'Review Title': review_title,
        'Rating': ratings,
        'Comment': comments
    }

    df = pd.DataFrame(data)
    filename = f'{product_name}_reviews.csv'
    df.to_csv(filename, index=False)
    return filename

def main():
    st.header("Scrape Reviews and Save to CSV")
    product_name = st.text_input("Enter Product Name:")
    url = st.text_input("Enter URL for Scraping (Flipkart URL)", value='https://www.flipkart.com/motorola-g84-5g-viva-magneta-256-gb/product-reviews/itmed938e33ffdf5?pid=MOBGQFX672GDDQAQ&lid=LSTMOBGQFX672GDDQAQSSIAM2&marketplace=FLIPKART&page={}')

    if st.button("Scrape Reviews"):
        if product_name and url:
            st.info("Scraping reviews and saving to CSV...")
            filename = scrape_reviews_and_save_to_csv(product_name, url)
            st.success(f"Reviews scraped and saved to {filename} successfully!")
            plot_emotions(filename, product_name)  
        else:
            st.warning("Please enter both product name and URL.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        if st.button("Process CSV Input"):
            process_csv_input(uploaded_file)
            plot_emotions(uploaded_file.name, uploaded_file.name)  

    st.header("Text Input for Emotion Analysis")
    text_input = st.text_area("Type or paste your text here:", height=200)
    if st.button("Analyze Text"):
        if text_input.strip() != "":
            sentences = [text_input]
            perform_emotion_analysis(sentences)
            plot_emotions("Input Text", "Input Text")  
        else:
            st.warning("Please input some text to analyze.")

    st.header("Sentiment Analysis")
    user_input = st.text_area("Enter a review text:")

    if st.button("Predict"):
        if user_input:
            sentiment = predict_sentiment(user_input)
            if sentiment == "positive":
                st.markdown("<h2 style='text-align: center;'>Positive Sentiment Detected!</h2>", unsafe_allow_html=True)
                st.markdown('<div style="text-align: center;"><img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExeXg2N3hxaGh5ZmpkdGJkNzhzM2NyNnZnMjVlZjhrcnZrbHlweGJpMCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/chzz1FQgqhytWRWbp3/giphy.webp"></div>', unsafe_allow_html=True)
            elif sentiment == "negative":
                st.markdown("<h2 style='text-align: center;'>Negative Sentiment Detected!</h2>", unsafe_allow_html=True)
                st.markdown('<div style="text-align: center;"><img src="https://media0.giphy.com/media/l1KVaj5UcbHwrBMqI/200.webp?cid=790b7611iax98h1kpxexlwp7nntp5pf4pknw720hkr687ep7&ep=v1_gifs_search&rid=200.webp&ct=g"></div>', unsafe_allow_html=True)
            else:
                st.error("Sentiment could not be determined.")
    else:
        st.warning("Please enter a review text.")

