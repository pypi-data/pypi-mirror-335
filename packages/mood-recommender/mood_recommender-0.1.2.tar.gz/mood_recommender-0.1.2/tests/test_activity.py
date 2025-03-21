import pytest
from mood_suggester.activity import recommend_activity, ACTIVITY_RECOMMENDATIONS

def test_recommend_activity_valid_mood():


    moods = ["happy", "sad", "stressed", "bored","motivated","angry"]
    for mood in moods:
        activity = recommend_activity(mood)
        assert activity in ACTIVITY_RECOMMENDATIONS[mood]

    """ for mood in activities.keys():
        activity = recommend_activity(mood)
        assert activity in activities[mood]   """

def test_recommend_activity_invalid_mood():

    assert recommend_activity("excited") == "Try something new!"
    assert recommend_activity("") == "Try something new!"
    assert recommend_activity("unknown") == "Try something new!"