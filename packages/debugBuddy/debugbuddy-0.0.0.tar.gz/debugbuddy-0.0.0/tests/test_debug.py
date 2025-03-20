import pytest 
from debugBuddy import debug

class Tests:
    #Test functions
    
    # jake test units
    def test_debug_hint_default_parameters(self):
        result = debug.debug_hint()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_debug_hint_specific_parameters(self):
        result = debug.debug_hint("syntax", "beginner")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_debug_hint_all_combinations(self):
        issue_types = ["general", "syntax", "logic", "runtime", "performance"]
        experience_levels = ["beginner", "intermediate", "advanced"]
        for issue_type in issue_types:
            for level in experience_levels:
                result = debug.debug_hint(issue_type, level)
                assert isinstance(result, str)
                assert len(result) > 0
                
    def test_debug_hint_invalid_issue_type(self):
        with pytest.raises(ValueError):
            debug.debug_hint("nonexistent_issue_type")

    def test_debug_hint_invalid_experience_level(self):
        with pytest.raises(ValueError):
            debug.debug_hint("general", "nonexistent_level")
            
    
    #Samir unit tests
    def test_error_message_help_invalid_parameter(self):
        with pytest.raises(ValueError):
            debug.error_message_help("NoError")

    def test_error_message_help_valid_parameter(self):
        ret = debug.error_message_help("ValueError")
        assert isinstance(ret,str)
        assert len(ret) > 0

    def test_error_message_help_default_parameter(self):
        ret = debug.error_message_help()
        assert isinstance(ret,str)
        assert len(ret) > 0

    def test_error_message_help_all_parameters(self):
        errors = ['FileNotFoundError', 'ImportError', 'IndentationError', 'ValueError', 'AttributeError', 
                    'KeyError', 'IndexError', 'TypeError', 'NameError', 'SyntaxError']
        for error in errors:
            ret = debug.error_message_help(error)
            assert isinstance(ret,str)
            assert len(ret) > 0
    
    #Jimenas test units
    #should i make my tests simpler?? 
    def test_ask_for_input_encouraging(self):
        result = debug.ask_for_input("Why isn't my loop breaking?", "encouraging")
        assert isinstance(result, str)
        assert len(result) > 0
        assert result in [
            "Let's break this down step by step. Make sure to check all areas of your code.",
            "You're close! Walk through your logic. Where does it start behaving unexpectedly?",
            "Think about the inputs. Could any unexpected values be sneaking in?",
            "You got it, just try again!",
            "If you had to explain this to a complete beginner, how would you phrase it?",
        ]

    def test_ask_for_input_sarcastic(self):
        result = debug.ask_for_input("Why isn't my loop breaking?", "sarcastic")
        assert isinstance(result, str)
        assert len(result) > 0
        assert result in [
            "Maybe your loop just really likes running. Have you checked the condition?",
            "Oh, your code works perfectly—just not in this universe...",
            "Did you remember to tell your loop it’s allowed to stop?",
            "Ah yes, the classic 'works in my head' bug. Try printing some values!",
            "Have you tried learning how to code."
        ]

    def test_ask_for_input_philosophical(self):
        result = debug.ask_for_input("Why isn't my loop breaking?", "philosophical")
        assert isinstance(result, str)
        assert len(result) > 0
        assert result in [
            "Does a loop truly end, or does it just move on to a different state of being?",
            "If a function runs in a program and no one is around to call it, does it even exist?",
            "If you don't re-start the program, did it ever stop to begin with? ",
            "Maybe the loop is working as expected, and it's your expectations that are wrong.",
            "If an exception is raised in a forest of print statements, can it still be caught?",
            "Are your variable names formatted correctly for what is even in a name?"
        ]

    def test_ask_for_input_invalid_style(self):
        with pytest.raises(ValueError):
            debug.ask_for_input("Why isn't my loop breaking?", "aggressive")

    def test_ask_for_input_empty_question(self):
        result = debug.ask_for_input("", "encouraging")
        assert isinstance(result, str)
        assert len(result) > 0  # Ensures function still returns a response

    def test_ask_for_input_default_style(self):
        result = debug.ask_for_input("Why isn't my loop breaking?")
        assert isinstance(result, str)
        assert len(result) > 0
        assert result in [
            "Let's break this down step by step. Make sure to check all areas of your code.",
            "You're close! Walk through your logic. Where does it start behaving unexpectedly?",
            "Think about the inputs. Could any unexpected values be sneaking in?",
            "You got it, just try again!",
            "If you had to explain this to a complete beginner, how would you phrase it?",
        ]

    # Sarah's tests for motivate(name)

    def test_motivate_returns_string(self):
        result = debug.motivate("Alice")
        assert isinstance(result, str)

    def test_motivate_contains_name(self):
        name = "Charlie"
        result = debug.motivate(name)
        assert name in result

    def test_motivate_handles_weird_names(self):
        weird_names = ["X Æ A-12", "Von Halle", "O'Reilly", " "]
        for weird_name in weird_names:
            result = debug.motivate(weird_name)
            assert weird_name in result

    def test_motivate_randomness(self):
        name = "Sarah"
        results = {debug.motivate(name) for _ in range(10)}
        assert len(results) > 1