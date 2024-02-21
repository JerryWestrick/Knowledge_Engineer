You are writing a python version of the snake game using pygame.

# Game constants
    SNAKE_CHARACTERS = ["🔴", "🔵", "🟠", "🟡", "🟢", "🟣", "🟤"]
    FOOD_CHAR = "🍎"
    FOOD_COUNT = 5
    DIRECTION = {"Stop": (0, 0), "Up": (0,-1), "Down": (0,1), "Left": (-1,0), "Right": (1,0) }


# The Game

It is the standard "snake" game.

#### Architecture: 
python 3, with pygame

#### The game_board 
Terminal width x terminal height 2d character representation of the playing ground.
is kept up to date with the values of Snake and Foods; 
Therefor you can check for collisions by checking the value of the character in the game_board at position (x, y).

#### Step Logic:
The game is implemented as steps 5 per second.
