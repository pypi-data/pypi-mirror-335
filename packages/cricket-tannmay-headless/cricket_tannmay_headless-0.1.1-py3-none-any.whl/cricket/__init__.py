from .batting.straight_drive import (classify_entire_video as classify_straight_drive,
                                     analyze_video as analyze_straight_drive)
from .batting.cover_drive import classify_entire_video as classify_cover_drive, analyze_video as analyze_cover_drive
from .batting.pull_shot import classify_entire_video as classify_pull_shot, analyze_video as analyze_pull_shot
from .batting.defense import classify_entire_video as classify_defence, analyze_video as analyze_defense
from .balling.fast import classify_entire_video as classify_fast_ball, analyze_video as analyze_fast_ball
from .balling.slow import classify_entire_video as classify_slow_ball, analyze_video as analyse_slow_ball
from .balling.yorker import classify_entire_video as classify_yorker, analyze_video as analyze_yorker
from .balling.spin import classify_entire_video as classify_spin, analyze_video as analyse_spin
from .balling.overall_bowl_detection import CricketBallAnalyzer
from .batting.overall_shot_detection import CricketShotClassifier
from .combined import classify_overall
from .utils import color_ranges

__all__ = [
    "classify_straight_drive",
    "analyze_straight_drive",
    "classify_cover_drive",
    "analyze_cover_drive",
    "analyze_pull_shot",
    "classify_pull_shot",
    "analyze_defense",
    "classify_defence",
    "classify_fast_ball",
    "analyze_fast_ball",
    "classify_slow_ball",
    "analyse_slow_ball",
    "classify_yorker",
    "analyze_yorker",
    "classify_spin",
    "analyse_spin",
    "classify_overall",
    "color_ranges",
    "CricketBallAnalyzer",
    "CricketShotClassifier"
]

__version__ = "0.1"
__author__ = "Tannmay Khandelwal"
__description__ = (
    "This package contains modules for detecting and assessing cricket shots "
    "using computer vision with MediaPipe, OpenCV, and TensorFlow."
)


def get_available_shots():
    """
    Returns a list of available shot types supported by this package.
    """
    return ["straight_drive", "pull_shot"]


def about():
    """
    Prints basic information about the cricket package.
    """
    print(f"Cricket Package - Version: {__version__}")
    print(f"Author: {__author__}")
    print(__description__)
