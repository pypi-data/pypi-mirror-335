![Workflow](https://github.com/software-students-spring2025/3-python-package-p3-py/actions/workflows/python-package.yml/badge.svg)
# Python Package Exercise
# debugBuddy

## Description
debugBuddy is your emotional support companion when debugging code. We all know debugging can be frustrating, demoralizing, and sometimes downright infuriating. debugBuddy is designed to make those moments a little more bearable by providing:

* Motivational messages when you feel like giving up
* Practical debugging tips tailored to your experience level and problem type
* A rubber duck debugging experience that talks back
* Comforting responses to scary error messages

Unlike traditional debugging tools that focus solely on fixing technical issues, debugBuddy addresses the emotional and psychological aspects of debugging, helping you maintain sanity and motivation throughout the process.

## PyPI Link
[debugBuddy on PyPl]()

## Team
* [Jake Chang](https://github.com/jakechang1284)
* [Samir Hussain](https://github.com/Samir2324)
* [Jimena Menendez](https://github.com/jkm8294)
* [Sarah Wang](https://github.com/sarahswang)

## How to Install and use this Package
1. Install pipenv (if not already installed):
```bash 
pip install pipenv
``` 
2. Install the Package: 
```bash
pip install debugBuddy
```
3. Activate the Virtual Environment: 
```bash 
pipenv shell
```
4. Create a Python program file to import and use the package:
```python
import debugBuddy.debug as debug
```
5. Run the Program:
```bash
python your_program_name.py
```
6. Exit the virtual environment: 
```bash 
Exit
```

## Functions
### Function 1
#### motivate(name)
* Provides a random motivational message to keep you going through difficult debugging sessions.

#### Parameters:
* name (str): Your name, which will be included in the personalized message

#### Returns:
* A string containing a randomly selected motivational message

```python
import debugBuddy.debug as debug

# get a motivational message
message = debug.motivate("Alex")
print(message)
# output might be: "Your code might be broken, Alex, but you're not! Keep going!"
```

### Function 2
#### ask_for_input(question, style="encouraging")
* Simulates a rubber duck debugging conversation, responding to your questions in different conversational styles.

#### Parameters:

* question (str): Your debugging question or issue

* style (str, optional): The response style. 
* Options:
* "encouraging": Positive and supportive responses
* "sarcastic": Humorous, sarcastic responses
* "philosophical": Deep, philosophical perspectives on debugging
* Default is "encouraging"

#### Returns:
* A string containing a response to your question in the specified style

#### Raises:
* ValueError: If an invalid style is provided

```python
import debugBuddy.debug as debug

# get an encouraging response
response = debug.ask_for_input("Why isn't my loop breaking?")
print(response)
# output might be: "You're close! Walk through your logic. Where does it start behaving unexpectedly?"

# get a sarcastic response
sarcastic = debug.ask_for_input("Why isn't my loop breaking?", "sarcastic")
print(sarcastic)
# output might be: "Maybe your loop just really likes running. Have you checked the condition?"

# get a philosophical response
philosophical = debug.ask_for_input("Why isn't my loop breaking?", "philosophical")
print(philosophical)
# output might be: "Maybe the loop is working as expected, and it's your expectations that are wrong."
```

### Function 3
#### debug_hint(issue_type="general", experience_level="intermediate")
* Provides specific debugging tips and strategies based on the type of issue you're facing and your experience level.

#### Parameters:
issue_type (str, optional): Type of debugging issue you're facing. 
* Options:
* "general": General debugging advice
* "syntax": Help with syntax errors
* "logic": Help with logical errors
* "runtime": Help with runtime errors
* "performance": Help with performance issues
* Default is "general"

* experience_level (str, optional): Your programming experience level. 
* Options:
* "beginner": For new programmers
* "intermediate": For programmers with some experience
* "advanced": For experienced programmers
* Default is "intermediate"

#### Returns:
* A string containing a debugging tip relevant to the specified issue type and experience level

#### Raises:
* ValueError: If an invalid issue_type or experience_level is provided

```python
import debugBuddy.debug as debug

# get a general debugging hint for intermediate programmers
hint = debug.debug_hint()
print(hint)
# output might be: "Try commenting out sections of code to isolate the issue"

# get a syntax debugging hint for beginners
beginner_hint = debug.debug_hint("syntax", "beginner")
print(beginner_hint)
# output might be: "Check for missing colons at the end of if, for, while, def statements"

# get a performance debugging hint for advanced programmers
advanced_hint = debug.debug_hint("performance", "advanced")
print(advanced_hint)
# output might be: "Profile your code to identify bottlenecks"
```

### Function 4
#### error_message_help(error = 'TypeError')
* Provides tips or suggestions based on the specific error type you are dealing with.

#### Parameter:
error (str, optional): Error you are facing
* Options:
* 'FileNotFoundError'
* 'ImportError'
* 'IndentationError'
* 'ValueError'
* 'AttributeError'
* 'KeyError'
* 'IndexError'
* 'NameError'
* 'SyntaxError'
* 'TypeError': default

### Returns:
* A string containing a suggestion on how to resolve the specific error

### Raises:
* ValueError: If an invalid error is passed in

```python
import debugBuddy.debug as debug

# get a hint for Type Errors
type_hint = debug.error_message_help()
print(type_hint)
# output may be: You're so close! Try using int(), str(), or float() to match the data types!

# get a hint for Syntax Errors
syntax_hint = debug.error_message_help('SyntaxError')
print(syntax_hint)
# output may be: You're almost there! A missing colon, parenthesis, or quote might be the issue.

# get a hint for Value Errors
value_hint = debug.error_message_help('ValueError')
print(value_hint)
# output may be: Great work! Just check if the value is within the expected range before using it.
```
An exercise to create a Python package, build it, test it, distribute it, and use it. See [instructions](./instructions.md) for details.

## Contributions
If you would like to contribute to this package, please follow the steps below.
#### Clone the repository
``` bash
git clone https://github.com/software-students-spring2025/3-python-package-p3-py.git
cd 3-python-package-p3-py
```
#### Create a new branch
``` bash
git checkout -b <branch-name>
```
#### How to Run Unit Tests
We've included at least 4 unit tests for each function in the debugBuddy package. To run these tests: 
1. Install pytest in the virtual environment:
```bash 
pipenv install pytest
```
2. Naviagate to the main project directory: 
```bash 
cd path/to/your/project
```
3. Run Pytest for all tests 
```bash 
pytest test_debugBuddy.py
```
4. (Optional) Run all tests with detailed output: 
```bash 
pytest -v test_debugBuddy.py
```
5. (Optional)If you want to run a single test inside test_debugBuddy.py, for example, test_ask_for_input_encouraging, use: 
```bash 
pytest test_debugBuddy.py -k "test_ask_for_input_encouraging"
```

## Command Line 
You can also use debugBuddy on the command line if you want to quickly use the functions for debugging help. Example, to use the motivate function you can call the following which will print out a motivational message with the name inputed. 
```bash 
debugBuddy motivate name 
#Output may be: One bug at a time, name
```
Another example is to use the error message function you can similarly type in the command line:
```bash 
debugBuddy error_message_help FileNotFoundError
#Output may be: No worries! Double-check the file path and ensure it exists—it’s an easy fix!
```
