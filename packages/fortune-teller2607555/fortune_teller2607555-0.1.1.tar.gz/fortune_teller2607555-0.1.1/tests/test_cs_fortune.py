import pytest
from fortune_teller.cs_fortune import cs_fortune

class TestCsFortune:
    @pytest.mark.parametrize("category", ["tech", "startup", "open source", "ai", "career"])
    def test_returns_str(self, category):
        """
        Check if cs_fortune() returns a string for each valid category.
        """
        result = cs_fortune(category)
        assert isinstance(result, str), "Expected a string fortune."

    def test_randomness(self):
        """
        Check for randomness of the fortunes.
        (Not guaranteed 100% different every time, but likely over multiple attempts.)
        """
        results = {cs_fortune("tech") for _ in range(10)}
        assert len(results) > 1, "Expected random fortunes, but got the same one every time."

    def test_invalid_category_returns_error_string(self):
        """
        If given an invalid category, cs_fortune function should return a string
        starting with 'Oops:' rather than raising ValueError.
        """
        invalid_category = "internships"
        result = cs_fortune(invalid_category)
        assert result.startswith("Oops:"), (
            f"For invalid category '{invalid_category}', expected the returned string "
            f"to start with 'Oops:', but got {result} instead."
        )

    @pytest.mark.parametrize("category, valid_fortunes", [
        ("tech", {
            "You will fix a bug... but create two new ones.",
            "Your commit messages will inspire thousands of developers.",
            "Your code will compile on the first try... eventually.",
            "Rubber duck debugging will save your day—just don't question the duck.",
            "A segfault in your future? Fear not, for logs will guide you.",
            "You will spend more time reading logs than writing code.",
            "Your local environment will perfectly mirror production… for exactly 30 seconds.",
            "You'll fix 30 lines of code and break 300 in the same commit.",
            "In the near future, you'll rediscover the infinite loop… but eventually you'll break free."
        }),
        ("startup", {
            "Your pitch deck will raise millions, as soon as you remove that one extra slide.",
            "A hidden co-founder is about to appear in your life.",
            "Your MVP will be hailed as the next big thing.",
            "Investors will love your product… right after they ask for 50 new features.",
            "Your next pivot will feel like a 180° turn, but it leads you straight to success.",
            "A late-night Slack thread will spark an idea that changes everything.",
            "Your biggest critic will become your most loyal brand ambassador.",
            "You'll wake up one day to realize: your side project is now your main hustle.",
            "A surprise endorsement will triple your user base overnight."
        }),
        ("open source", {
            "You will become a beloved maintainer of a widely used project.",
            "A community member's pull request will solve your trickiest issue.",
            "Your next contribution will inspire new developers to join open source.",
            "You'll discover that your community is an unstoppable force of bug-squashing heroes.",
            "Your next feature request will spark a worldwide collaboration, uniting devs in harmony.",
            "Your README will be hailed as the gold standard of open-source documentation.",
            "A fork of your project will evolve into something unexpectedly brilliant.",
            "One day, a grateful contributor will credit you for inspiring their own successful project.",
            "Your commit history will be studied as a shining example for new developers everywhere."
        }),
        ("ai", {
            "Your ML model will become self-aware… proceed with caution!",
            "AI is just a fancy name for code that doesn't work yet.",
            "Your next project: bridging the gap between humans and robots.",
            "Your chatbot will sound so human, you'll start asking it for life advice at 2 a.m.",
            "You will develop an AI that detects sarcasm—though it won't believe you.",
            "Your ML pipeline will gain sentience, then politely ask for a day off.",
            "You'll realize half your time is spent cleaning data, not training models.",
            "One day, your neural net will pass the Turing Test… until it encounters a CAPTCHA.",
            "Automating everything with AI will free up your time—just in time to debug the AI itself."
        }),
        ("career", {
            "You're on the path to landing your dream developer job!",
            "One day you'll write the code that changes the world.",
            "Your LinkedIn profile will attract a special opportunity.",
            "Your next promotion will arrive sooner than you think—keep building those skills.",
            "A hidden opportunity will reveal itself just when you need it most.",
            "You'll discover your dream role in the most unexpected place.",
            "Your debugging prowess will earn you a reputation as the office superhero.",
            "A recruiter will contact you about a role that seems impossible—until you make it possible.",
            "You'll mentor someone who ends up skyrocketing your own career in return."
        })
    ])
    def test_valid_category_fortunes(self, category, valid_fortunes):
        """
        For each valid category, checks that the returned fortune is in the complete set.
        """
        fortune_returned = cs_fortune(category)
        assert fortune_returned in valid_fortunes, (
            f"For category '{category}', the fortune '{fortune_returned}' is not recognized. "
            f"Expected one of: {valid_fortunes}"
        )
    

