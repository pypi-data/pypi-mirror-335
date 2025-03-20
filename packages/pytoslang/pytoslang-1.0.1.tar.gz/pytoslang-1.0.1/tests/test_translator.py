import pytest
from src.pytoslang.translations import full_to_slang, slang_to_emoji, slang_to_full, remove_slang

class Tests:
    @pytest.fixture
    def example_fixture(self):
        """
        An example of a pytest fixture - a function that can be used for setup and teardown before and after test functions are run.
        """

        # place any setup you want to do before any test function that uses this fixture is run

        yield  # at th=e yield point, the test function will run and do its business

        # place with any teardown you want to do after any test function that uses this fixture has completed

    #
    # Test functions
    #

    def test_sanity_check(self, example_fixture):
        """
        Test debugging... making sure that we can run a simple test that always passes.
        Note the use of the example_fixture in the parameter list - any setup and teardown in that fixture will be run before and after this test function executes
        From the main project directory, run the `python3 -m pytest` command to run all tests.
        """
        expected = True  # the value we expect to be present
        actual = True  # the value we see in reality
        assert actual == expected, "Expected True to be equal to True!"

    def test_full_to_slang(self):
        """
        Test basic slang conversion.
        """
        assert full_to_slang("I don't know") == "idk"
    
    def test_full_to_slang_case_sensitive(self):        
        """
        Check for different cases
        """
        assert full_to_slang("i DoN't kNoW") == "idk"
        
    def test_full_to_slang_no_slang(self):
        """
        If there is no slang in the sentence
        """
        assert full_to_slang("There is no slang") == "there is no slang"
    
    def test_full_mixed_with_slang(self):
        """
        sentences with both slang and regular text
        """
        assert full_to_slang("To be honest, I am tired") == "tbh, i am tired"

    def test_slang_to_emoji(self):
        """
        Test basic slang to emoji conversion.
        """
        assert slang_to_emoji("goat") == "🐐"
    
    def test_slang_to_emoji_case_sensitive(self):        
        """
        Check that input translates regardless of upper/lower case
        """
        assert slang_to_emoji("GOAT") == "🐐"
        
    def test_slang_to_emoji_no_emoji(self):
        """
        Check that no translations happen if there is no slang or slang not in translation list
        """
        assert slang_to_emoji("lmc") == "lmc"
    
    def test_slang_mixed_with_emoji(self):
        """
        Check that sentence can include both text and emoji conversions
        """
        assert slang_to_emoji("lmc brb goat") == "lmc 🔙 🐐"

    def test_slang_to_full(self):
        """
        Test basic conversion.
        """
        assert slang_to_full("nm") == "nothing much"
        assert slang_to_full("oh nm") == "oh nothing much"

    def test_slang_to_full_case_sensitive(self):        
        """
        Check for different cases
        """
        assert slang_to_full("fReN") == "friend"
        assert slang_to_full("I miss you fReN") == "i miss you friend"
        assert slang_to_full("I miss you FRen ") == "i miss you friend "

    
    def test_slang_mixed_with_full(self):
        """
        sentences with both slang and regular text
        """
        assert full_to_slang("To be honest, I am tired") == "tbh, i am tired"

    def test_remove_slang(self):
        """ test basic slang removal """
        assert remove_slang("Brb im going to get food") == "im going to get food"

    def test_remove_slang_case_sensitive(self):
        """ ensure function is case insensitive """
        assert remove_slang("BRB im GOING to get FOOD") == "im going to get food"

    def test_remove_slang_mixed_sentences(self):
        """ ensure function removes slang while keeping other words """
        assert remove_slang("Tbh this food is great") == "this food is great"

    def test_remove_slang_no_slang(self):
        """ ensure function does nothing if there is no slang """
        assert remove_slang("i love coding") == "i love coding"
    


    

