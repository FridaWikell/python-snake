# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

import gspread
from google.oauth2.service_account import Credentials
from os import system, name
import random
import curses
import keyboard

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
    global player_name 
    player_name = input("Please enter your name: \n")

    return player_name


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
    print("\nSo, there is only one thing left to ask...\n\n")
    input("Are you ready? If so, please press Enter\n")
   

def create_apple(snake, play_area):
    # -2 is used to not get the food to close to the egdese of the scren 
    sh, sw = play_area.getmaxyx()
    apple = [random.randint(1, sh-2), random.randint(1, sw-2)]

    while apple in snake:
        apple = [random.randint(1, sh-2), random.randint(1, sw-2)]

    play_area.addch(apple[0], apple[1], "O")

    return apple


def main_game(stdscr):
    # the timeout is set for getch in milliseconds
    # Kanske ersätta med sh, sw = stdscr.getmaxyx() ?
    #new win sätts 20 in och 4 ner. Kanske ändra för att få äpplet rätT?
    #win = curses.newwin(height, width, begin_y, begin_x)
    global score    

    stdscr.timeout(100)

    sh, sw = stdscr.getmaxyx()
    play_area = curses.newwin(sh, sw, 0, 0)
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

# skriva ut direction = 
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

            play_area.addch(snake[0][0], snake[0][1], "X")

        else:
            break

    curses.endwin()


def wait_for_answer():
    yes = {"yes","y", "ye", "", "ja"}
    no = {"no", "n", "nej"}

    play_again_answer = input("\nDo you want to play again? \n").lower()
    if play_again_answer in yes:
        #return True
        print("Yeah!")
    elif play_again_answer in no:
        # return False
        print("noooo...")
    else:
        print("Please answer yes or no")


def add_to_highscore():
    global score
    SHEET.worksheet("highscore").append_row([str(score), player_name])


def game_over():
    print_ascii("dead-snake-ascii.txt")
    print("Well... That was... Well played? "
          f"Come on {player_name}, you can do better than {score} points... "
          "Take a look at the highscore below, take a deep breath "
          "and shoot for the stars!\n")

    print("{:15}".format("Name:"), "{:5}".format("Points:"))
    
    highscore = SHEET.worksheet("highscore")

    # Sortera highscore och visa top fem

    highscore_records = highscore.get_all_records()
    sorted_highscore = sorted(highscore_records, key=lambda x: x['Points'], reverse=True)
    top_five = sorted_highscore[:5]

    highscore_names = [entry['player_name'] for entry in top_five]
    highscore_points = [entry['score'] for entry in top_five]

    present_highscore = "\n".join("{:15} {:5}".format(x, y) for x, y in zip(highscore_names, highscore_points))

    print(present_highscore)

    wait_for_answer()



def main():
    start_page()
    clear_screen()
    rules_page()
    clear_screen()
    get_ready_page()
    clear_screen()

main()
if __name__ == "__main__":
    try:
        curses.wrapper(main_game)
        add_to_highscore()    
        game_over()
    except curses.error as e:
        print(f"Curses error: {e}")

