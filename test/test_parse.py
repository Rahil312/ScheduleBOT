"""
Module for testing parsing functions.

This module contains unit tests for the parsing functionalities
implemented in the parse.match module.
"""

import sys
import os
import datetime
import string
from random import randint, choices

import pytest

from parse.match import parse_period

NUM_ITER = 1000

def random_datetime(start_year=2020, end_year=2025):
    """
    Generate a random datetime object within a specified range.

    Args:
        start_year (int, optional): The starting year. Defaults to 2020.
        end_year (int, optional): The ending year. Defaults to 2025.

    Returns:
        datetime.datetime: A randomly generated datetime object.
    """
    # Determine all possible days between the start and end
    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(end_year, 12, 31)

    # Calculate the total number of days
    delta_days = (end_date - start_date).days

    # Choose a random day
    chosen_day = randint(0, delta_days)

    # Randomly pick a time
    hour = randint(0, 23)
    minute = randint(0, 59)

    # Get the random date
    date = start_date + datetime.timedelta(days=chosen_day)

    # Combine date and time
    return datetime.datetime(
        date.year,
        date.month,
        date.day,
        hour,
        minute
    )

def to_military(dt):
    """
    Convert a datetime object to a military time string.

    Args:
        dt (datetime.datetime): The datetime object.

    Returns:
        str: Formatted datetime string in military time.
    """
    return f"{dt.month:02}/{dt.day:02}/{dt.year} {dt.hour}:{dt.minute:02}"

def to_12hour(dt):
    """
    Convert a datetime object to a 12-hour time string.

    Args:
        dt (datetime.datetime): The datetime object.

    Returns:
        str: Formatted datetime string in 12-hour time.
    """
    ampm = "am" if dt.hour < 12 else "pm"
    hour = dt.hour % 12
    if hour == 0:
        hour = 12
    return f"{dt.month:02}/{dt.day:02}/{dt.year} {hour}:{dt.minute:02} {ampm}"

def period_to_string(date1, date2):
    """
    Convert two datetime objects to a period string.

    Each date has a 50% chance of being in military or 12-hour format.

    Args:
        date1 (datetime.datetime): The first datetime object.
        date2 (datetime.datetime): The second datetime object.

    Returns:
        str: The period string representing date1 to date2.
    """
    s = ""
    for dt in [date1, date2]:
        # 50% chance of military or 12-hour format
        if randint(0, 1) == 0:
            s += to_military(dt)
        else:
            s += to_12hour(dt)
        s += " "
    return s.strip()

def test_correct():
    """
    Test parsing of correct date periods.

    This test generates random valid date periods and verifies that
    the parse_period function correctly parses them into the original datetime objects.
    """
    for _ in range(NUM_ITER):
        # Pick 2 random dates
        date1 = random_datetime()
        date2 = random_datetime()
        date1, date2 = min(date1, date2), max(date1, date2)

        s = period_to_string(date1, date2)
        
        # Parse input; expecting correct parsing
        res_date1, res_date2 = parse_period(s)

        assert res_date1 == date1, f"Expected {date1}, got {res_date1}"
        assert res_date2 == date2, f"Expected {date2}, got {res_date2}"

def test_swapped():
    """
    Test parsing with inverted date periods (start date after end date).

    This test generates date periods where the start date is after the end date
    and verifies that parse_period raises a ValueError with the appropriate message.
    """
    for _ in range(NUM_ITER):
        # Pick 2 random dates
        date1 = random_datetime()
        date2 = random_datetime()
        date1, date2 = max(date1, date2), min(date1, date2)

        s = period_to_string(date1, date2)

        # It should fail; ensure exception is raised
        with pytest.raises(ValueError, match="your starting date is after your ending date"):
            parse_period(s)

def test_impossible():
    """
    Test parsing of impossible dates (e.g., Feb 30, Feb 29 in non-leap years).

    This test attempts to parse date periods with invalid dates and verifies
    that parse_period raises a ValueError with the appropriate message.
    """
    # Define invalid date cases
    invalid_cases = [
        (2, 29, 2023),  # Non-leap year
        (2, 30, 2024),  # Even in leap year, Feb 30 doesn't exist
    ]
    # Add months that don't have 31 days
    invalid_cases += [(month, 31, 2022) for month in [2, 4, 6, 9, 11]]

    # Test invalid ending dates
    for mm, dd, yyyy in invalid_cases:
        date1 = random_datetime(2020, 2021)
        
        s = to_military(date1) + " " + f"{mm:02}/{dd:02}/{yyyy} 0:00"

        # It should fail; ensure exception is raised
        with pytest.raises(ValueError, match="your entered date is not possible"):
            parse_period(s)
    
    # Test invalid starting dates
    for mm, dd, yyyy in invalid_cases:
        date2 = random_datetime(2025, 2026)
        
        s = f"{mm:02}/{dd:02}/{yyyy} 0:00 " + to_military(date2)

        # It should fail; ensure exception is raised
        with pytest.raises(ValueError, match="your entered date is not possible"):
            parse_period(s)

def gibberish():
    """
    Generate a random string with uppercase, lowercase letters, and some symbols.

    Returns:
        str: A randomly generated string.
    """
    return ''.join(choices(string.ascii_letters + " /:", k=randint(0, 62)))

def test_gibberish():
    """
    Test parsing with random, nonsensical input.

    This test generates random strings that do not conform to expected date formats
    and verifies that parse_period raises an exception.
    """
    for _ in range(NUM_ITER):
        s = gibberish()

        # It should fail; ensure exception is raised
        with pytest.raises(Exception):
            parse_period(s)
