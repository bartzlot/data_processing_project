from information_fetching_scripts import get_config
from analyzing_scripts import yt_comments_analyzer

CONFIG = get_config.load_config()

if __name__ == '__main__':

    yt_analyzer = yt_comments_analyzer.CommentsAnalyzer()
    yt_analyzer.analyze_comments("")
