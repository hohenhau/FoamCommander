#!/usr/bin/python

def get_positive_metric_input(prompt: str):
    while True:
        try:
            metric = float(input(prompt))
            if metric <= 0:
                raise ValueError("Value must be positive")
            return metric
        except ValueError as e:
            print(f"Invalid input: {e}")


def get_valid_text_input(prompt: str) -> str:
    """Retrieves a text input consisting strictly of alphabetic characters."""
    while True:
        user_input = input(prompt).strip()
        if user_input.isalpha():
            return user_input
        print("Invalid input: Please enter alphabetic characters only (no spaces, numbers, or symbols).")