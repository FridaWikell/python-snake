# Write your code to expect a terminal of 80 characters wide and 24 rows high

import gspread
from google.oauth2.service_account import Credentials
from os import system, name
import random
import curses
import cursor
import re
import rich
from rich.table import Table
from rich.console import Console
from rich.theme import Theme
from rich.padding import Padding
from rich.panel import Panel


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("snake_highscore")


# Global varibles
score = 0
console = Console()


# Functions 

def print_ascii(filename, style=None):
    '''Opens ascii images and print them'''

    with open(filename, "r") as file:
        ascii_art = ''.join([line for line in file])

    if style:
        console.print(ascii_art, style=style)
    else:
        console.print(ascii_art)


def snake_ascii():
    ascii = Padding(r"""
   _    _
,-(|)--(|)-.
\_   ..   _/
  \______/
    V  V                                  ____
    `.^^`.                               (^,--`
      \^^^\                             (^^)
      |^^^|                  _,-._       \^^)
      (^^^^\      __      _,-'^^^^^`.    _,'^^)
       \^^^^`._,-'^^`-._.'^^^^__^^^^ `--'^^^_/
        \^^^^^ ^^^_^^^^^^^_,-'  `.^^^^^^^^_/ 
         `.____,-' `-.__.'        `-.___.' 
"""
    , (0, 15), style="green")
    console.print(ascii)


def welcome_ascii():
    ascii = Padding(r"""
. . .     |                           |            ,---.          |         |
| | |,---.|    ,---.,---.,-.-.,---.   |--- ,---.   `---.,---.,---.|__/ ,---.|
| | ||---'|    |    |   || | ||---'   |    |   |       ||   |,---||  \ |---' 
`-'-'`---'`---'`---'`---'` ' '`---'   `---'`---'   `---'`   '`---^`   ``---'o"""
    , (0, 1), style="green")

    console.print(ascii)



def start_page():
    '''Views the start page with ascii images'''

    cursor.hide()
    snake_ascii()
    welcome_ascii()
    margin = 20
    input(" " * margin + "Press Enter to continue...")


def clear_screen():
    ''' Clear the screen for Windows respectively Mac/linux '''

    if name == 'nt':
        system('cls')
    else:
        system('clear')


def validate_input(input_string):
    ''' Validate the input to be only letters, between 3 and 13 letters '''
    letters_only = re.compile(r'^[a-zA-Z]+$')

    if 3 <= len(input_string) <= 13:
        if letters_only.match(input_string):
            return True
        else:
            contain_only_letters = Padding("Your name should only contain letters. Please try again.", (0, 4))
            console.print(contain_only_letters)
    else:
        between_three = Padding("Your name should be between 3 and 13 letters. Please try again.", (0, 4))
        console.print(between_three)


def enter_name():
    ''' Makes the user to input their name '''

    cursor.show()
    global player_name

    while True:
        margin = 4
        player_name = input(" " * margin + "Please enter your name (3-13 letters): \n").capitalize()
        if validate_input(player_name):
            break

    return player_name


def rules_page():
    ''' Present the rules for the user '''

    rules_text = Padding("""
    Rules:
    The rules are simple. You are the snake. So far, so good. Right?
    You control the snake with your arrow keys. Up make the snake to
    turn up, right makes the snake to turn right. Well, you get the 
    picture. The goal is to eat as many of the lovely apples (o) as 
    you can. When you eat an apple, you grow and get one apple longer
    than before.
    Beware of yourself! Don't collide into yourself!
    Beware of the walls! Don't collide into the walls!
    Easy peasy lemon squeezy! Right?\n""", (2,4))

    console.print(rules_text)
    enter_name()


def get_ready_page():
    ''' Let the user to press enter when they're ready to play '''

    cursor.hide()
    snake_ascii()
    print("\nSo, there is only one thing left to ask...\n\n")
    margin = 6
    input(" " * margin + "Are you ready? If so, please press Enter\n")
   

def create_apple(snake, play_area):
    ''' Create the apples which the snake is hunting for
    -2 is used to not get the apples to close to the edges '''

    sh, sw = 20, 40
    apple = [random.randint(1, sh-2), random.randint(1, sw-2)]

    while apple in snake:
        apple = [random.randint(1, sh-2), random.randint(1, sw-2)]

    play_area.addch(apple[0], apple[1], "\u25cf")

    return apple


def main_game(stdscr):
    ''' The main game loop. It sets the playboard, 
     make sure the snake starts in the middle, controls the snake, 
      insert a new X when an apple is eaten '''

    # the timeout is set for getch in milliseconds
    # Kanske ersätta med sh, sw = stdscr.getmaxyx() ?
    #new win sätts 20 in och 4 ner. Kanske ändra för att få äpplet rätT?
    #win = curses.newwin(height, width, begin_y, begin_x)
    score = 0    

    stdscr.timeout(100)

    sh, sw = 20, 40
    play_area = curses.newwin(sh, sw, 4, 20)
    play_area.box("|", "-")
    play_area.keypad(1)
    play_area.timeout(100)
    

    # To make sure the snake starts in the middle
    snake = [
        [sh//2, sw//2+1],
        [sh//2, sw//2],
        [sh//2, sw//2-1]
    ]

    apple = create_apple(snake, play_area)


    # Makes the snake start to the right
    direction = curses.KEY_RIGHT


    # vad gör första if?
    while True:
        next_direction = play_area.getch()
        direction = direction if next_direction == -1 else next_direction

        if (
            direction in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_DOWN, curses.KEY_UP] and
            (direction == curses.KEY_RIGHT and snake[0][1] < sw -1) or
            (direction == curses.KEY_LEFT and snake[0][1] > 0) or
            (direction == curses.KEY_DOWN and snake[0][0] < sh-1) or
            (direction == curses.KEY_UP and snake[0][0] > 0)
        ):
            snake_new_head = [snake[0][0], snake[0][1]]

            if direction == curses.KEY_RIGHT:
                snake_new_head[1] += 1
            elif direction == curses.KEY_LEFT:
                snake_new_head[1] -= 1
            elif direction == curses.KEY_DOWN:
                snake_new_head[0] += 1
            elif direction == curses.KEY_UP:
                snake_new_head[0] -= 1

            snake.insert(0, snake_new_head)

            if snake[0] == apple:
                apple = create_apple(snake, play_area)
                score += 1
            else:
                snake_tail = snake.pop()
                play_area.addch(snake_tail[0], snake_tail[1], ' ')

            play_area.addch(snake[0][0], snake[0][1], "\u25a0")

        else:
            break

    curses.endwin()


def wait_for_answer():
    ''' Makes the user decide if they want to play again '''

    yes = {"yes","y", "ye", "", "ja"}
    no = {"no", "n", "nej"}

    while True:
        margin = 6
        play_again_answer = input(" " * margin + "\nDo you want to play again? \n").lower()
        if play_again_answer in yes:
            return True     
        elif play_again_answer in no:
            return False
        else:
            yes_or_no = Padding("Please answer yes or no", (0, 6))
            console.print(yes_or_no)


def add_to_highscore():
    ''' Add the players result to the highscore '''

    global score, player_name
    SHEET.worksheet("highscore").append_row([score, player_name])


def game_over():
    ''' Present the top 5 highscore to the user '''

    highscore = SHEET.worksheet("highscore")
    
    highscore_records = highscore.get_all_records()
    sorted_highscore = sorted(highscore_records, key=lambda x: x['Points'], reverse=True)
    top_five = sorted_highscore[:5]
    

    highscore_text = Padding(f"""
    Well... That was... Well played?
    Come on {player_name}, you can do better than {score} points...
    Take a look at the highscore below, take a deep breath
    and shoot for the stars!""", (2, 6))

    console.print(highscore_text)
    

    highscore_list = Table()
    highscore_list.add_column("Name", width=15)
    highscore_list.add_column("Points", width=6)

    for entry in top_five:
        highscore_list.add_row(entry['Name'], str(entry['Points']))

    padded_highscore = Padding(highscore_list, (0, 26))
    console.print(padded_highscore)   


def thanks_for_playing():
    ''' The end screen, thanking the user for the game '''

    clear_screen()
    cursor.hide()

    thanks_text = Padding("""
    So you don't want to play anymore?
    Well, it's up to you. You know where
    to find us when you want to conquer the highscore!
     
    For now, so long and thank you for the fish!""", (4, 8))

    console.print(thanks_text)


def main():
    ''' The entire program loop'''

    start_page()
    clear_screen()
    rules_page()

    while True:
        clear_screen()
        get_ready_page()
        clear_screen()
        curses.wrapper(main_game)
        add_to_highscore()    
        game_over()
        
        if not wait_for_answer(): 
            break

    thanks_for_playing()
    

main()