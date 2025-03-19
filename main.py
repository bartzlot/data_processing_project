import os
from information_fetching_scripts import get_config
from analyzing_scripts import yt_comments_analyzer

CONFIG = get_config.load_config()

if __name__ == '__main__':

    yt_analyzer = yt_comments_analyzer.CommentsAnalyzer()

    # Perform sentiment analysis for individual file
    # yt_analyzer.analyze_comments              ("d:\\Users\\SUPERKOMP\\Desktop\\Studia\\sem6\\Przetwarzanie_danych\\data_processing_project\\output\\comments\\comments_1.json")

    # Perform sentiment analysis for all files in the directory
    comments_dir = r"d:\Users\SUPERKOMP\Desktop\Studia\sem6\Przetwarzanie_danych\data_processing_project\output\comments"
    json_files = [f for f in os.listdir(comments_dir) if f.startswith("comments_") and f.endswith(".json")]
    
    for file_name in json_files:
        file_path = os.path.join(comments_dir, file_name)
        print(f"🔍 Processing: {file_path}")
        yt_analyzer.analyze_comments(file_path)
    
    print("✅ All files processed successfully!")
