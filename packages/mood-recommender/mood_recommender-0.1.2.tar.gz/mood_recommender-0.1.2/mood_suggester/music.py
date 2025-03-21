import random

# Dictionary containing activity recommendations based on different moods
music = {
    "happy": ["Pop music", 
              "Upbeat electronic music",
              "Walking on a Dream - Empire of the Sun",
              "Good as Hell - Lizzo",
              "The Nights - Avicii",
              "Put Your Records On - Corinne Bailey Rae",
              "Can’t Stop the Feeling - Justin Timberlake",
              "September - Earth, Wind & Fire",
              "Love Me Again - John Newman"],

    "sad": ["Soft piano music", 
            "Lyrical ballads",
            "The Night We Met - Lord Huron",
            "Fix You - Coldplay",
            "I Will Follow You into the Dark - Death Cab for Cutie",
            "Lost Cause - Billie Eilish",
            "When We Were Young - Adele",
            "Wake Me Up When September Ends - Green Day",
            "To Build a Home - The Cinematic Orchestra",
            "The Scientist - Coldplay",
            "Hard Sometimes - Ruel"],

    "stressed": ["Nature sounds", 
                 "Calm instrumental music",
                 "Weightless - Marconi Union",
                 "Sunset Lover - Petit Biscuit",
                 "Holocene - Bon Iver",
                 "Clair de Lune - Claude Debussy",
                 "River Flows in You - Yiruma",
                 "Bloom - The Paper Kites",
                 "Opus 23 - Dustin O'Halloran",
                 "Night Owl - Galimatias",
                 "Breathe Me - Sia",
                 "Saturn - Sleeping at Last"],

    "bored": ["Jazz", 
              "Rock music",
              "Dog Days Are Over - Florence + The Machine",
              "Take a Walk - Passion Pit",
              "Paper Planes - M.I.A.",
              "Houdini - Foster the People",
              "Are You Bored Yet? - Wallows ft. Clairo",
              "Go Your Own Way - Fleetwood Mac",
              "Dance, Dance - Fall Out Boy",
              "Young Folks - Peter Bjorn and John",
              "Shut Up and Dance - WALK THE MOON",
              "HandClap - Fitz and The Tantrums"],
    
    "motivated": ["Eye of the Tiger", 
                  "Stronger - Kanye West", 
                  "Lose Yourself - Eminem", 
                  "We Will Rock You - Queen", 
                  "Can't Hold Us - Macklemore & Ryan Lewis", 
                  "Till I Collapse - Eminem", 
                  "Remember the Name - Fort Minor", 
                  "Unstoppable - Sia", 
                  "Hall of Fame - The Script", 
                  "Born to Run - Bruce Springsteen"],

    "angry": ["Break Stuff - Limp Bizkit", 
              "Killing in the Name - Rage Against the Machine", 
              "Smells Like Teen Spirit - Nirvana", 
              "Duality - Slipknot", 
              "Bodies - Drowning Pool", 
              "Headstrong - Trapt", 
              "The Way I Am - Eminem", 
              "Before I Forget - Slipknot", 
              "Down with the Sickness - Disturbed", 
              "Psychosocial - Slipknot"]
}

def recommend_music(mood: str) -> str:
    mood = mood.capitalize()  # Ensure consistency in capitalization
    return random.choice(music.get(mood.lower(), ["Explore a new music genre!"]))