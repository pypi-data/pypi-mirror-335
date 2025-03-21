import pytest
from src.magic8ballfortunes.fortunes import Magic8Ball


class TestMagic8Ball:
    """Test suite for Magic8Ball's tell_fortune function."""

    def test_tell_fortune_returns_valid_fortune(self):
        """Test that tell_fortune returns a valid general fortune."""
        general_fortunes = Magic8Ball.DATA["general"]
        # Run the test multiple times to account for randomness.
        for _ in range(10):
            fortune = Magic8Ball.tell_fortune()
            assert fortune in general_fortunes

    def test_tell_fortune_with_monkeypatch(self, monkeypatch):
        """Test that tell_fortune returns the expected fortune when random.choice is monkeypatched."""
        fixed_fortune = "You will find unexpected joy today."
        # Import the random module used in the module so we can patch its choice method.
        import random

        monkeypatch.setattr(random, "choice", lambda x: fixed_fortune)
        fortune = Magic8Ball.tell_fortune()
        assert fortune == fixed_fortune

    """Test suite for Magic8Ball's category function."""

    # Test suite for Magic8Ball's category function.

    @pytest.mark.parametrize("category", ["love", "career", "health"])
    def test_valid_category(self, category):
        """Test that a valid category returns a fortune from the correct list."""
        fortune = Magic8Ball.fortune_by_category(category)
        assert fortune in Magic8Ball.DATA["categories"][category]

    @pytest.mark.parametrize(
        "category, expected_key",
        [
            ("lOvE", "love"),
            ("cAReer", "career"),
            ("HeaLTH", "health"),
        ],
    )
    def test_case_insensitivity(self, category, expected_key):
        """Test that the function handles different cases correctly."""
        fortune = Magic8Ball.fortune_by_category(category)
        assert fortune in Magic8Ball.DATA["categories"][expected_key]

    @pytest.mark.parametrize("invalid_category", ["cHase", "apple", "1234", ""])
    def test_invalid_category(self, invalid_category):
        """Test that an invalid category raises a ValueError."""
        with pytest.raises(
            ValueError, match=r"Invalid Category: Please enter a valid category \('love', 'career', 'health'\)"
        ):
            Magic8Ball.fortune_by_category(invalid_category)

    @pytest.mark.parametrize("non_string_input", [123, None, 5.5, ["love"], {"category": "love"}])
    def test_non_string_input(self, non_string_input):
        """Test that non-string inputs raise a TypeError."""
        with pytest.raises(TypeError, match="Invalid input: The category must be a string."):
            Magic8Ball.fortune_by_category(non_string_input)

    # Test suite for Magic8Ball's daily_by_birth_month function.

    @pytest.mark.parametrize("month", ["January", "February", "March"])
    def test_valid_month(self, month):
        """Test that a valid month returns a message from the correct list."""
        assert Magic8Ball.daily_by_birth_month(month) in Magic8Ball.DATA["birthdays"][month]

    @pytest.mark.parametrize(
        "month, expected",
        [
            ("january", "January"),
            ("FEBRUARY", "February"),
            ("MarCh", "March"),
        ],
    )
    def test_case_insensitivity(self, month, expected):
        """Test that the function handles different cases correctly."""
        assert Magic8Ball.daily_by_birth_month(month) in Magic8Ball.DATA["birthdays"][expected]

    @pytest.mark.parametrize("invalid_month", ["NotAMonth", "Octember", "1234", ""])
    def test_invalid_month(self, invalid_month):
        """Test that an invalid month raises a ValueError."""
        with pytest.raises(ValueError, match="Invalid month: Please enter a valid month name"):
            Magic8Ball.daily_by_birth_month(invalid_month)

    @pytest.mark.parametrize("invalid_input", [123, None, ["January"], {"month": "January"}])
    def test_non_string_input(self, invalid_input):
        """Test that non-string inputs raise a TypeError."""
        with pytest.raises(TypeError, match="Invalid input: The month must be provided as a string."):
            Magic8Ball.daily_by_birth_month(invalid_input)

    def test_random_fortune_selection(self):
        """Test that the function always returns a valid fortune from the respective month."""
        month = "January"
        for _ in range(10):  # Run multiple times to verify randomness
            assert Magic8Ball.daily_by_birth_month(month) in Magic8Ball.DATA["birthdays"][month]

            
    """Tests for the fortune_by_personality method."""

    @pytest.mark.parametrize("valid_personality", ["anxious", "kind", "rude"])
    def test_valid_personality(self, valid_personality):
        """
        Test that a valid personality type returns a fortune
        from the correct list in DATA["personalities"].
        """
        fortune = Magic8Ball.fortune_by_personality(valid_personality)
        # Ensure the returned fortune is one of the possible lines for that personality
        assert fortune in Magic8Ball.DATA["personalities"][valid_personality]

    @pytest.mark.parametrize(
        "input_val, expected_key",
        [
            ("Anxious", "anxious"),
            ("KIND", "kind"),
            ("RuDe", "rude"),
        ],
    )
    def test_case_insensitivity(self, input_val, expected_key):
        """
        Test that the function is case-insensitive and returns a fortune
        from the correct sub-dictionary in DATA["personalities"].
        """
        fortune = Magic8Ball.fortune_by_personality(input_val)
        assert fortune in Magic8Ball.DATA["personalities"][expected_key]

    @pytest.mark.parametrize("invalid_personality", ["", "123", "joyful", "RUDEE", "Kindness"])
    def test_invalid_personality(self, invalid_personality):
        """
        Test that providing an unrecognized personality raises a ValueError.
        """
        with pytest.raises(ValueError, match="Invalid Personality Type"):
            Magic8Ball.fortune_by_personality(invalid_personality)

    @pytest.mark.parametrize("non_string_input", [123, 3.14, None, ["kind"], {"personality": "rude"}])
    def test_non_string_input(self, non_string_input):
        """
        Test that providing a non-string raises a TypeError.
        """
        with pytest.raises(TypeError, match="Invalid input: The personality type must be a string."):
            Magic8Ball.fortune_by_personality(non_string_input)

    def test_fortune_by_personality_monkeypatch(self, monkeypatch):
        """
        Test that the function calls random.choice by monkeypatching
        it to return a known string.
        """
        fixed_fortune = "A special fortune just for you."
        import random

        monkeypatch.setattr(random, "choice", lambda x: fixed_fortune)

        fortune = Magic8Ball.fortune_by_personality("anxious")
        assert fortune == fixed_fortune