import os
import re
from googleapiclient.discovery import build
from textblob import TextBlob
import matplotlib.pyplot as plt  # Import matplotlib for plotting
import streamlit as st
import pandas as pd  # Required for handling the bar chart

# Function to get the YouTube API key from user input
def get_youtube_api_key():
    """
    Prompts the user to enter their YouTube API key.
    
    Returns:
        str: The YouTube API key entered by the user.
    """
    api_key = st.text_input("Please enter your YouTube API key:").strip()
    if not api_key:
        st.warning("API key cannot be empty. Please enter a valid YouTube API key.")
        return None
    return api_key

# Function to extract video ID from YouTube URL
def get_video_id(url):
    """
    Extracts video ID from a YouTube URL.
    
    Args:
        url (str): The URL of the YouTube video.
        
    Returns:
        str: The extracted video ID.
    """
    # Regular expression pattern to match YouTube video IDs
    pattern = r"(?:https?://(?:www\.)?youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        st.error("Invalid YouTube URL")
        return None

# Function to fetch comments from a YouTube video using YouTube Data API
def fetch_comments(video_id, api_key, max_comments=100):
    """
    Fetches comments from a YouTube video using the YouTube Data API.
    
    Args:
        video_id (str): The ID of the YouTube video.
        api_key (str): Your YouTube Data API key.
        max_comments (int): Maximum number of comments to fetch.
        
    Returns:
        list: A list of comment strings.
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
            if len(comments) >= max_comments:
                break

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return comments

# Function to analyze sentiment of comments
def analyze_sentiment(comments):
    """
    Analyzes the sentiment of comments using TextBlob.
    
    Args:
        comments (list): A list of comment strings.
        
    Returns:
        dict: Sentiment analysis results (positive, neutral, negative counts).
    """
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}

    for comment in comments:
        polarity = TextBlob(comment).sentiment.polarity
        if polarity > 0:
            sentiment_counts["positive"] += 1
        elif polarity == 0:
            sentiment_counts["neutral"] += 1
        else:
            sentiment_counts["negative"] += 1

    return sentiment_counts

# Function to plot sentiment analysis results with Matplotlib
def plot_sentiment_results(sentiment_counts):
    """
    Displays sentiment analysis results as a bar chart using matplotlib.
    """
    labels = sentiment_counts.keys()
    values = sentiment_counts.values()

    # Create a figure and axis object for customization
    fig, ax = plt.subplots(figsize=(8, 6))

    # Create a bar chart with beautiful colors
    bar_colors = ['#00FF00', '#808080', '#FF6347']  # Green, Gray, Red
    bars = ax.bar(labels, values, color=bar_colors, edgecolor='black', linewidth=1.5)

    # Add title and labels
    ax.set_title('Sentiment Analysis of YouTube Comments', fontsize=16, fontweight='bold', color='darkblue')
    ax.set_xlabel('Sentiment', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Comments', fontsize=14, fontweight='bold')

    # Customize tick labels
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    # Add value annotations on top of each bar
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 1, round(yval, 0), ha='center', fontsize=12, color='black')

    # Add gridlines for better readability
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Display the plot in Streamlit
    st.pyplot(fig)

# Streamlit main app
def main():
    st.title("YouTube Comment Sentiment Analysis")

    # User inputs
    api_key = get_youtube_api_key()
    video_url = st.text_input("Enter YouTube Video URL")

    if st.button("Analyze Sentiment") and api_key and video_url:
        video_id = get_video_id(video_url)
        if video_id:
            st.write(f"Extracted Video ID: {video_id}")

            # Fetch comments
            st.write("Fetching comments...")
            comments = fetch_comments(video_id, api_key)
            st.write(f"Fetched {len(comments)} comments.")

            # Analyze sentiment
            st.write("Analyzing sentiment...")
            sentiment_results = analyze_sentiment(comments)

            # Display sentiment results
            st.write(f"Sentiment Analysis Results: {sentiment_results}")

            # Plot sentiment analysis results with matplotlib
            plot_sentiment_results(sentiment_results)

if __name__ == "__main__":
    main()
