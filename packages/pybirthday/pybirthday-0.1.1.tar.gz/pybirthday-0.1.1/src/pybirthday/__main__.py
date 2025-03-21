"""
In Python packages, this file called __main__.py is run when the package is run
directly from command line, as opposed to importing it into another program.
"""

import pybirthday


def main():
    """
    Get some birthday-themed visuals.
    """
    line = pybirthday.cake('Alex', 'Words')
    print(line)

    candle_str_1 = pybirthday.candle(3)
    print(candle_str_1)

    candle_str_2 = pybirthday.candle()
    print(candle_str_2)

    balloon_str_1 = pybirthday.balloon(2)  # Display a specific balloon
    print(balloon_str_1)
    
    balloon_str_2 = pybirthday.balloon()  # Display a random balloon
    print(balloon_str_2)

    teddy_str_1 = pybirthday.teddy()
    print(teddy_str_1)

    teddy_str_2 = pybirthday.teddy("20th", "Lauren")
    print(teddy_str_2)

if __name__ == "__main__":
    # run the main function
    main()