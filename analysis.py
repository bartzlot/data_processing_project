from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer
from scipy.special import softmax
import numpy as np
import json
import argparse
from config import LIKES_COEFFICIENT, SENTIMENT_MODEL

class SentimentModel:
    def __init__(self, model_path: str):
        self.labels = ['Negative', 'Neutral', 'Positive']
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.tokenizer.save_pretrained(model_path)
        self.model.save_pretrained(model_path)

    # Preprocess text (username and link placeholders)
    @staticmethod
    def _preprocess(text: str) -> str:
        '''
        Preprocesses given text the way it was preprocessed before model training
        :param text: Comment text
        :return: Preprocessed text
        '''
        new_text = []
        for t in text.split(" "):
            t = '@user' if t.startswith('@') and len(t) > 1 else t
            t = 'http' if t.startswith('http') else t
            new_text.append(t)
        return " ".join(new_text)

    def analyze(self, text: str):
        '''
        Get the sentiment scores of a comment text
        :param text: comment content to be analyzed
        :return:
        '''
        text = self._preprocess(text)
        encoded_input = self.tokenizer(text, return_tensors='pt')
        output = self.model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        return scores

    def analyze_all(self, comments, likes_coeff: int=0, verbose=False):
        '''
        Analyze a list of comments with likes count
        :param comments: List of comments with likes
        :param likes_coeff: How much are the comment likes taken into account
        :param verbose: Log every comment score to stdout
        :return: Average computed score
        '''
        overall_average = np.zeros(3, dtype=float)
        try:
            max_likes = max(comment_obj['likes'] for comment_obj in comments)
        except KeyError:
            max_likes = 1  # to avoid zero division error
        k = -likes_coeff / (likes_coeff - 1)
        m = k / max_likes
        weight_sum = 0
        for comment_obj in comments:
            text = comment_obj['text']
            likes = comment_obj.get('likes', 0)
            scores = self.analyze(text)
            weight = 1 + m * likes
            weight_sum += weight
            overall_average += scores * weight

            if verbose:
                print(text)
                for i in range(len(self.labels)):
                    print(f'{self.labels[i]}: {scores[i]}')
                print()

        overall_average /= weight_sum
        return overall_average

    def print_result(self, result):
        '''
        Print labeled results to stdout
        :param result:
        :return:
        '''
        for i in range(len(self.labels)):
            print(f'{self.labels[i]}: {result[i]:.2%}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    model = SentimentModel(SENTIMENT_MODEL)

    if args.file:
        f = open(args.file)
        comments = json.load(f)
        model.analyze_all(comments, LIKES_COEFFICIENT)
    else:
        print('No file specified, running interactive model test')
        while text := input('> '):
            scores = model.analyze(text)
            model.print_result(scores)
