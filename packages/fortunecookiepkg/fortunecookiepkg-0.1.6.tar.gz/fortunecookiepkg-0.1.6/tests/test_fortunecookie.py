import datetime
from unittest.mock import patch
import pytest
import random

from fortunecookiepkg.fortunecookie import (
    FORTUNES,
    get_random_fortune,
    get_lucky_numbers,
    get_daily_fortune,
    get_custom_fortune,
    get_themed_fortune,
)

class Tests:
    #Fixtures
    @pytest.fixture
    def example_fixture(self):
        """
        An example fixture used for setup/teardown before/after tests are run.
        """
        yield

    #Test functions
    def test_sanity_check(self, example_fixture):
        """
        Test debugging is working with a simple check.
        """
        expected = True
        actual = True
        assert actual==expected, "Expected True to equal True."
        
    #Random fortune tests
    def test_get_random_fortune_randomness(self):
        """
        Given multiple calls, two outputs should not always be the same, ensuring randomness. 
        """
        res1 = get_random_fortune()
        res2 = get_random_fortune()
        assert res1 != res2, f"Expected get_random_fortune() to return 2 different fortunes, but got identical results: '{res1}'."

    #Lucky number tests
    def test_get_lucky_numbers_length_valid(self):
        """
        If the input is valid, the array should be the same length as the given input"
        """
        valid_len = random.randint(1, 10)
        res = get_lucky_numbers(valid_len)
        assert len(res) == valid_len, f"Expected get_lucky_numbers() to return {valid_len} numbers. Instead, it returned an array with {len(res)} numbers"

    def test_get_lucky_numbers_length_invalid(self):
        """
        If there is invalid input, the array should have length of 0.
        """
        invalid_len = random.randint(11, 100)
        res = get_lucky_numbers(invalid_len)
        assert res == 0, f"Expected get_lucky_numbers() to return 0 numbers. Instead, it returned an array with {len(res)} numbers"  

    def test_get_lucky_numbers_randomness(self):
        """
        Given the same length, two outputs should not be the same which ensures randomness.
        """
        valid_len = random.randint(1, 10)
        res1 = get_lucky_numbers(valid_len)
        res2 = get_lucky_numbers(valid_len)
        assert res1 != res2, f"Expected get_lucky_numbers() to return 2 different arrays, given the same length. Instead, it returned two arrays with identical values"

    #Custom fortune tests
    def test_get_custom_fortune_name(self):
        """
        Output should include the given name.
        """
        name = "Sam"
        res = get_custom_fortune(name)
        assert name in res, f"Expected '{name}' in the output but got '{res}'"
   
    def test_get_custom_fortune_empty_name(self):
        """
        If the name is empty, the function should still return a valid fortune.
        """
        res = get_custom_fortune("")
        assert isinstance(res, str), "Expected output to be a string"
        assert res.strip() != "", "Expected a non-empty fortune, but got an empty string"
   
    def test_get_custom_fortune_long_name(self):
        """
        If system has length limits or unexpected behavior with long strings, function should still work.
        """

        name = "A" * 100
        res = get_custom_fortune(name)
        assert name in res, f"Expected the long name in the output but got '{res}'"
    
    def test_get_custom_fortune_special_chars(self):
        """
        Function should corrrectly handle names with special characters in them.
        """
        name = "@l!c3_42"
        res = get_custom_fortune(name)
        assert name in res, f"Expected '{name}' in the output but got '{res}'"
    
    #Themed fortune tests
    def test_get_themed_fortune_invalid_theme(self):
        """ 
        Provided theme should be valid.
        """
        res = get_themed_fortune("unknown")
        assert "There are no fortunes for your provided theme" in res, f"Expected an error message but got '{res}'"

    def test_get_themed_fortune_empty(self):
        """
        If an empty string is given as a theme, it should return an error message.
        """
        res = get_themed_fortune("")
        assert "There are no fortunes for your provided theme" in res, f"Expected an error message but got '{res}'"

    @pytest.mark.parametrize("theme", [" love ", "  career  ", " happiness "])
    def test_get_themed_fortune_spaces(self, theme):
        """
        If there are spaces, hand the extra spaces. 
        """
        res = get_themed_fortune(theme.strip())
        assert isinstance(res, str), "Expected output to be a string"
        assert len(res) > 0, f"Expected a non-empty fortune but got '{res}'"

    #Daily fortune tests
    def test_get_daily_fortune_exists(self):
        """
        Tests that the fortune for a given day exists in the FORTUNES array.
        """
        fortune = get_daily_fortune('wednesday')
        assert fortune in FORTUNES

    def test_get_daily_fortune_is_accurate(self):
        """
        Tests that the fortune for a given day of the week remains consistent given different cases.
        """
        fortune1 = get_daily_fortune('monday')
        fortune2 = get_daily_fortune('Monday')
        assert (fortune1 == fortune2)

    def test_get_daily_fortune_returns_string(self):
        """
        Tests that the daily fortune function returns a non-empty string, given a valid day of the week.
        """
        fortune = get_daily_fortune('tuesday')
        assert len(fortune) != 0, f"Expected get_daily_fortune() to return a non-empty string of length > 0. Instead, it returned a string with length {len(fortune)}"

    def test_get_daily_fortune_returns_string(self):
        """    
        Tests that the daily fortune function returns an empty string, given an invalid day of the week
        """
        fortune = get_daily_fortune('invalid_day')
        assert len(fortune) == 0, f"Expected get_daily_fortune() to return string of length 0. Instead, it returned a string with length {len(fortune)}"
    
    @pytest.mark.parametrize("invalid_day", [None, 123, [], {}, set(), 5.6])
    def test_get_daily_fortune_invalid_types(self, invalid_day):
        """
        Ensure the funciton can handle invalid data types.
        """
        fortune = get_daily_fortune(invalid_day)
        assert len(fortune) == 0, f"Expected empty string for invalid input but got '{fortune}'"
  
    @pytest.mark.parametrize("day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    def test_get_daily_fortune_valid_days(self, day):
        """
        Ensure function returns a valid fortune for all days of the week
        """
        fortune = get_daily_fortune(day)
        assert isinstance(fortune, str) and len(fortune) > 0, f"Expected a valid fortune but got '{fortune}'"