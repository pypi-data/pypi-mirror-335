# import function from main .py in final version
from fortune_teller.mood_fortune import mood_fortune
import pytest
# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(
#     os.path.dirname(__file__), '..')))  # add project root into path


class TestEmojiFortune:

    @pytest.fixture # defines different tests which are done
    def valid_moods(self):
        """Provides the valid moods available in emoji_fortune."""
        return ["positive", "funny", "cursed", "motivational"]

    @pytest.fixture
    def fortune_dict(self):
        """A dictionary containing all the currently valid fortunes from emoji_fortune."""
        return {
            "positive": [
                "Your next 🏗️ `build` will succeed on the first try. 🚀",
                "You will finally master `regex` and feel like a 🧙‍♂️.",
                "Your next `git pull` will not cause a 🔥 merge conflict. Rejoice!",
                "A PR review will leave a 🌟 `LGTM` instead of nitpicks.",
                "Your bug 🐛 will fix itself while you’re making ☕.",
                "You will find an obscure `CLI` command that saves you ⏳.",
                "Your next `Docker` container will work… without 😱 debugging.",
            ],
            "funny": [
                "You will find a `fix` for your bug… in a 2008 Stack Overflow post. 🕰️",
                "Your code will work on your machine… and nowhere else. 🏠💻",
                "Your next `npm install` will require a fresh OS install. 😭💾",
                "Your `print(debug)` statement will fix everything… until you remove it. 🧐",
                "You’ll spend 3 hours debugging… and it was just `cAsE sEnSiTiViTy`. 🤦‍♂️",
                "Your next feature request will be 'Just add AI'. 🤖✨",
                "Your `README.md` will be out of date before you hit save. 📜🔥",
            ],
            "cursed": [
                "You will find a `TODO` in the code… last updated in 2015. ☠️",
                "Your PR will break everything… and the only test that fails is ✅ `test_example.py`.",
                "Your `git rebase` will go horribly wrong… but you’ll pretend it didn’t. 😅",
                "Your `database migration` will fail… and no one knows why. 🕵️‍♂️🗄️",
                "Your `deploy` will work fine… until 🌙 when it mysteriously crashes.",
                "Your next `hotfix` will become a permanent feature. 👀",
                "A manager will say 'This will be a small change'. 🚨",
            ],
            "motivational": [
                "You are not an 'imposter' — you are a developer. Believe in yourself. 💪🚀",
                "Every great coder was once a beginner. Keep pushing! 🔥💡",
                "Your past mistakes do not define your future commits. 🌱✨",
                "You are one Google search away from solving your problem. 🔍💡",
                "Debugging is just another word for learning. Stay curious! 🧠💻",
                "The best way to write better code is to keep writing code. 🏗️📜",
                "You got this! One line at a time, one function at a time. Keep building. 💪💻",
            ]
        }

    def test_returns_string(self):
        """Verify that emoji_fortune always returns a string."""
        result = mood_fortune()
        assert isinstance(
            result, str), "emoji_fortune() should return a string."

    def test_valid_fortune(self, fortune_dict):
        """Verify that the returned fortune is within the predefined fortunes."""
        all_fortunes = sum(fortune_dict.values(), [])
        result = mood_fortune()
        assert result in all_fortunes, f"Returned fortune should be a valid option, got {result}"

    @pytest.mark.parametrize("mood", ["positive", "funny", "cursed", "motivational"])
    def test_mood_fortune(self, mood, fortune_dict):
        """Verify that emoji_fortune(mood) returns a fortune from the correct category."""
        result = mood_fortune(mood)
        assert result in fortune_dict[mood], f"Expected a {mood} fortune, but got: {result}."


    @pytest.mark.parametrize("mood", ["positive", "funny", "cursed", "motivational"])
    def test_randomness(self, mood):
        """Ensure the function returns different fortunes over multiple calls."""
        results = {mood_fortune(mood) for _ in range(10)}
        assert len(
            results) > 1, "emoji_fortune() should return different results over multiple calls"

    @pytest.mark.parametrize("mood", ["positive", "funny", "cursed", "motivational"])
    def test_all_moods_have_variety(self, mood, fortune_dict):
        """Ensure that multiple calls for each mood return different fortunes."""  # i.e. make sure randomization happens
        results = {mood_fortune(mood) for _ in range(10)}
        assert len(
            results) > 1, f"emoji_fortune('{mood}') should return different fortunes."
