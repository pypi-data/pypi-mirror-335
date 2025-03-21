from .fast import classify_entire_video as classify_fast_ball, analyze_video as analyze_fast_ball
from .slow import classify_entire_video as classify_slow_ball, analyze_video as analyse_slow_ball
from .yorker import classify_entire_video as classify_yorker, analyze_video as analyze_yorker
from .spin import classify_entire_video as classify_spin, analyze_video as analyse_spin
from .overall_bowl_detection import CricketBallAnalyzer

__all__ = [
    "classify_fast_ball",
    "analyze_fast_ball",
    "classify_slow_ball",
    "analyse_slow_ball",
    "classify_yorker",
    "analyze_yorker",
    "classify_spin",
    "analyse_spin",
    "CricketBallAnalyzer"
]

__version__ = "0.1"
__author__ = "Tannmay Khandelwal"
__description__ = (
    "This package contains modules for detecting and assessing cricket bowling using computer vision with MediaPipe, "
    "OpenCV, and Numpy."
)


def get_available_shots():
    """
    Returns a list of available shot types supported by this package.
    """
    return ["Fast ball", "Slow ball", "Yorker", "Spin"]


def about():
    """
    Prints basic information about the cricket package.
    """
    print(f"Cricket Balling Package - Version: {__version__}")
    print(f"Author: {__author__}")
    print(__description__)
