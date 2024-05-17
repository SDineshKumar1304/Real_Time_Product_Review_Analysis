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

st.title("Real Time Brand Monitering and Interactive Analysis💕")

detected_emotions_list = []

emotion = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')

def process_csv_input(file):
    encoding_list = ['utf-8', 'latin-1', 'ISO-8859-1']

    for encoding in encoding_list:
        try:
            df = pd.read_csv(file, encoding=encoding)
            st.success(f"CSV file successfully loaded using encoding: {encoding}")
            st.table(df)  
            sentences = df["Sentence"].tolist()
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

    st.write("Analysis Results:")
    result_df = pd.DataFrame(detected_emotions_list, columns=["Sentence", "Detected_Emotion"])
    st.table(result_df)

def plot_emotions():
    st.header("Detected Emotions Distribution")

    if detected_emotions_list:
        df_emotions = pd.DataFrame(detected_emotions_list, columns=['Sentence', 'Detected_Emotion'])

        emotion_counts = df_emotions['Detected_Emotion'].value_counts().reset_index()
        emotion_counts.columns = ['Emotion', 'Count']

        positive_emotions = ['admiration', 'amusement', 'approval', 'caring', 'desire', 'excitement', 'gratitude', 'joy', 'love', 'optimism', 'pride', 'realization', 'relief']
        negative_emotions = ['anger', 'annoyance', 'disappointment', 'disapproval', 'disgust', 'embarrassment', 'fear', 'grief', 'nervousness', 'remorse', 'sadness']
        df_emotions['Emotion Category'] = df_emotions['Detected_Emotion'].apply(lambda x: 'Positive' if x in positive_emotions else ('Negative' if x in negative_emotions else 'Neutral'))

        emotion_category_counts = df_emotions['Emotion Category'].value_counts().reset_index()
        emotion_category_counts.columns = ['Emotion Category', 'Count']

        fig_bar = px.bar(emotion_category_counts, x='Emotion Category', y='Count', labels={'Emotion Category': 'Emotion Category', 'Count': 'Count'}, color='Emotion Category')
        st.plotly_chart(fig_bar)

        fig_pie = px.pie(emotion_category_counts, values='Count', names='Emotion Category', title='Detected Emotions Distribution', color='Emotion Category')
        st.plotly_chart(fig_pie)
    else:
        st.info("No emotions detected yet.")

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
    review_title =review_title = review_title[:min_length]
    ratings = ratings[:min_length]
    comments = comments[:min_length]

    data = {
        'Customer Name': customer_names,
        'Review Title': review_title,
        'Rating': ratings,
        'Comment': comments
    }

    df = pd.DataFrame(data)
    df.to_csv(f'{product_name}_reviews.csv', index=False)

def main():
    st.header("Scrape Reviews and Save to CSV")
   
    st.image("https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/5/e/3/g84-5g-paym0018in-motorola-original-imagsy5zmhvkcfsx.jpeg?q=70")
    st.subheader("Motorola Reviews")
    if st.button("Scrape Motorola Reviews"):
        st.info("Scraping Motorola reviews and saving to CSV...")
        scrape_reviews_and_save_to_csv('Motorola', 'https://www.flipkart.com/motorola-g84-5g-viva-magneta-256-gb/product-reviews/itmed938e33ffdf5?pid=MOBGQFX672GDDQAQ&lid=LSTMOBGQFX672GDDQAQSSIAM2&marketplace=FLIPKART&page={}')
        st.success("Motorola reviews scraped and saved to CSV successfully!")
    
    st.image("https://rukminim2.flixcart.com/image/312/312/kdkkdjk0/shuttle/u/r/3/mavis-350-green-cap-6-75-nylon-yonex-slow-original-imafug3vnxye6skh.jpeg?q=70")
    st.subheader("Badminton Reviews")
    if st.button("Scrape Badminton Reviews"):
        st.info("Scraping badminton reviews and saving to CSV...")
        scrape_reviews_and_save_to_csv('Badminton', 'https://www.flipkart.com/yonex-mavis-350-nylon-shuttle-yellow/product-reviews/itmfcjdyhnghfyey?pid=STLEFJ7UFQGRUUR3&lid=LSTSTLEFJ7UFQGRUUR3SUDA2S&marketplace=FLIPKART={}')
        st.success("Badminton reviews scraped and saved to CSV successfully!")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        if st.button("Process CSV Input"):
            process_csv_input(uploaded_file)
            plot_emotions()

    st.header("Text Input for Emotion Analysis")
    text_input = st.text_area("Type or paste your text here:", height=200)
    if st.button("Analyze Text"):
        if text_input.strip() != "":
            sentences = [text_input]
            perform_emotion_analysis(sentences)
            plot_emotions()
        else:
            st.warning("Please input some text to analyze.")

if __name__ == "__main__":
    main()

