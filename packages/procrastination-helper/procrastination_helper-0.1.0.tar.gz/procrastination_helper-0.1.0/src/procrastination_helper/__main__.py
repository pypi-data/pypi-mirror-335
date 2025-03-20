"""
Main entry point for the procrastination_helper package.
This file is run when the package is executed directly from the command line.
It provides an interactive menu for selecting various procrastination features.
"""

import argparse

from procrastination_helper.customexcuses import get_custom_excuse
from procrastination_helper.get_excuse import get_excuse
from procrastination_helper.list_of_excuses import get_excuse_list
from procrastination_helper.quotes import get
from procrastination_helper.delay_timer import delay_timer


def get_procrastination_quotes(num_quotes):
    """
    Get procrastination quotes and return them.
    """
    return get(num_quotes=num_quotes)


def display_procrastination_wisdom(quotes):
    """
    Display procrastination wisdom quotes.
    """
    print("\nProcrastination Wisdom:")
    print(quotes)
    print("\nNote: More features coming soon!")


def display_sample_excuse():
    """
    Display a sample excuse.
    """
    print("\nSample Excuse:")
    print(get_excuse())


def get_task_and_custom_excuse():
    """
    Get the task input from the user and display a custom excuse.
    """
    task = input("\nWhat task are you procrastinating on? ")
    excuse = get_custom_excuse(task)
    print("\nYour custom excuse:")
    print(excuse)


def display_random_excuses(number_of_excuses):
    """
    Display a list of random excuses for procrastination.
    """
    excuses = get_excuse_list(number_of_excuses)
    print("\nHere are some random excuses for procrastination:")
    for excuse in excuses:
        print(f"- {excuse}")


def interactive_menu():
    """
    Display an interactive menu for the user to choose features.
    """
    while True:
        print("\n=== Procrastination Helper Menu ===")
        print("1. Get Procrastination Wisdom (Quotes)")
        print("2. Display a Sample Excuse")
        print("3. Get Custom Excuse for Your Task")
        print("4. Display Random Excuses")
        print("5. Use Delay Timer")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            try:
                num = int(input("How many quotes would you like? "))
            except ValueError:
                print("Invalid input. Defaulting to 1 quote.")
                num = 1
            quotes = get_procrastination_quotes(num)
            display_procrastination_wisdom(quotes)

        elif choice == "2":
            display_sample_excuse()

        elif choice == "3":
            get_task_and_custom_excuse()

        elif choice == "4":
            try:
                num = int(input("How many random excuses would you like? "))
            except ValueError:
                print("Invalid input. Defaulting to 3 excuses.")
                num = 3
            display_random_excuses(num)

        elif choice == "5":
            try:
                minutes = int(input("How many minutes do you want to procrastinate? "))
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                continue
            delay_timer(minutes)

        elif choice == "6":
            print("Goodbye! Now, maybe try being productive... eventually!")
            break

        else:
            print("Invalid choice. Please select a number between 1 and 6.")


def main():
    """
    Main function that parses command-line arguments.
    If no feature is specified via arguments, launch the interactive menu.
    """
    parser = argparse.ArgumentParser(
        description="Procrastination Helper - A package to help you delay productivity!"
    )
    parser.add_argument(
        "-f", "--feature",
        choices=["quotes", "sample", "custom", "random", "delay"],
        help=(
            "Specify a feature to run directly (quotes, sample, custom, random, delay). "
            "If not provided, an interactive menu will be displayed."
        )
    )
    parser.add_argument(
        "-n", "--number",
        type=int,
        default=1,
        help="Number of quotes or excuses to display (default: 1)."
    )
    parser.add_argument(
        "-t", "--time",
        type=int,
        default=5,
        help="Number of minutes for the delay timer (default: 5)."
    )
    args = parser.parse_args()

    # If a feature is specified via arguments, run that feature
    if args.feature:
        if args.feature == "quotes":
            quotes = get_procrastination_quotes(args.number)
            display_procrastination_wisdom(quotes)
        elif args.feature == "sample":
            display_sample_excuse()
        elif args.feature == "custom":
            get_task_and_custom_excuse()
        elif args.feature == "random":
            display_random_excuses(args.number)
        elif args.feature == "delay":
            delay_timer(args.time)
    else:
        # Otherwise, launch the interactive menu
        interactive_menu()


if __name__ == "__main__":
    main()
