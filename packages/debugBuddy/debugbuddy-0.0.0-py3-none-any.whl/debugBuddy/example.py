from debug import motivate,ask_for_input,debug_hint,error_message_help

#example of motivate()
name = input("What is your name? ")
print(motivate(name))

#example of ask_for_input()
question = input("What's your question? ")
style = input("What style do you want your question in? (encouraging, sarcastic, philosophical)\n")
print(ask_for_input(question,style) + "\n")

#example of debug_hint()
issue_type = input("What kind of issue are you dealing with? (general, syntax, logic, runtime, performance)\n")
experience_level = input("What experience level are you? (beginner, intermediate, advanced)\n")
print(debug_hint(issue_type, experience_level)+"\n")

#example of error_message_help()
error = input("What specific error are you facing? (FileNotFoundError, ImportError, IndentationError, ValueError, AttributeError, KeyError, IndexError, TypeError, NameError, SyntaxError) \n")
print(error_message_help(error))