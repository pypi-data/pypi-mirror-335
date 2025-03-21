import os
import json
import random

# Determine the path to the data file within the package
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data.json')

with open(DATA_PATH, 'r') as f:
    DATA = json.load(f)


class Magic8Ball:

    DATA = DATA

    @staticmethod
    def tell_fortune() -> str:
        """Return a random general fortune."""
        return random.choice(DATA.get("general"))

    @staticmethod
    def personalized_fortune(name: str) -> str:
        """Return a personalized fortune including the given name."""
        
        if not isinstance(name, str):
            raise TypeError("Invalid input: The name must be provided as a string.")

        # Retrieve a random fortune from the "personalized" category
        fortunes = DATA.get("personalized")

        if fortunes:
            return f"{name}, {random.choice(fortunes)}"


    @staticmethod
    def fortune_by_category(category: str) -> str:
        """Return a fortune from the specified category ('love', 'career', 'health')."""

        if not isinstance(category, str):
            raise TypeError("Invalid input: The category must be provided as a string.")

        # Retrieve the fortunes under specified category
        fortunes = DATA.get("categories", {}).get(category.lower())
        if fortunes:
            return random.choice(fortunes)
        else:
            raise ValueError("Invalid Category: Please enter a valid category ('love', 'career', 'health')")

    @staticmethod
    def daily_by_birth_month(month: str) -> str:
        """
        Returns a personalized fortune message based on the given birth month.

        Parameters:
            month (str): The name of the birth month.

        Returns:
            str: A randomly selected fortune message for the given month.

        Raises:
            TypeError: If the input is not a string.
            ValueError: If the input is not a valid month name.
        """
        if not isinstance(month, str):
            raise TypeError("Invalid input: The month must be provided as a string.")

        birthdays = DATA["birthdays"]
        month = month.capitalize()

        if month in birthdays:
            return random.choice(birthdays[month])
        else:
            raise ValueError("Invalid month: Please enter a valid month name (e.g., 'January', 'February').")
    

    @staticmethod
    def fortune_by_personality(personality_type: str) -> str:
        """
        Return a fortune from the specified personality type.
        This function looks up fortunes under the "personalities" key in data.json.

        Raises:
            TypeError: If the input is not a string.
            ValueError: If the personality type is not recognized.
        """
        if not isinstance(personality_type, str):
            raise TypeError("Invalid input: The personality type must be a string.")

        personalities = DATA.get("personalities", {})
        # Normalize case, just like 'categories' does:
        personality_type_lower = personality_type.lower()

        if personality_type_lower in personalities:
            return random.choice(personalities[personality_type_lower])
        else:
            raise ValueError("Invalid Personality Type: Please provide a valid personality type (e.g. 'introvert', 'extrovert').")
