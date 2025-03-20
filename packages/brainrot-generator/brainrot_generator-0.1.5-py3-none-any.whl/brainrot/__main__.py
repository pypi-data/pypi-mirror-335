"""
In Python packages, this file called __main__.py is run when the package is run
directly from command line, as opposed to importing it into another program.
"""

import brainrot.brainrot_functions as brainrot
import sys


def main():
    """
    Get some wise text and print it out.
    """
    n = 1
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Error: Argument must be an integer")
            sys.exit(1)
    
    line = brainrot.brainrot(n)  # get a line of text
    print(line)  # print it out


if __name__ == "__main__":
    # run the main function
    main()