"""
Main entry point for the MyCodeBuddy application.

This script presents a command-line interface (CLI) allowing the user to choose between:
1. Debugging tips.
2. Python fun facts.
3. Language help resources.
4. A study timer with pause, resume, and cancel functionality.

It provides a user-friendly way to access these utilities by taking input from the user and executing the corresponding function.

Usage:
    The script is executed directly from the command line.
    The user will be prompted to select an option and follow subsequent instructions.
"""
import fun_facts as fun_fact
import get_debug_tips as debug
import get_help as help
from study_timer import StudyTimer

def main():
    try:
        function = int(input("What do you need help with? \n1. Debugging Tip\n2. Python Fun Fact\n3. Help Resources\n4. Study Timer\n(enter a number between 1-4): "))
        while (function < 1 or function > 4):
            function = int(input("Not a valid category. Please choose a number between 1-4: "))

        if function == 1:
            debug_option()
        elif function == 2:
            fun_facts_option()
        elif function == 3:
            help_resources_option()
        elif function == 4:
            study_timer_option()

    except ValueError as e:
        print(f"Error: {e}")

def debug_option():
    """
    Handles the debug tips option.
    """
    tip_type = int(input("\nAvailable types: \n1. Syntax\n2. Runtime\n3. Logic\nChoose a type (1-3): "))
    while (tip_type < 1 or tip_type > 3):
        tip_type = int(input("Invalid choice. Please choose a number between 1-3: "))

    tip_dict = {1: "syntax", 2: "runtime", 3: "logic"}
    print(debug.debug_tip(tip_dict[tip_type]))

def fun_facts_option():
    """
    Handles the fun facts option.
    """
    fact_type = int(input("\nAvailable types: \n1. Features\n2. Libraries\n3. Trivia\n4. Performance\nChoose a type (1-4): "))
    while (fact_type < 1 or fact_type > 4):
        fact_type = int(input("Invalid choice. Please choose a number between 1-4: "))

    fact_dict = {1: "features", 2: "libraries", 3: "trivia", 4: "performance"}
    print(fun_fact.get(fact_dict[fact_type]))

def help_resources_option():
    """
    Handles the help resources option.
    """
    language_type = int(input("\nWhat language do you need help with? \n1. Python\n2. Javascript\n3. Java\n4. c#\n5. c++\n6. php\n7. ruby\n8. swift\n9. r\n10. sql\n11. kotlin\n12. typescript\n13. go\n14. rust\n15. scala\n16. dart\n17. perl\nChoose a type (1-17): "))
    while (language_type < 1 or language_type > 17):
        language_type = int(input("Invalid choice. Please choose a number between 1-17: "))

    languages = [
        "Python", "Javascript", "Java", "c#", "c++", "php", "ruby", "swift", "r", "sql",
        "kotlin", "typescript", "go", "rust", "scala", "dart", "perl"
    ]
    print(help.language_help(languages[language_type - 1]))

def study_timer_option():
    """
    Handles the study timer option.
    """
    timer = StudyTimer()
    while True:
        command = input("Enter command (start, exit): ").strip().lower()
        if command == "start":
            start_timer(timer)
        elif command == "exit":
            print("Exiting MyCodeBuddy.")
            break
        else:
            print("Unknown command. Please try again.")

def start_timer(timer):
    """
    Starts the study timer and handles timer commands.
    """
    timer.start()
    while timer.running or timer.paused:
        sub_cmd = input("\nEnter timer command (pause, resume, cancel, turn off alarm): ").strip().lower()
        if sub_cmd == "pause":
            timer.pause()
        elif sub_cmd == "resume":
            timer.resume()
        elif sub_cmd == "cancel":
            timer.cancel()
        elif sub_cmd == "turn off alarm" and timer.completed:
            break
        elif sub_cmd == "turn off alarm":
            print("The alarm is not going off yet...")
        if timer.completed:
            timer.completed = False
            break

if __name__ == "__main__":
    main()
