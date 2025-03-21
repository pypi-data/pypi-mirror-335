from .straight_drive import classify_entire_video as classify_straight_drive, analyze_video as analyze_straight_drive
from .cover_drive import classify_entire_video as classify_cover_drive, analyze_video as analyze_cover_drive
from .pull_shot import classify_entire_video as classify_pull_shot, analyze_video as analyze_pull_shot
from .defense import classify_entire_video as classify_defence, analyze_video as analyze_defense
from .hook_shot import classify_entire_video as classify_hook_shot, analyze_video as analyse_hook_shot
from .sweep import classify_entire_video as classify_sweep, analyze_video as analyse_sweep
from .reverse_sweep import classify_entire_video as classify_reverse_sweep, analyze_video as analyse_reverse_sweep
from .overall_shot_detection import CricketShotClassifier

__all__ = [
    "classify_straight_drive",
    "analyze_straight_drive",
    "classify_cover_drive",
    "analyze_cover_drive",
    "analyze_pull_shot",
    "classify_pull_shot",
    "analyze_defense",
    "classify_defence",
    "classify_sweep",
    "analyse_sweep",
    "classify_hook_shot",
    "analyse_hook_shot",
    "classify_reverse_sweep",
    "analyse_reverse_sweep",
    "CricketShotClassifier"
]

__version__ = "0.1"
__author__ = "Tannmay Khandelwal"
__description__ = (
    "This package contains modules for detecting and assessing cricket shots using computer vision with MediaPipe, "
    "OpenCV, and Numpy."
)


def get_available_shots():
    """
    Returns a list of available shot types supported by this package.
    """
    return ["straight drive", "pull shot", "sweep", "reverse sweep", "hook shot", "defence", "cover drive"]


def about():
    """
    Prints basic information about the cricket package.
    """
    print(f"Cricket Batting Package - Version: {__version__}")
    print(f"Author: {__author__}")
    print(__description__)
