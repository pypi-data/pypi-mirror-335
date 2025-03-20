import pytest
import random
from src.emotive import emotive

class Tests: 

    @pytest.fixture
    def example_fixture(self):
        emotion_list = ["happy", "friendly", "laughing", "laugh", "numb", "wordless", "surprise", "angry", "sad", "cheated", " "]
        emotion = random.choice(emotion_list)
        s = "Hello, World!"
        return s, emotion
    
    def test_sanity_check(self, example_fixture): 
        expected = True
        actual = True
        assert actual == expected, "Expected True to be equal to True!"

    def test_emotion(self, example_fixture):
        s, emotion = example_fixture
        for i in range(100): 
            actual = emotive(s, emotion)
            assert isinstance(
                actual, str
            ), f"Expected emoji() to return a string. Instead, it return {actual}"
            assert (
                len(actual) > 0
            ), f"Expected emoji() not to be empty. Instead, it returned a string with {len(actual)} characters"

    def test_content(self, example_fixture):
        s, emotion = example_fixture
        actual = emotive(s, emotion)
        print(emotion)

        if (emotion == "happy"):
            expected = s + "\U0001F601"
        elif (emotion == "friendly"):
            expected = s + "\U0001F603"
        elif (emotion == "laughing"):
            expected = s + "\U0001F602"
        elif (emotion == "love"):
            expected = s + "\U0001F60D"
        elif (emotion == "numb"):
            expected =  s + "\U0001F611"
        elif (emotion == "wordless"):
            expected = s + "\U0001F612"
        elif (emotion == "surprise"):
            expected = s + "\U0001F92F"
        elif (emotion == "angry"):
            expected = s + "\U0001F621"
        elif (emotion == "sad"):
            expected = s + "\U0001F62D"
        elif (emotion == "cheated"):
            expected = s + "\U0001F921"
        else: 
            expected = s + "\U0001F92B"
        
        assert (actual == expected), f"Expected the string returned by emoji() to be with emotion {emotion}. Instead, it returned '{actual}'"