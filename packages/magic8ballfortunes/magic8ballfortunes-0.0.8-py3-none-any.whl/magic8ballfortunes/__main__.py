"""
In Python packages, this file called __main__.py is run when the package is run
directly from command line, as opposed to importing it into another program.
"""

from .fortunes import Magic8Ball
import os


def main(*args):
    """
    Get some wise text and print it out.
    """

    os.system('cls' if os.name == 'nt' else 'clear')

    header = r"""
      .--------------------------.
     /                            \
    |    WELCOME TO MAGIC8BALL    |
     \                            /
      '--------------------------'
    """

    print(header)
    print("What type of fortune are you looking for?")
    print(" 1   - General")
    print(" 2   - Based on your name")
    print(" 3   - Based on a category")
    print(" 4   - Based on your birthday")
    print("-" * 40)

    choice = input("Input the number corresponding to your choice: ").strip()

    if choice == '1':
        fortune = Magic8Ball.tell_fortune()
    elif choice == '2':
        fortune = Magic8Ball.personalized_fortune(input("Enter your name: "))
    elif choice == '3':
        print("Enter a category:")
        print("     - Love")
        print("     - Career")
        print("     - Health")
        category = input("Enter choice: ").strip()
        fortune = Magic8Ball.fortune_by_category(category)
    elif choice == '4':
        fortune = Magic8Ball.daily_by_birth_month(input("Enter month (i.e. December): ").strip())
    else:
        fortune = "Invalid choice. Please try again."

    footer = f"""
         .---------------------.
        /                     /|
       /     YOUR FORTUNE    / |
      /         IS:         /  |
     '---------------------'   |
     |                     |  /
     |                     | /
     |_____________________|/

                ||
                ||
                \/

    {fortune}
    """
    print(footer)


if __name__ == "__main__":
    # run the main function
    main()
