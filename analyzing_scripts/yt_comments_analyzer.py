import os
import json
import re
import requests
from datetime import datetime
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

class CommentsAnalyzer:


    def __init__(self, model_name = "nlptown/bert-base-multilingual-uncased-sentiment"):
        """
        Initialize the CommentsAnalyzer with an API key.
        :param api_key: AI API key
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)


    def analyze_comments(self, file_name: str):
        """
        Reads comments from a JSON file, analyzes their sentiment using OpenRouter API, and saves the results.
        """
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_dir = os.path.join(os.path.dirname(__file__), "..", "output", "sentiment_analysis")
        file_path = os.path.join(os.path.dirname(__file__), "..", "output", "comments", file_name)
        analyzed_file_path = os.path.join(save_dir, f"analyzed_comments_{current_time}.json")

        if not os.path.exists(file_path):
            print("Error: comments.json file not found.")
            return
        
        try:

            with open(file_path, 'r', encoding='utf-8') as file:
                comments_data = json.load(file)

            if not comments_data:
                print("No comments found in the file.")
                return

            texts = [entry["text"] for entry in comments_data]
            likes = [entry["likes"] for entry in comments_data]
            sentiments = self.get_batch_sentiments(texts)
            print(sentiments)
            analyzed_data = [
                {"text": text, "likes": like, "sentiment": sentiment}
                for text, like, sentiment in zip(texts, likes, sentiments)
            ]

            with open(analyzed_file_path, 'w', encoding='utf-8') as file:
                json.dump(analyzed_data, file, indent=4, ensure_ascii=False)

            print(f'Sentiment analysis saved to {analyzed_file_path}')
        except Exception as e:
            print(f'Error processing comments: {e}')


    def get_batch_sentiments(self, comments: list) -> list:
        """
        Processes a batch of comments and classifies sentiment using the multilingual model.
        """
        # Tokenize texts efficiently
        inputs = self.tokenizer(comments, return_tensors="pt", padding=True, truncation=True).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        if predictions.shape[1] != 5:
            print(f"Unexpected number of classes: {predictions.shape[1]}")
            return ["Error"] * len(comments)

        star_ratings = predictions.argmax(dim=-1).cpu().numpy() + 1 

        sentiment_labels = {
            1: "Very Negative",
            2: "Negative",
            3: "Neutral",
            4: "Positive",
            5: "Very Positive"
        }

        sentiments = [sentiment_labels.get(rating, "Error") for rating in star_ratings]
        return sentiments
