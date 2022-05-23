# 6.009 Lab 2: Snekoban

from hashlib import new
import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    init_game = {}
    for row in range(len(level_description)):
        for col in range(len(level_description[0])):
            init_game[(row, col)] = level_description[row][col]
    return init_game

def player_and_computers(game):
    toReturn = []
    for key, val in game.items():
        if "computer" in val or "player" in val:
            toReturn.append((tuple(key), tuple(val.copy())))
    return tuple(toReturn)


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    check = False
    for key in game.keys():
        if game[key] != [] and 'target' in game[key]:
            if 'computer' in game[key]:
                check = True
            else:
                return False
    return check


def is_step_possible(game, direction):
    for key, value in game.items():
        if 'player' in value:
            player_loc = key 
    new_loc = (direction_vector[direction][0]+player_loc[0], direction_vector[direction][1]+player_loc[1])
    if game[new_loc] == ['wall']:
        return False
    elif 'computer' in game[new_loc]:
        if 'computer' in game[(direction_vector[direction][0]+new_loc[0], direction_vector[direction][1]+new_loc[1])] or game[(direction_vector[direction][0]+new_loc[0], direction_vector[direction][1]+new_loc[1])] == ['wall']:
            return False
    return True

def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    new_step = {key:value.copy() for key, value in game.items()}
    for key, value in new_step.items():
        if 'player' in value:
            player_loc = key 
    #print('original: ', player_loc)
    new_loc = (direction_vector[direction][0]+player_loc[0], direction_vector[direction][1]+player_loc[1])
    #print('new: ', new_loc)
    if new_step[new_loc] == ['wall']:
        return new_step
    elif 'computer' in new_step[new_loc]:
        if 'computer' in new_step[(direction_vector[direction][0]+new_loc[0], direction_vector[direction][1]+new_loc[1])] or new_step[(direction_vector[direction][0]+new_loc[0], direction_vector[direction][1]+new_loc[1])] == ['wall']:
            return new_step
        new_step[new_loc].remove('computer')
        new_step[new_loc].append('player')
        new_step[(direction_vector[direction][0]+new_loc[0], direction_vector[direction][1]+new_loc[1])].append('computer')
    else:
        new_step[new_loc].append('player')
    new_step[player_loc].pop()
    return new_step


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    num_rows = list(game.keys())[len(game)-1][0]
    nums_columns = list(game.keys())[len(game)-1][1]
    toReturn = []
    for i in range(num_rows+1):
        row = []
        for j in range(nums_columns+1):
            row.append(game[(i,j)])
        toReturn.append(row)
    return toReturn


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    if victory_check(game):
        return []
    queue = [[game, []]]
    visited = set()
    first_visit = player_and_computers(game)
    visited.add(first_visit)
    possible_wins = []
    while len(queue) != 0:
        zero_queue = queue.pop(0)
        curr_path = zero_queue[0]
        if len(possible_wins) > 0 and len(zero_queue[1])+1 > len(min(possible_wins)):
            next
        else:
            directions = ['up', 'down', 'left', 'right']
            for direction in directions:
                if is_step_possible(curr_path, direction):
                    new_game = step_game(curr_path, direction)
                    now_visited = player_and_computers(new_game)
                    if now_visited not in visited:
                        queue.append([new_game, zero_queue[1] + [direction]])
                        visited.add(now_visited)
                        if victory_check(new_game):
                            possible_wins.append(queue[-1][1])
    if possible_wins == []:
        return None
    return min(possible_wins)





if __name__ == "__main__":
    
#    test_1 = [[["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]], [["wall"], [], [], [], ["player"], [], [], ["wall"]], [["wall"], [], [], [], ["target", "computer"], [], [], ["wall"]], [["wall"], ["wall"], ["wall"], ["target"], ["computer"], ["wall"], ["wall"], ["wall"]], [[], [], ["wall"], [], ["target", "computer"], [], ["wall"], []], [[], [], ["wall"], [], [], [], ["wall"], []], [[], [], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], []]]
#    check_g = new_game(test_1)
#    print(victory_check(check_g))
    pass

