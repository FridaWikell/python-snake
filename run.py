# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

from os import system, name
import random
import keyboard


def print_ascii(filename):
    '''Opens ascii images and print them'''

    file = open(filename, "r")
    print(''.join([line for line in file]))


def start_page():
    '''Views the start page with ascii images'''

    print_ascii("snake-ascii.txt")
    print_ascii("welcome-ascii.txt")
    input("Press Enter to continue...")


def clear_screen():
    ''' Clear the screen for Windows respectively Mac/linux '''

    if name == 'nt':
        system('cls')
    else:
        system('clear')


def enter_name():
    player_name = input("Please enter your name: ")


def rules_page():
    print("Rules:\n")
    print("The rules are simple. You are the snake. So far, so good. Right? "
          "You control the snake with your arrow keys. Up make the snake to"
          "turn up, right makes the snake to turn right. Well, you get the picture."
          "The goal is to eat as many of the lovely apples (o) as you can. "
          "When you eat an apple, you grow and get one apple longer than before.\n"
          "Beware of yourself! Don't collide into yourself!\n"
          "Beware of the walls! Don't collide into the walls!\n"
          "Easy peasy lemon squeezy! Right?\n")
    enter_name()


def get_ready_page():
    print_ascii("snake-ascii.txt")
    print("\nSo, there is only one thing left to ask...\n\n"
          "Are you ready? If so, please press 's'")
    keyboard.wait('s')
    

def create_apple(snake, window):
    # -2 is used to not get the food to close to the egdese of the scren 
    sh, sw = 20, 40
    apple = [random.randint(1, sh-2), random.randint(1, sw-2)]

    while apple in snake:
        apple = [random.randint(1, sh-2), random.randint(1, sw-2)]

    window.addch(apple[0], apple[1], "O")

    return apple

def main_game():
    

def main():
    start_page()
    clear_screen()
    rules_page()
    clear_screen()
    get_ready_page()
    clear_screen()


main()

create_apple(snake, window)
