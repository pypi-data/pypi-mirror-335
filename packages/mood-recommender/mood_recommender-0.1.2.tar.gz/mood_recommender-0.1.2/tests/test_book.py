import pytest
from mood_suggester.book import recommend_book, BOOK_RECOMMENDATIONS

def test_recommend_book():
    moods = ["Happy", "Sad", "Stressed", "Bored","Motivated","Angry"]
    for mood in moods:
        book = recommend_book(mood)
        assert book in BOOK_RECOMMENDATIONS[mood]

def test_invalid_mood():
    assert recommend_book("") == "No recommendations available for this mood."
    assert recommend_book("excited") == "No recommendations available for this mood."
    assert recommend_book("so sad") == "No recommendations available for this mood."