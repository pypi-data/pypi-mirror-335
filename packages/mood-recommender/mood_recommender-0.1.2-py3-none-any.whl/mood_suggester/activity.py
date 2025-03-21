import random

# Dictionary containing activity recommendations based on different moods
ACTIVITY_RECOMMENDATIONS = {
    "happy": ["Go for a walk in the park", 
                "Attend a friend's party", 
                "Try out new hobbies", 
                "Listen to your favorite music",
                "Try something creative",
                "Exercise or play a sport",
                "Enjoy a favorite meal, dessert, or relaxing spa day",
                "Call or meet up with a friend and spread the joy",
                "Dance, sing along, or just vibe to the beat",
                "Take a spontaneous trip",
                "Help a friend, volunteer, or surprise someone with a small gift",
                "Watch a funny movie, read jokes, or play games",
                "Write in a journal",
                "Dance, sing along, or just vibe to the beat of your favorite playlist",
                "Take a spontaneous trip to a nearby city or go on a road trip",
                "Help a friend, volunteer, or surprise someone with a small gift",
                "Watch a funny movie, read jokes, or play interactive games with friends",
                "Write in a journal about your happiest memories or things you're grateful for",
                "Visit an amusement park, zoo, or museum for a fun experience",
                "Try adrenaline-rushing activities like zip-lining or indoor skydiving"],
    
    "sad": ["Write in a journal", 
            "Meditate",
            "Get fresh air to clear your mind",
            "Watch a comforting movie",
            "Share how you feel with someone who cares",
            "Practice deep breathing",
            "Draw, paint, write, or play music to channel your feelings into art",
            "A little movement, like stretching, yoga, or a short walk, can boost your mood",
            "Cuddle with a pet",
            "Watch cute animal videos",
            "Draw, paint, write, or play music to channel your feelings into art",
            "A little movement, like stretching, yoga, or a short walk, can boost your mood",
            "Cuddle with a pet or watch cute animal videos to lift your spirits",
            "Try aromatherapy with calming scents like lavender or chamomile",
            "Read an uplifting book or listen to a soothing podcast",
            "Light candles, dim the lights, and take a long, warm bath",
            "Cook your comfort food and enjoy it mindfully",
            "Do something nostalgic, like revisiting old childhood photos or watching childhood cartoons"],
    
    "stressed": ["Do deep breathing exercises", 
                 "Practice yoga", 
                 "Drink a hot cup of tea",
                 "Go for a walk or exercise",
                 "Play calming music, nature sounds, or even white noise to create a relaxing atmosphere",
                 "Take a warm shower or bath",
                 "Disconnect from screens and take a break from social media",
                 "Watch a funny movie or stand-up comedy to lighten your mood",
                 "Try aromatherapy with lavender or chamomile scents",
                 "Write down what's stressing you and break it into smaller, manageable steps",
                 "Watch a funny movie, stand-up comedy, or lighthearted TV show to distract yourself",
                 "Try aromatherapy with lavender or peppermint essential oils",
                 "Write down what's stressing you and break it into smaller, manageable steps",
                 "Spend time with animals, whether it's your pet or visiting an animal shelter",
                 "Declutter your workspace or bedroom for a sense of control",
                 "Do progressive muscle relaxation exercises to ease tension",
                 "Take a quick nap or power nap if you're feeling overwhelmed"],
    
    "bored": ["Try out a new hobby like painting, knitting, or photography", 
              "Learn a new skill through an online course or tutorial",
              "Read a book or listen to an audiobook",
              "Cook or bake something new and experiment with different recipes",
              "Explore a new place in your city or take a spontaneous road trip",
              "Solve a puzzle, play a board game, or try an escape room challenge",
              "Write a short story, poem, or start a blog",
              "Declutter and reorganize your room for a fresh start",
              "Volunteer for a local cause or help someone in need",
              "Challenge yourself with a DIY project or build something creative",
              "Volunteer for a local cause or help someone in need",
                "Challenge yourself with a DIY project or build something creative",
                "Try a new form of exercise like rock climbing, skating, or kickboxing",
                "Create a vision board with your goals and inspirations",
                "Play an instrument or learn a new song on guitar, piano, or another instrument"],
    
    "motivated": ["Set a new goal and plan out the steps to achieve it", 
                  "Hit the gym or do an intense workout",
                  "Read an inspiring book or listen to a motivational podcast",
                  "Write down affirmations or visualize your success",
                  "Work on a passion project or learn a new skill",
                  "Surround yourself with like-minded, driven people",
                  "Watch TED talks or success stories to fuel your drive",
                  "Organize your workspace and create a productive environment",
                  "Surround yourself with like-minded, driven people to stay motivated",
                    "Watch TED talks, motivational speeches, or success stories",
                    "Organize your workspace and create a productive environment",
                    "Take an online masterclass in something that interests you",
                    "Join a challenge, like a 30-day fitness or personal growth challenge",
                    "Celebrate small wins to keep momentum going",
                    "Create a motivational playlist with pump-up songs to keep you going"],
    
    "angry": ["Do a high-intensity workout or go for a run", 
              "Write down your thoughts, then tear up the paper or burn it safely", 
              "Listen to aggressive music or play an instrument to release tension",
              "Practice controlled breathing exercises",
              "Hit a punching bag or squeeze a stress ball",
              "Take a cold shower to reset your emotions",
              "Talk it out with someone you trust",
              "Engage in a creative activity like painting, writing, or playing a video game to redirect your energy",
              "Engage in a creative activity like painting, writing, or playing a video game to redirect your energy",
                "Go for a long drive with your favorite music blasting",
                "Try guided meditation focused on anger management",
                "Walk outside or be in nature to physically distance yourself from the frustration",
                "Practice gratitude by listing things you’re thankful for",
                "Write an unsent letter to express your feelings privately"]

}

"""
    Given a mood, recommend a random book from the corresponding category.

    Parameters:
        mood (str): The user's current mood.
    
    Returns:
        str: A recommended book title.
"""

def recommend_activity(mood: str) -> str:
    mood = mood.capitalize()  # Ensure consistency in capitalization
    return random.choice(ACTIVITY_RECOMMENDATIONS.get(mood.lower(), ["Try something new!"]))