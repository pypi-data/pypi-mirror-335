import sys
from debugBuddy import motivate, error_message_help, ask_for_input, debug_hint

def motivate_cli():
    if len(sys.argv) < 2:
        print("Usage: motivate <name>")
        sys.exit(1)
    
    name = " ".join(sys.argv[1:])
    print(motivate(name))

def error_message_help_cli():
    if len(sys.argv) == 1:
        #default input
        try:
            print(error_message_help())
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif len(sys.argv) == 2:
        #given argument
        try:
            print(error_message_help(sys.argv[1]))
        except ValueError as e:
            print(f"Error: {e}")
            print("Valid errors are: FileNotFoundError, ImportError, IndentationError, ValueError, AttributeError, KeyError, IndexError, TypeError, NameError, SyntaxError")
            sys.exit(1)
    else:
        print("Syntax: error_message_help <ErrorType>")
        print("Valid errors are: FileNotFoundError, ImportError, IndentationError, ValueError, AttributeError, KeyError, IndexError, TypeError, NameError, SyntaxError")
        sys.exit(1)

def ask_for_input_cli(): #jime
    if len(sys.argv) < 3:  #question and style exist 
        print("Usage: ask_for_input <question> <style>")
        print("Styles: encouraging, sarcastic, philosophical")
        sys.exit(1)
    question = " ".join(sys.argv[1:-1]).strip()  # everything - style so question
    style = sys.argv[-1].lower().strip()# last thing is the style
    if not question:  #question exists
        print("Error: Question cannot be empty.")
        sys.exit(1)
    try:
        print(ask_for_input(question, style))
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
        
def debug_hint_cli(): #jake
    # check if arguments are provided correctly
    if len(sys.argv) == 1:
        # no arguments provided, use defaults
        try:
            print(debug_hint())
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
    elif len(sys.argv) == 2:
        # only issue_type provided
        issue_type = sys.argv[1].lower().strip()
        try:
            print(debug_hint(issue_type=issue_type))
        except ValueError as e:
            print(f"Error: {e}")
            print("Valid issue types: general, syntax, logic, runtime, performance")
            sys.exit(1)
    elif len(sys.argv) == 3:
        # both issue_type and experience_level provided
        issue_type = sys.argv[1].lower().strip()
        experience_level = sys.argv[2].lower().strip()
        try:
            print(debug_hint(issue_type=issue_type, experience_level=experience_level))
        except ValueError as e:
            print(f"Error: {e}")
            print("Valid issue types: general, syntax, logic, runtime, performance")
            print("Valid experience levels: beginner, intermediate, advanced")
            sys.exit(1)
    else:
        # too many arguments
        print("Usage: debug_hint [issue_type] [experience_level]")
        print("Valid issue types: general, syntax, logic, runtime, performance")
        print("Valid experience levels: beginner, intermediate, advanced")
        sys.exit(1)