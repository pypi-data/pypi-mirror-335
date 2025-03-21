# chugthiskoolaid

## Badges
[![log github events](https://github.com/software-students-spring2025/3-python-package-chugthiskoolaid/actions/workflows/event-logger.yml/badge.svg)](https://github.com/software-students-spring2025/3-python-package-chugthiskoolaid/actions/workflows/event-logger.yml)

[![CI](https://github.com/software-students-spring2025/3-python-package-chugthiskoolaid/actions/workflows/python-package.yml/badge.svg)](https://github.com/software-students-spring2025/3-python-package-chugthiskoolaid/actions/workflows/python-package.yml)

## Team members

- Jess Liang: [GitHub](https://github.com/jess-liang322)  
- Yukun Dong: [GitHub](https://github.com/abccdyk)  
- Hao Yang: [GitHub](https://github.com/Hao-Yang-Hao)  
- Yifan Zhang: [GitHub](https://github.com/YifanZZZZZZ)
  
## TABLE OF CONTENTS
1. [Description](#description)
2. [PyPI Page](#pypi-page)
3. [Installation](#installation)
4. [Virtual Environment & Dependencies](#virtual-environment--dependencies)
5. [Usage Examples](#usage-examples)
6. [Contributing](#contributing)

## Description
Mood Recommender is your ultimate boredom-busting, vibe-matching companion! 🎉
Whether you're feeling happy, stressed, bored, or just looking for something fun to do, this package has got you covered. 
Get personalized recommendations for activities, books, movies, and music based on your mood—because sometimes, all you need is the perfect song, a great read, or a wild adventure to turn your day around. 
Just tell us how you’re feeling, and we’ll do the rest. 
Let the good vibes roll! 😎🎶📖🎬

## PyPI Page
You can find the package here: [Mood-recommender](https://pypi.org/project/mood-recommender/)

## Installation

You can import the Mood Recommender package into your projects using pip. 
Below is how to install the package:

**1. Install the package from PyPI**
``` bash
pip install mood-recommender
```

**2. Import the functions in your Python code**
``` bash
from mood_suggester import recommend_activity, recommend_book, recommend_movie, recommend_music
```
## Virtual Environment & Dependencies

1️⃣ **Clone the Repository**
``` bash
git clone https://github.com/software-students-spring2025/3-python-package-chugthiskoolaid.git
cd 3-python-package-chugthiskoolaid
```

2️⃣ **Create a Virtual Environment**
``` bash
python -m venv venv
```
For MacOS/Linux:
```bash
source venv/bin/activate
```
For Windows:
```bash
venv\Scripts\activate
```

3️⃣ **Install Dependencies**
```bash
pip install -r .github/workflows/requirements.txt
```

4️⃣ **Run Tests**
```bash
pytest tests/
```

5️⃣ **Build the Package**
```bash
python setup.py sdist bdist_wheel
```

## Usage Examples
For a detailed example of how to use this package, please refer to example.py, which contains comprehensive demonstrations of the available functions. Below is a brief overview of how each function can be used.

## 1. recommend_activity:

Feeling restless?  Inspired?  Maybe a little down?  Not sure what to do? Let your emotions guide you! No worries—I have just the right activity to match your mood and help you make the most of your day!

How are you feeling now? (happy/sad/stressed/bored/motivated/angry): bored

🎉 activity: Solve a puzzle, play a board game, or try an escape room challenge

## 2. recommend_book:

Books have a unique way of reflecting and shaping our emotions.  Whether you're feeling adventurous and craving an epic journey, or simply looking for a heartwarming story to lift your spirits, there’s a perfect book waiting for you.  Tell me how you're feeling, and I'll recommend a story that resonates with your mood and transports you to the world you need most right now!

How are you feeling now? (happy/sad/stressed/bored/motivated/angry): happy

📖 book: The Hundred-Year-Old Man Who Climbed Out the Window and Disappeared – Jonas Jonasson

## 3. recommend_movie:

Looking for a movie that fits your emotions? Whether you're in the mood for action, romance, or something uplifting, I’ve got a perfect recommendation just for you!

How are you feeling now? (happy/sad/stressed/bored/motivated/angry): angry

🍽 movie: The Revenant

## 4. recommend_music:

Music speaks when words can’t. Every mood has a melody to match. Tell me how you're feeling, and I'll find the perfect song to match your vibe and emotions!

How are you feeling now? (happy/sad/stressed/bored/motivated/angry): bored

🎵 music: Young Folks - Peter Bjorn and John

## Contributing  

We welcome contributions! If you would like to improve **Mood Recommender**, follow these steps:  

### 1️⃣ Fork the Repository  
Click on the **Fork** button at the top-right corner of the repository page.  

### 2️⃣ Clone the Repository  
```bash
git clone https://github.com/your-username/mood-recommender.git
cd mood-recommender
```

### 3️⃣ Create a Virtual Environment
```bash
python -m venv venv
```
For MacOS/Linux:
```bash
source venv/bin/activate
```
For Windows:
```bash
venv\Scripts\activate
```

### 4️⃣ Install Dependencies
```bash
pip install -r .github/workflows/requirements.txt
```

### 5️⃣ Create a New Branch
```bash
git checkout -b feature-branch
```

### 6️⃣ Make Your Changes
```bash
git add .
git commit -m "Add new feature"
```
### 7️⃣ Push Changes
```bash
git push origin feature-branchs
```

### 8️⃣ Submit a Pull Request
Go to the original repository on GitHub.
Click on Pull Requests > New Pull Request.
Select your branch and submit a Pull Request (PR) for review.

## 📜 License
This project is licensed under the MIT License. See the LICENSE.txt file for details.

