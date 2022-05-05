"""6.009 Lab 10: Snek Is You Video Game"""

import doctest

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

def inside_board(original, len_board, direction = (0,0)):
    if original[0] + direction[0] >= len_board or original[1] + direction[1] >= len_board:
        return False
    elif original[0] + direction[0] < 0 or original[1] + direction[1] < 0:
        return False
    else:
        return True

def change_position(original, len_board, direction):
    if inside_board(original, len_board, direction,):
        return (original[0] + direction[0], original[1] + direction[1])
    else:
        raise ValueError

def get_obj(board, coordinates):
    if inside_board(coordinates, board):
        return board[coordinates[0]][coordinates[1]]
    else:
        return []


class gameObj():
    def __init__(self, value, board, position):
        self.properties = set()
        self.value = value
        self.board = board
        self.position = position
    
    def reset(self):
        self.move_allowed = None # or True or False
        self.moved = None # or True or False

    def move_obj(self, direction):
        try:
            try_position = change_position(self.position, len(self.board), direction)
        except:
            print('in exception')
            return self.board
        self.board[self.position[0]][self.position[1]] = []
        self.position = try_position
        self.board[try_position[0]][try_position[1]].append(self)

        
def find_rules(game):
    def search_neighbors(obj, nouns, len_board, properties_dic):
        for direction in [(1, 0), (0, 1)]:
            try:
                new_position = change_position(obj.position, len_board, direction)
            except:
                continue
            if obj.board[new_position[0]][new_position[1]] != []:
                if obj.board[new_position[0]][new_position[1]][0].value == 'IS':
                    try:
                        new_position = change_position(new_position, len_board, direction)
                        if obj.board[new_position[0]][new_position[1]] != []:
                            if obj.board[new_position[0]][new_position[1]][0].value in PROPERTIES:
                                obj.properties.add(obj.board[new_position[0]][new_position[1]][0].value)
                                properties_dic[obj.board[new_position[0]][new_position[1]][0].value].append(obj)
                                nouns[obj.value.lower()].append(obj.board[new_position[0]][new_position[1]][0].value)
                            elif obj.board[new_position[0]][new_position[1]][0].value in NOUNS:
                                nouns[obj.value.lower()].append(obj.board[new_position[0]][new_position[1]][0].value)
                    except:
                        pass    

    objects, len_board, properties_dic = game['objects'], len(game['board']), game['properties']
    nouns = {val.lower():[] for val in NOUNS}

    for obj in objects:
        if obj.value.isupper():
            if obj.value in PROPERTIES:
                obj.properties.add(obj.value)
                properties_dic[obj.value].append(obj)
            elif obj.value in NOUNS:
                search_neighbors(obj, nouns, len_board, properties_dic)

    for obj in objects:
        if obj.value in nouns:
            for props in nouns[obj.value]:
                obj.properties.add(props)
        elif obj.value in NOUNS or obj.value in PROPERTIES:
            obj.properties = {}
    print(nouns)

    return nouns


def are_nouns(game, nouns):
    for obj in game['objects']:
        if obj.value in nouns:
            print('in if')
            for props in nouns[obj.value]:
                print('props are ', props)
                if props in NOUNS:
                    obj.value = props.lower()
                    obj.properties = {p if p != props else {} for p in nouns[props.lower()]}
                    break
        

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
    print(level_description)
    board = []
    game_objs = []
    for r_idx in range(len(level_description)):
        new_row = []
        for c_idx in range(len(level_description[0])):
            if level_description[r_idx][c_idx] == []:
                new_row.append([])
            else:
                this_level = []
                for obj in level_description[r_idx][c_idx]:
                    new_obj = gameObj(obj, board, (r_idx, c_idx))
                    this_level.append(new_obj)
                    game_objs.append(new_obj)
                new_row.append(this_level)
        board.append(new_row)
    game = {
        'properties': {prop:[] for prop in PROPERTIES},
        'board': board,
        'objects': game_objs
    }
    are_nouns(game, find_rules(game))
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
    direction, properties, board, objects = direction_vector[direction], game['properties'], game['board'], game['objects']
    for obj in objects:
        print(obj.value, obj.properties)
        if 'YOU' in obj.properties:
            print('moving')
            obj.move_obj(direction)
    print(dump_game(game))
    return False



def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return [[[obj.value for obj in c] for c in r] for r in game['board']]

curr_game = [
      [["SNEK"], [], [], ["SNEK"]],
      [["IS"], [], ["snek"], ["IS"]],
      [["PULL"], ["snek"], [], ["PUSH"]],
      [[], [], [], []]
    ]

print(dump_game(new_game(curr_game)))
