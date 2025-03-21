from .batting.overall_shot_detection import CricketShotClassifier
from .balling.overall_bowl_detection import CricketBallAnalyzer
import cricket.utils


def classify_overall(video, ball_colour, pitch_length):
    bat = CricketShotClassifier()
    bat_decision = bat.classify_entire_video(video)
    ball = CricketBallAnalyzer(video, cricket.utils.color_ranges[ball_colour][0], cricket.utils.color_ranges[ball_colour][1], pitch_length)
    ball_decision = ball.analyze_video()
    return {"ball": ball_decision, "bat": bat_decision}
