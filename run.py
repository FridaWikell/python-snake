# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

# Start view

def print_ascii(filename):
    file = open(filename, 'r')
    print(''.join([line for line in file]))

def enter_name():
    player_name = input("Please enter your name: ")
  

print_ascii("snake-ascii.txt")
print_ascii("welcome-ascii.txt")
input("Press Enter to continue...")
enter_name()
