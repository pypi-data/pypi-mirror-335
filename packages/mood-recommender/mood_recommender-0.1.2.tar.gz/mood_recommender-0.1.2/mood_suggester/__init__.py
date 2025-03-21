#Import functions
from .music import recommend_music
from .movie import recommend_movie
from .activity import recommend_activity
from .book import recommend_book

__all__ = ["recommend_music", "recommend_movie", "recommend_activity", "recommend_book"]
