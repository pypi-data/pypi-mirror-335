
# This script provides movie recommendations based on different moods.
# Users can input their mood, and a relevant movie will be suggested.

# Dictionary containing categorized movie recommendations for various moods.
# Each mood is mapped to a list of movies that match its emotional tone.

# Function to recommend a movie based on the user's mood.
# It selects a random movie from the corresponding category.

import random
# Dictionary containing activity recommendations based on different moods
#Movie recommendations
MOVIE_RECOMMENDATIONS = {
    "Happy": [
        "Inside Out", 
        "La La Land", 
        "Forrest Gump", 
        "The Intouchables", 
        "The Grand Budapest Hotel",
        "Amelie",
        "The Princess Bride",
        "Singin' in the Rain",
        "Up",
        "Little Miss Sunshine",
        "The Secret Life of Walter Mitty",
        "Paddington 2",
      
    ],
    
    "Sad": [
        "The Pursuit of Happyness", 
        "Schindler's List", 
        "Manchester by the Sea", 
        "A Silent Voice", 
        "Grave of the Fireflies",
        "Inside Out",
        "Good Will Hunting",
        "About Time",
        "The Perks of Being a Wallflower",
        "Dead Poets Society",
        
    ],
    
    "Stressed": [
        "My Neighbor Totoro", 
        "The Perks of Being a Wallflower", 
        "Silver Linings Playbook", 
        "Black Swan", 
        "Joker",
        "Paddington",
        "Finding Nemo",
        "The Hundred-Foot Journey",
        "Julie & Julia",
        "The Secret Garden",
        "Chef",
        "The Peanut Butter Falcon",
   
    ],
    
    "Bored": [
        "The Secret Life of Walter Mitty", 
        "Call Me by Your Name", 
        "Ponyo", 
        "Spirited Away", 
        "Before Sunrise",
        "Lost in Translation",
        "The Before Trilogy",
        "The Tree of Life",
        "A Ghost Story",
        "Into the Wild",
        "The Farewell",
        "Moonlight",
       
    ],
    
    "Motivated": [
        "Rocky", 
        "The Social Network", 
        "Whiplash", 
        "The Pursuit of Happyness", 
        "Ford v Ferrari",
        "Moneyball",
        "Limitless",
        "The Wolf of Wall Street",
        "Rush",
        "Good Will Hunting",
        "Coach Carter",
        "Million Dollar Baby",
        
    ],
    
    "Angry": [
        "Joker", 
        "Fight Club", 
        "There Will Be Blood", 
        "A Clockwork Orange", 
        "John Wick",
        "Kill Bill: Vol. 1 & 2",
        "Falling Down",
        "Taxi Driver",
        "Mad Max: Fury Road",
        "Training Day",
        "The Revenant",
        "American History X",
        "Scarface",
        "V for Vendetta",
        "Nightcrawler",
        "No Country for Old Men",
        "Gladiator",
        "The Girl with the Dragon Tattoo"
    ]
}


def recommend_movie(mood: str) -> str:
    mood = mood.capitalize()  # Ensure consistency in capitalization
    return random.choice(MOVIE_RECOMMENDATIONS.get(mood, ["No recommendations available for this mood."]))