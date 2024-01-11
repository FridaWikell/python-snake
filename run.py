# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

def print_ascii(filename):
    '''Opens ascii images and print them'''

    file = open(filename, "r")
    print(''.join([line for line in file]))


def start_page():
    '''Views the start page with ascii images'''

    print_ascii("snake-ascii.txt")
    print_ascii("welcome-ascii.txt")
    input("Press Enter to continue...")


def enter_name():
    player_name = input("Please enter your name: ")


def main():
    start_page()


main()
enter_name()
