#File for all of our methods
# Sarah
import random

def motivate(name):

    messages = [

        f"Hang in there, {name}!",
        f"Don't give up, {name}!",
        f"Almost there, {name}!",
        f"You're one function away from being done, {name}!",
        f"Think about how satisfied you'll feel when you're done, {name}!",
        f"One bug at a time, {name}!",
        f"Your code might be broken, {name}, but you're not! Keep going!",

    ]

    return random.choice(messages)


#Jimena's Rubber Ducky Method 
def ask_for_input(question, style="encouraging"):
    #question is a string
        #diff styles 
        #encouraging
        #sarcastic
        #philosophical

    encouragingResponses = [
        "Let's break this down step by step. Make sure to check all areas of your code.",
        "You're close! Walk through your logic. Where does it start behaving unexpectedly?",
        "Think about the inputs. Could any unexpected values be sneaking in?",
        "You got it, just try again!",
        "If you had to explain this to a complete beginner, how would you phrase it?",
    ]

    sarcasticResponses = [
        "Maybe your loop just really likes running. Have you checked the condition?",
        "Oh, your code works perfectly—just not in this universe...",
        "Did you remember to tell your loop it’s allowed to stop?",
        "Ah yes, the classic 'works in my head' bug. Try printing some values!",
        "Have you tried learning how to code."
    ]

    philosophicalResponses = [
        "Does a loop truly end, or does it just move on to a different state of being?",
        "If a function runs in a program and no one is around to call it, does it even exist?",
        "If you don't re-start the program, did it ever stop to begin with? ",
        "Maybe the loop is working as expected, and it's your expectations that are wrong.",
        "If an exception is raised in a forest of print statements, can it still be caught?",
        "Are your variable names formatted correctly for what is even in a name?"
    ]

    responseOptions = {
        "encouraging": encouragingResponses,
        "sarcastic": sarcasticResponses,
        "philosophical": philosophicalResponses
    }

    if style not in responseOptions:
        raise ValueError(f"Invalid style '{style}'. Choose from 'encouraging', 'sarcastic', or 'philosophical'.")

    return random.choice(responseOptions[style])

# Example question -> print(ask_for_input("Why isn't my loop breaking?", "sarcastic"))

# jake's debug hint method
def debug_hint(issue_type="general", experience_level="intermediate"):
    
    # valid parameter inputs if different from default
    valid_issue_types = ["general", "syntax", "logic", "runtime", "performance"]
    valid_experience_levels = ["beginner", "intermediate", "advanced"]
    
    if issue_type not in valid_issue_types:
        raise ValueError(f"Invalid issue_type '{issue_type}'. Choose from {valid_issue_types}")
    if experience_level not in valid_experience_levels:
        raise ValueError(f"Invalid experience_level '{experience_level}'. Choose from {valid_experience_levels}")
    
    # dictionary of hints based on issue and experience
    hints = {
        "general": {
            "beginner": [
                "Print variables to see their current values throughout your code",
                "Take a break and come back with fresh eyes",
                "Read your code line by line, like you're explaining it to someone else",
                "Check your indentation and make sure your code blocks are properly structured",
                "Try running a simpler version of your code to isolate the problem"
            ],
            "intermediate": [
                "Use logging instead of print statements for better debugging output",
                "Try commenting out sections of code to isolate the issue",
                "Check for edge cases in your input data",
                "Review your algorithm's logic step by step",
                "Consider using a debugger to step through your code execution"
            ],
            "advanced": [
                "Use profiling tools to identify bottlenecks",
                "Consider writing unit tests to verify components individually",
                "Check for race conditions or concurrency issues",
                "Look for memory leaks or improper resource management",
                "Review your design patterns and architectural choices"
            ]
        },
        "syntax": {
            "beginner": [
                "Check for missing colons at the end of if, for, while, def statements",
                "Make sure you're using the correct indentation",
                "Verify all parentheses, brackets, and curly braces are properly closed",
                "Watch for typos in variable and function names",
                "Check if you're using assignment (=) when you meant comparison (==)"
            ],
            "intermediate": [
                "Look for incorrect use of comprehensions or generator expressions",
                "Check for misuse of lambda functions or decorators",
                "Verify correct use of string formatting methods",
                "Check for proper exception handling syntax",
                "Look for incorrect function parameter definitions"
            ],
            "advanced": [
                "Verify correct usage of metaprogramming constructs",
                "Check for subtle issues with operator overloading",
                "Verify correct use of context managers and the with statement",
                "Look for incorrect async/await syntax",
                "Check for proper type hints and annotations"
            ]
        },
        "logic": {
            "beginner": [
                "Check your loop conditions - are they terminating correctly?",
                "Verify if conditions are doing what you expect",
                "Check that variables are being updated as expected",
                "Ensure your function is returning the correct value",
                "Verify the order of operations in complex expressions"
            ],
            "intermediate": [
                "Look for off-by-one errors in indexing or ranges",
                "Check for edge cases in your algorithm",
                "Verify the correctness of recursive function base cases",
                "Ensure proper handling of null/None values",
                "Validate assumptions about data formats and structures"
            ],
            "advanced": [
                "Check for subtle issues in complex algorithms",
                "Verify thread-safety in concurrent code",
                "Look for unintended side effects in function calls",
                "Check boundary conditions in mathematical operations",
                "Verify correctness of optimization strategies"
            ]
        },
        "runtime": {
            "beginner": [
                "Check if you're accessing a list index that doesn't exist",
                "Make sure you're not dividing by zero",
                "Verify that variables are defined before they're used",
                "Check if you're using the correct data types for operations",
                "Make sure files are open before reading/writing and closed after"
            ],
            "intermediate": [
                "Check for proper exception handling around potentially failing operations",
                "Verify resource cleanup in all execution paths",
                "Look for potential infinite recursion cases",
                "Check for correct API usage in external library calls",
                "Verify timeout handling for network operations"
            ],
            "advanced": [
                "Look for race conditions in concurrent code",
                "Check for deadlocks or livelocks in multi-threaded applications",
                "Verify proper handling of system resource limits",
                "Look for memory leaks in long-running processes",
                "Check for proper error propagation in complex call stacks"
            ]
        },
        "performance": {
            "beginner": [
                "Avoid unnecessary calculations inside loops",
                "Use appropriate data structures for your operations",
                "Limit the use of global variables",
                "Check if you're creating large temporary objects unnecessarily",
                "Consider using better algorithms for sorting or searching"
            ],
            "intermediate": [
                "Use list/dict/set comprehensions instead of loops where appropriate",
                "Consider using generator expressions for large data sets",
                "Look for redundant database queries or API calls",
                "Check if you can use caching for expensive operations",
                "Consider using more efficient libraries for performance-critical code"
            ],
            "advanced": [
                "Profile your code to identify bottlenecks",
                "Consider parallelizing CPU-intensive operations",
                "Look for opportunities to use vectorized operations",
                "Optimize database queries with proper indexing",
                "Consider memory-time tradeoffs in your algorithm design"
            ]
        }
    }
    # return a random hint from the dict
    return random.choice(hints[issue_type][experience_level])


#Samir's method
def error_message_help(error = 'TypeError'):

    valid_errors = ['FileNotFoundError', 'ImportError', 'IndentationError', 'ValueError', 'AttributeError', 
                    'KeyError', 'IndexError', 'TypeError', 'NameError', 'SyntaxError']
    
    

    if error not in valid_errors:
        temp = error.replace("_"," ").title().split()
        formatted_error = "".join(temp)#support for cases: value error, value_error
        if formatted_error not in valid_errors:#if format is different
            raise ValueError(f"This error is not supported, please choose from this list of errors: {valid_errors}")
        
    formatted_error = error
    #dict of supportive messages based on error type
    supportive_messages = {
    "FileNotFoundError": [
        "No worries! Double-check the file path and ensure it exists—it’s an easy fix!",
        "This happens to the best of us! Try using os.path.exists() to confirm the file’s location.",
        "Maybe the file was moved? A quick search or using an absolute path can help!",
        "Check for typos in the filename or directory—Python is very picky about paths!",
        "If the file should be created dynamically, consider using 'w' mode to create it when needed!"
        ],
    "ImportError": [
        "You’re close! Try pip install module_name or check the module’s correct import name.",
        "Sometimes, built-in modules don’t need installation—double-check Python’s docs!",
        "Try dir(module_name) to see what’s available—you might need a different function name.",
        "If it’s a local module, ensure it’s in the same directory or added to the Python path.",
        "Virtual environments can be tricky—activate the right one with source venv/bin/activate!"
        ],
    "IndentationError": [
        "Python loves consistency! Make sure your code is indented the same way (spaces vs. tabs).",
        "This is a quick fix! Many editors have an auto-indent feature—give it a try!",
        "Your logic is solid! Just align your indentation, and Python will understand it.",
        "Check nested blocks—sometimes an if, for, or def needs proper alignment.",
        "You're on the right path! A little adjustment will get your code running smoothly."
        ],
    "ValueError": [
        "Great work! Just check if the value is within the expected range before using it.",
        "Python is just ensuring everything makes sense—try validating inputs before passing them in!",
        "You’re almost there! Consider adding error handling like try-except to catch unexpected values.",
        "A quick print(type(your_value)) might help you understand why Python is complaining!",
        "You’ve got this! A small check with if statements or input validation will fix it in no time."
        ],
    "AttributeError": [
        "You're doing great! Just check if the object actually has the attribute you’re calling.",
        "No big deal! Use dir(object_name) to see what attributes are available.",
        "Maybe you need to initialize the object differently? Double-check its type!",
        "If you're working with a library, check the docs—sometimes methods change between versions!",
        "Python is just making sure you’re using the right method—look out for small typos or missing imports!"
        ],
    "KeyError": [
        "You’re close! Use dict.get(key) to prevent errors when a key might be missing.",
        "Maybe a small typo? Double-check the key name—it’s case-sensitive!",
        "Try printing dict.keys() to see what’s available—it might help you debug!",
        "If the key should always exist, ensure it's added before accessing it.",
        "Adding error handling with if key in dict can make your code more robust!"
        ],
    "IndexError": [
        "You’re almost there! Check len(your_list) before accessing an index.",
        "Python just wants to keep things safe—make sure your index is within range!",
        "Try using negative indexing (-1 for the last element) to stay within bounds!",
        "Lists start at index 0, so double-check that you’re not off by one.",
        "If your list length changes dynamically, handle it with try-except or a loop!"
        ],
    "TypeError": [
        "You're so close! Try using int(), str(), or float() to match the data types!",
        "Python just needs a little help—check which type each value is before performing operations.",
        "Maybe you meant to concatenate strings instead of adding numbers? A quick str(value) can help!",
        "A function might be returning an unexpected type—print it out to debug!",
        "This is an easy fix! Just check your variable types using type(variable) before using them."
        ],
    "NameError": [
        "Almost there! Make sure the variable is declared before you use it.",
        "A simple typo might be the culprit—double-check the spelling!",
        "If you're inside a function, the variable might need to be passed as an argument.",
        "Try print(globals()) or print(locals()) to check what’s actually available.",
        "This happens to everyone! A quick if 'var' in locals(): can help prevent it!"
        ],
    "SyntaxError": [
        "You're almost there! A missing colon, parenthesis, or quote might be the issue.",
        "Python is just making sure everything is structured properly—double-check line breaks!",
        "Try reformatting your code—sometimes an extra space or missing keyword can cause this.",
        "Syntax errors are normal! Carefully reading the error message will help you pinpoint the problem.",
        "Python’s syntax rules are strict, but once you find the small mistake, it’ll work perfectly!"
        ]
    }

    #returning a random message based on 
    return random.choice(supportive_messages[formatted_error])
