"""6.009 Lab 10: Snek Is You Video Game"""

from curses.ascii import isupper
import doctest
from xxlimited import new

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def inside_board(original, direction, board):
    if original[0] + direction[0] >= len(board) or original[1] + direction[1] >= len(board[0]):
        return False
    elif original[0] + direction[0] < 0 or original[1] + direction[1] < 0:
        return False
    else:
        return True

def change_position(original, direction, board):
    if inside_board(original, direction, board):
        return (original[0] + direction[0], original[1] + direction[1])
    else:
        raise ValueError


class gameObj():
    def __init__(self, value, board, position):
        self.value = value
        self.board = board
        self.position = position
        self.properties = set()
    
    # def try_move(self, direction):
    #     try_position = change_position(self.position, direction)
    #     forward_neighbors = get_position(self.board, try_position)
    #     if self.can_move is not None:
    #         pass
    #     elif any(map(lambda n: 'STOP' in n.properties and 'PUSH' not in n.properties, forward_neighbors)):
    #         self.can_move = False
    #     else:
    #         self.can_move = all(map(lambda n: n.try_move(direction),
    #                 filter(lambda n: n.properties & {'PUSH'}, forward_neighbors))) and \
    #             position_in_bounds(self.board, try_position)
    #     return self.can_move
def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    board = []
    objects = []
    for r_idx in range(len(level_description)):
        new_row = []
        for c_idx in range(len(level_description[0])):
            if level_description[r_idx][c_idx] == []:
                new_row.append([])
            else:
                new_obj = gameObj(level_description[r_idx][c_idx], board, (r_idx, c_idx))
                new_row.append(new_obj)
                objects.append(new_obj)
        board.append(new_row)
    game = {
        'property_map': {property: [] for property in PROPERTIES},
        'board': board,
        'objects': objects
    }
    return game


def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """
    # if "snek" in game.values().value:

    # return False


def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    raise NotImplementedError
