# Cricket
This is a package which can be used for assessing videos of bowling and batting.It is different from cricket as this can work in situations where opencv-python is throwing this type of error:
```text
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```
**Note:** Please add a packages.txt file inside your project having the following data:
```text
libgl1-mesa-glx
libglib2.0-0
libxrender1
```

## Installation
### Option 1
Use the command:
```commandline
pip install cricket-tannmay
```

### Option 2
Go to this [link](https://github.com/tannmaycoding/Cricket "The link for cricket github repository"). Then download the source code and `requirements.txt` and run this command:
```commandline
pip install -r requirements.txt
```

## How To Use
**Note:** The name to use while installing is `cricket-tannmay` but while using it in python we have to import `cricket` 
### Batting
#### Specific Shot
##### Option 1

This option will give a single string in return telling It will also if it was a:
- Good shot
- Bad shot
- Not the shot the function was called for

This is the implementation for the compatible shots: 
- Straight Drive:
```python
from cricket.batting import straight_drive
decision = straight_drive.classify_entire_video("video_path")
```
- Cover drive:
```python
from cricket.batting import cover_drive
decision = cover_drive.classify_entire_video("video_path")
```
- Pull shot:
```python
from cricket.batting import pull_shot
decision = pull_shot.classify_entire_video("video_path")
```
- Sweep:
```python
from cricket.batting import sweep
decision = sweep.classify_entire_video("video_path")
```
- Reverse sweep:
```python
from cricket.batting import reverse_sweep
decision = reverse_sweep.classify_entire_video("video_path")
```
- Hook shot:
```python
from cricket.batting import hook_shot
decision = hook_shot.classify_entire_video("video_path")
```
- Defense:
```python
from cricket.batting import defense
decision = defense.classify_entire_video("video_path")
```

##### Option 2
This will return a dictionary which tells about what it thinks at that frame, whether it is a:
- Good Shot
- Bad Shot
- Not the shot it was called for

This is the implementation for the compatible shots:
- Straight Drive:
```python
from cricket.batting import straight_drive
decision = straight_drive.analyze_video("video_path")
```
- Cover drive:
```python
from cricket.batting import cover_drive
decision = cover_drive.analyze_video("video_path")
```
- Pull shot:
```python
from cricket.batting import pull_shot
decision = pull_shot.analyze_video("video_path")
```
- Sweep:
```python
from cricket.batting import sweep
decision = sweep.analyze_video("video_path")
```
- Reverse sweep:
```python
from cricket.batting import reverse_sweep
decision = reverse_sweep.analyze_video("video_path")
```
- Hook shot:
```python
from cricket.batting import hook_shot
decision = hook_shot.analyze_video("video_path")
```
- Defense:
```python
from cricket.batting import defense
decision = defense.analyze_video("video_path")
```

#### Overall
```python
from cricket.batting import overall_shot_detection
classifier = overall_shot_detection.CricketShotClassifier()
classifier.classify_entire_video("video_path")
```
This classifier class is compatible with the following shots:
- Straight Drive
- Cover Drive
- Sweep
- Defence
- Reverse Sweep
- Pull Shot
- Hook Shot

This will also return if it was a:
- Good Shot
- Bad Shot

### Balling
#### Specific Type

```python
from cricket.balling import fast
import cricket.utils as utils

ball_colour_range = utils.color_ranges["white"]
decision = fast.classify_entire_video("video_path", ball_colour_range)
```
This method is compatible with:
- Fast ball
- Slow ball
- Yorker
- Spin

This was an implementation of a fast ball. It will also tell if it was a:
- Good Delivery
- Bad Delivery

#### Overall
```python
from cricket.balling.overall_bowl_detection import CricketBallAnalyzer
import cricket.utils as utils

ball_colour_range = utils.color_ranges["white"]
analyser = CricketBallAnalyzer("video_path", ball_colour_range[0], ball_colour_range[1], 22)
decision = analyser.analyze_video()
```
This classifier class is compatible with:
- Fast Ball
- Slow ball
- Yorker
- Spin

### Combined
```python
from cricket.combined import classify_overall
import cricket.utils as utils

ball_colour = utils.color_ranges["white"]
decision = classify_overall("video_path", ball_colour, 22)
```

This will run both the classes given above and will return a dictionary. First key will be of bowling and second key will be of batting

**Note:** For ease of use you can import like this and it would import all things for implementation from both the subpackages
```python
from cricket import *
```