import pytest
import re
from fortune_teller.date_time import rand_date_time

class TestRandDateTime:
    @pytest.fixture
    def sample_fortune(self):
        return "You will write perfect code today! 🚀"

    def test_basic_functionality(self, sample_fortune):
        """Verify that the function correctly embeds the provided fortune."""
        result = rand_date_time(sample_fortune)
        assert sample_fortune in result, f"Expected fortune to be included in result: {result}"

    def test_date_formatting(self, sample_fortune):
        """Ensure the returned string follows the expected date formatting."""
        result = rand_date_time(sample_fortune)
        assert "📅 On " in result, "Date formatting missing from output"
        assert any(day in result for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]), "Day of week missing"
        assert any(month in result for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]), "Month missing"
    
    def test_randomness(self, sample_fortune):
        """Ensure that multiple calls produce different dates (randomness check)."""
        results = {rand_date_time(sample_fortune) for _ in range(10)}
        assert len(results) > 1, "rand_date_time should produce varying results"

    def test_year_range(self, sample_fortune):
        """Ensure that the generated year is within the expected range (2025-2060)."""
        result = rand_date_time(sample_fortune)

        # Use regex to extract a four-digit year from the string
        match = re.search(r'\b(202[5-9]|20[3-5][0-9]|2060)\b', result)
        assert match, f"No valid year found in result: {result}"

        year = int(match.group())
        assert 2025 <= year <= 2060, f"Year {year} is out of expected range"


    def test_return_type(self, sample_fortune):
        """Ensure that the function returns a string."""
        result = rand_date_time(sample_fortune)
        assert isinstance(result, str), "Return value should be a string"

    def test_various_fortunes(self):
        """Ensure function handles multiple different fortune inputs correctly."""
        sample_fortunes = [
            "You will finally fix that bug you've been struggling with! 🐛",
            "A mysterious error message will lead you to a breakthrough. 💡",
            "Your code will run perfectly... on the first try! 🎉",
            "You will receive an unexpected but exciting coding challenge. 🚀",
            "Someone will compliment your Git commit messages. 📝"
        ]
        for fortune in sample_fortunes:
            result = rand_date_time(fortune)
            assert fortune in result, f"Expected '{fortune}' in result, but got: {result}"