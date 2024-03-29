import gspread
from google.oauth2.service_account import Credentials
from os import system, name
import random
import curses
import cursor
import re
from rich.table import Table
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.progress import Progress


# Constant variables
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
console = Console()
score = 0


# Functions
def welcome_snake():
    ''' ASCII art of welcome snake '''

    ascii = Padding(r"""
   _    _
,-(|)--(|)-.
\_   ..   _/
  \______/      .-. . . .-. . . .-.
    V  V        `-. |\| |-| |<  |-         ____
    `.^^`.      `-' ' ` ` ' ' ` `-'      (^,--`
      \^^^\                             (^^)
      |^^^|                  _,-._       \^^)
      (^^^^\      __      _,-'^^^^^`.    _,'^^)
       \^^^^`._,-'^^`-._.'^^^^__^^^^ `--'^^^_/
        \^^^^^ ^^^_^^^^^^^_,-'  `.^^^^^^^^_/
         `.____,-' `-.__.'        `-.___.'
""", (0, 15), style="green")
    console.print(ascii)


def snake_ascii():
    ''' The snake in ASCII art '''

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
""", (0, 15), style="green")
    console.print(ascii)


def start_menu():
    ''' The three buttons at the start page '''

    play_game = Panel("Play Game (p)", width=19, padding=(0, 2))
    console.print(Padding(play_game, (0, 30)))

    rules = Panel("Rules (r)", width=19, padding=(0, 4))
    console.print(Padding(rules, (0, 30)))

    highscore = Panel("Highscore (h)", width=19, padding=(0, 2))
    console.print(Padding(highscore, (0, 30)))


def start_menu_logic():
    ''' Makes the user to choose what they want to do; play game,
    read the rules or view the highscore'''

    while True:
        margin = 12
        selection = input(" " * margin).lower()
        if selection == "p":
            game_loop()
        elif selection == "r":
            rules_page()
        elif selection == "h":
            top_ten()
        else:
            make_choice = Padding("Please make a choice; "
                                  "'p', 'r', or 'h', and press Enter", (0, 12))
            console.print(make_choice)


def start_page():
    '''Views the start page with ASCII image'''

    cursor.hide()
    welcome_snake()
    start_menu()
    start_menu_logic()


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
            contain_letters = Padding("Your name should only contain "
                                      "letters. Please try again.", (0, 8))
            console.print(contain_letters)
    else:
        between_three = Padding("Your name should be between 3 and 13 letters."
                                " Please try again.", (0, 8))
        console.print(between_three)


def enter_name():
    ''' Makes the user to input their name '''

    cursor.show()
    global player_name

    while True:
        margin = 20
        player_name = input(" " * margin + "Please enter your name "
                            "(3-13 letters): \n" + " " * margin).capitalize()
        if validate_input(player_name):
            break
    return player_name


def take_me_back_logic():
    ''' The logic to make the user to go to the game or start page '''

    while True:
        margin = 15
        and_now = input(" " * margin).lower()
        if and_now == "p":
            game_loop()
            break
        elif and_now == "s":
            start_page()
            break
        else:
            easy_choice = Padding("Please make a choice; 'p' or 's', and "
                                  "press Enter", (0, 15))
            console.print(easy_choice)


def rules_page():
    ''' Present the rules for the user '''

    clear_screen()
    rules_text = Padding("""
    Rules:
    The rules are simple. You are the snake. So far, so good. Right?
    You control the snake with your arrow keys. Up make the snake to
    turn up, right makes the snake to turn right. Well, you get the
    picture. The goal is to eat as many of the lovely apples \u25cf as
    you can. When you eat an apple, you grow and get one apple longer
    than before.
    Beware of yourself! Don't collide into yourself!
    Beware of the walls! Don't collide into the walls!
    Easy peasy lemon squeezy! Right?\n
    To get to the game, press 'p'.
    If you want to go back and look at the beautiful snake
    at the start page, press 's'.""", (2, 2))
    console.print(rules_text)
    take_me_back_logic()


def get_ready_page():
    ''' Makes the user to enter their name '''

    snake_ascii()
    enter_name()


def last_before_game():
    ''' Let the user to press enter when they're ready to play '''

    cursor.hide()
    snake_ascii()
    only_one = Padding(f"So {player_name}, there is only one thing "
                       "left to ask...", (1, 19))
    console.print(only_one)
    margin = 11
    input(" " * margin + "Are you ready? If you are, "
          "buckle up and please press Enter\n")


def create_apple(snake, play_area):
    ''' Creates the apples which the snake is hunting for,
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
    insert a new dot when an apple is eaten '''

    stdscr.timeout(100)

    sh, sw = 24, 48
    play_area = curses.newwin(sh, sw, 0, 16)
    play_area.box("|", "-")
    play_area.keypad(1)
    play_area.timeout(100)

    snake = [
        [sh//2, sw//2+1],
        [sh//2, sw//2],
        [sh//2, sw//2-1]
    ]

    apple = create_apple(snake, play_area)
    direction = curses.KEY_RIGHT
    global score

    while True:
        next_direction = play_area.getch()
        direction = direction if next_direction == -1 else next_direction
        if (
            direction in [curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_DOWN,
                          curses.KEY_UP] and
            (direction == curses.KEY_RIGHT and snake[0][1] < sw-1) or
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

            if snake_new_head in snake:
                break

            snake.insert(0, snake_new_head)

            if snake[0] == apple:
                apple = create_apple(snake, play_area)
                score += 1
            else:
                snake_tail = snake.pop()
                play_area.addch(snake_tail[0], snake_tail[1], ' ')

            play_area.addch(snake[0][0], snake[0][1], "\u25a0")
            play_area.box("|", "-")

            ''' To add live score, code row below is from
            https://github.com/DanyYax/MisionCodigoRepo/blob/
            b1a45cc590dcfe0f00b01516eb1f22ef58b752a2/Snake/snake.py
            with modified placement '''

            play_area.addstr(0, int(sw * 0.6), "Score: {} ".format(score))
            play_area.refresh()
        else:
            break

    curses.endwin()


def wait_for_answer():
    ''' Makes the user decide if they want to play again '''

    cursor.show()

    yes = {"yes", "y", "ye", "", "ja"}
    no = {"no", "n", "nej"}
    while True:
        margin = 15
        play_again_answer = input(" " * margin + "Do you want to play again? "
                                  "(yes/no)\n" + " " * margin).lower()
        if play_again_answer in yes:
            return True
        elif play_again_answer in no:
            return False
        else:
            yes_or_no = Padding("Please answer 'yes' or 'no'", (0, 15))
            console.print(yes_or_no)


def add_to_highscore():
    ''' Add the players result to the highscore '''

    global score, player_name
    SHEET.worksheet("highscore").append_row([score, player_name])


def game_over():
    ''' Present the top 5 highscore to the user '''

    try:
        with Progress() as progress:
            task = progress.add_task("Loading highscore...", total=100)

            highscore = SHEET.worksheet("highscore")
            highscore_records = highscore.get_all_records()
            sorted_highscore = sorted(highscore_records, key=lambda
                                      x: x['Points'], reverse=True)
            top_five = sorted_highscore[:5]
            while not progress.finished:
                progress.update(task, advance=1)
    except Exception:
        clear_screen()
        not_working = Padding("Oopsie daisy... It seems like the highscore "
                              "list is unavaliable at the moment. Maybe it has"
                              " a coffee break, who knows? Please come back "
                              " and try again later.", (0, 8))
        console.print(not_working)
    else:
        clear_screen()

        if score < 10:
            ten = Padding(f"""
            Well... That was... Well played?
            Come on {player_name}, you can do better than {score} points...
            Take a look at the highscore below, take a deep breath
            and shoot for the stars!""", (2, 3))
            console.print(ten)
        elif score < 20:
            twenty = Padding(f"""
            Not too bad, not too bad!
            {player_name}, I must admit that I'm pretty impressed with
            you scoring {score} points.
            Are you maybe on the highscore list? Take a look below!""", (2, 3))
            console.print(twenty)
        elif score < 30:
            thirty = Padding(f"""
            Are you born to play Snake {player_name}?
            You scored {score} points, that's really good!
            I must admit that you made my jaw drop...""", (2, 3))
            console.print(thirty)
        else:
            top_score = Padding(f"""
            Are you kidding with me {player_name}!?
            Did you really score {score} points!?
            Wow. Maybe it is time to sign up for the world
            champoinship in Snake?""", (2, 3))
            console.print(top_score)

        highscore_list = Table()
        highscore_list.add_column("Name", width=15)
        highscore_list.add_column("Points", width=6)
        for entry in top_five:
            highscore_list.add_row(entry['Name'], str(entry['Points']))
        padded_highscore = Padding(highscore_list, (0, 0, 1, 26))
        console.print(padded_highscore)


def top_ten():
    ''' Present the top 10 highscore to the user '''

    clear_screen()

    try:
        with Progress() as progress:
            task = progress.add_task("Loading highscore...", total=100)

            highscore = SHEET.worksheet("highscore")
            highscore_records = highscore.get_all_records()
            sorted_highscore = sorted(highscore_records, key=lambda
                                      x: x['Points'], reverse=True)
            top_ten = sorted_highscore[:10]
            while not progress.finished:
                progress.update(task, advance=1)
    except Exception:
        not_working = Padding("Oopsie daisy... It seems like the highscore "
                              "list is unavaliable at the moment. Maybe it has"
                              " a coffee break, who knows? Please come back "
                              " and try again later.", (0, 8))
        console.print(not_working)
    else:
        clear_screen()

        highscore_list = Table(title="Top 10 highscore")
        highscore_list.add_column("Name", width=15)
        highscore_list.add_column("Points", width=6)
        for entry in top_ten:
            highscore_list.add_row(entry['Name'], str(entry['Points']))
        padded_highscore = Padding(highscore_list, (1, 0, 0, 26))
        console.print(padded_highscore)

    take_me_back = Padding("""
    To get to the game, press 'p'.
    If you want to go back and look at the
    beautiful snake at the start page, press 's'.""", (1, 15))
    console.print(take_me_back)

    take_me_back_logic()


def thanks_for_playing():
    ''' The end screen, thanking the user for the game '''

    clear_screen()
    cursor.hide()

    thanks_text = Padding("""
    So you don't want to play anymore?
    Well, it's up to you. You know where
    to find us when you want to conquer the highscore!

    For now, so long and thank you for the fish!""", (4, 11))
    console.print(thanks_text)


def game_loop():
    ''' The snake game loop '''

    while True:
        clear_screen()
        get_ready_page()
        clear_screen()
        last_before_game()
        curses.wrapper(main_game)
        add_to_highscore()
        game_over()
        global score
        score = 0
        if not wait_for_answer():
            break
    thanks_for_playing()


def main():
    ''' The entire program loop'''

    start_page()
    game_loop()


if __name__ == "__main__":
    main()
