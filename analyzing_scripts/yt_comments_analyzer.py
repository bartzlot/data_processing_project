import os
import json
import re
import pandas as pd
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
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(os.path.dirname(__file__), "..", "output", "comments", file_name)
        analyzed_file_path = os.path.join(save_dir, f"analyzed_comments_{current_time}")

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
            word_counts = [len(re.findall(r'\b\w+\b', text)) for text in texts]
            unique_word_count = [len(set(re.findall(r'\b\w+\b', text.lower()))) for text in texts]
            char_count = [len(text) for text in texts]
            sentiments = self.get_batch_sentiments(texts)
            analyzed_data = [
                {"text": text, "likes": like, "words_amount": word_counts, "unique_word_count": unique_word_count, "char_count": char_count, "sentiment": sentiment}
                for text, like, word_counts, unique_word_count, char_count, sentiment in zip(texts, likes, word_counts, unique_word_count, char_count, sentiments)
            ]

            self.save_to_json(analyzed_data, f"{analyzed_file_path}.json")
            self.save_to_csv(analyzed_data, f"{analyzed_file_path}.csv")

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


    def save_to_json(self, analyzed_data, json_path):
        """
        Saves the analyzed data to a JSON file.
        """
        try:
            with open(json_path, 'w', encoding='utf-8') as file:
                json.dump(analyzed_data, file, indent=4, ensure_ascii=False)
            print(f"Successfully saved JSON file: {json_path}")
        except Exception as e:
            print(f"Error saving JSON file: {e}")


    def save_to_csv(self, analyzed_data, csv_path):
        """
        Saves the analyzed data to a CSV file.
        """
        try:
            df = pd.DataFrame(analyzed_data)
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"uccessfully saved CSV file: {csv_path}")
        except Exception as e:
            print(f"Error saving CSV file: {e}")
