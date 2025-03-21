import pytest
from fortune_teller.get_fortune import get_fortune

class TestGetFortune:
    @pytest.mark.parametrize("category", ["tech", "startup", "open source", "ai", "career"])
    def test_returns_str(self, category):
        """Check if the value that is returned is a string."""
        fortune_returned = get_fortune(category)
        assert isinstance(fortune_returned, str), f"String is expected here."

    def test_valid_tech(self):
        """Check if the valid only category tech returns one of the listed fortunes."""
        valid_only_tech = {
            "You will fix a bug... but create two new ones.",
            "Your commit messages will inspire thousands of developers.",
            "Your code will compile on the first try... eventually.",
            "Rubber duck debugging will save your day—just don't question the duck.",
            "A segfault in your future? Fear not, for logs will guide you.",
            "You will spend more time reading logs than writing code."
        }
        fortune_returned = get_fortune("tech")
        assert fortune_returned in valid_only_tech, (f"Valid fortunes are {valid_only_tech}, got {fortune_returned}")
    
    def test_value_error_raise(self):
        """Check if an invalid category raises a Valueerror and prompts the user to pick a valid one instead."""
        invalid_only = "internships"
        with pytest.raises(ValueError) as exc_info:
            get_fortune(invalid_only)
        error_text = str(exc_info.value)
        assert f"Sorry but '{invalid_only}' is not a category." in error_text
        assert f"Please pick on from this list:" in error_text
    
    
    def test_randomness(self):
        """Check for randomness: check if multiple calls for a given valid category return different fortunes."""
        fortune_returned = {get_fortune("tech") for _ in range(10)}
        assert len(fortune_returned) > 1, "Expected random fortunes every single time, but got the same fortune each time instead."

    @pytest.mark.parametrize("category, valid_fortunes", [
        ("tech", {
            "You will fix a bug... but create two new ones.",
            "Your commit messages will inspire thousands of developers.",
            "Your code will compile on the first try... eventually.",
            "Rubber duck debugging will save your day—just don't question the duck.",
            "A segfault in your future? Fear not, for logs will guide you.",
            "You will spend more time reading logs than writing code."
        }),
        ("startup", {
            "Your pitch deck will raise millions, as soon as you remove that one extra slide.",
            "A hidden co-founder is about to appear in your life.",
            "Your MVP will be hailed as the next big thing."
        }),
        ("open source", {
            "You will become a beloved maintainer of a widely used project.",
            "A community member's pull request will solve your trickiest issue.",
            "Your next contribution will inspire new developers to join open source."
        }),
        ("ai", {
            "Your ML model will become self-aware… proceed with caution!",
            "AI is just a fancy name for code that doesn't work yet.",
            "Your next project: bridging the gap between humans and robots."
        }),
        ("career", {
            "You're on the path to landing your dream developer job!",
            "One day you'll write the code that changes the world.",
            "Your LinkedIn profile will attract a special opportunity."
        })
    ])

    def test_valid_only_fortunes(self, category, valid_fortunes):
        """For each valid category, check if the returned fortune is one of the expected fortunes."""
        fortune_returned = get_fortune(category)
        assert fortune_returned in valid_fortunes, f"For category '{category}', the fortune '{fortune_returned}' is not valid."
    

