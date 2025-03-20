"""isoddeven Command Line Interface (CLI)
=====
This module allows you to check if a number is odd or even through the terminal.
"""

import argparse
from isoddeven import isodd, iseven, state

def main():
    parser = argparse.ArgumentParser(description="Check if a number is odd or even.")
    
    # Add mutually exclusive arguments (-o and -e) (optional flags)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-o", "--odd", help="Check if the number is odd (returns True/False)", action="store_true")
    group.add_argument("-e", "--even", help="Check if the number is even (returns True/False)", action="store_true")

    parser.add_argument("number", type=int, help="The number to check")
    args = parser.parse_args()

    # Handle the cases based on user input
    if args.odd:
        print(isodd(args.number))
    elif args.even:
        print(iseven(args.number))
    else:
        print(f"{args.number} is " + state(args.number))

if __name__ == "__main__":
    main()
