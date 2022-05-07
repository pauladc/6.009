"""6.009 Lab 10: Snek Is You Video Game"""

import doctest
from operator import truediv

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

def inside_board(original, board, direction = (0,0)):
    if original[0] + direction[0] >= len(board) or original[1] + direction[1] >= len(board[0]):
        return False
    elif original[0] + direction[0] < 0 or original[1] + direction[1] < 0:
        return False
    else:
        return True

def change_position(original, board, direction):
    return (original[0] + direction[0], original[1] + direction[1])


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
        self.moveable = None
        self.toMove = None
    
    def restart_self(self):
        self.moveable = None
        self.toMove = None

    def restart_prop(self):
        self.properties = set()

    def is_moveable(self, direction):
        toTry = change_position(self.position, self.board, direction)
        next_obj = get_obj(self.board, toTry)
        if self.moveable != None:
            pass
        potential_push = []
        for obj in next_obj:
            if 'PUSH' not in obj.properties and 'STOP' in obj.properties:
                self.moveable = False
                return
            elif 'PUSH' in obj.properties:
                potential_push.append(obj)
        self.moveable = inside_board(toTry, self.board) and all(map(lambda obj: obj.is_moveable(direction), potential_push)) 
        return self.moveable

    def will_move(self, direction):
        next_position = change_position(self.position, self.board, direction)
        next_obj = get_obj(self.board, next_position)
        if self.toMove != None:
            pass
        else:
            self.toMove = True
            for obj in next_obj:
                if 'STOP' in obj.properties and 'PUSH' not in obj.properties:
                    self.toMove = False
            if self.toMove:
                for obj in next_obj:
                    if 'PUSH' in obj.properties:
                        obj.will_move(direction)
                pull_position = change_position(self.position, self.board, (-direction[0], -direction[1]))
                pulled_obj = get_obj(self.board, pull_position)
                for obj in pulled_obj:
                    if 'PULL' in obj.properties and obj.is_moveable(direction):
                        obj.will_move(direction)
        
def find_rules(game):
    def search_neighbors(obj, nouns, game_board, properties_dic):
        for direction in [(1, 0), (0, 1)]:
            new_position = change_position(obj.position, game_board, direction)
            if not inside_board(new_position, game_board):
                continue
            if get_obj(obj.board, new_position) != []:
                if get_obj(obj.board, new_position)[0].value == 'IS':
                    new_position = change_position(new_position, game_board, direction)
                    if get_obj(obj.board, new_position) != []:
                        new_obj = get_obj(obj.board, new_position)[0].value
                        if new_obj in PROPERTIES:
                            obj.properties.add(new_obj)
                            properties_dic[obj.board[new_position[0]][new_position[1]][0].value].append(obj)
                            nouns[obj.value.lower()].append(new_obj)
                        elif new_obj in NOUNS:
                            nouns[obj.value.lower()].append(new_obj)

    objects, game_board, properties_dic = game['objects'], game['board'], game['properties']

    nouns = {val.lower():[] for val in NOUNS}
    for obj in objects:
        if obj.value.isupper():
            if obj.value in PROPERTIES:
                obj.properties.add(obj.value)
                properties_dic[obj.value].append(obj)
            elif obj.value in NOUNS:
                search_neighbors(obj, nouns, game_board, properties_dic)

    for obj in objects:
        if obj.value in nouns:
            for props in nouns[obj.value]:
                obj.properties.add(props)
        elif obj.value in WORDS:
            obj.properties = {'PUSH'}

    return nouns


def are_nouns(game, nouns):
    for obj in game['objects']:
        if obj.value in nouns:
            for props in nouns[obj.value]:
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
    direction, board, objects = direction_vector[direction], game['board'], game['objects']

    for obj in objects:
        obj.restart_self()

    for obj in objects:
        if 'YOU' in obj.properties:
            if obj.is_moveable(direction):
                obj.will_move(direction)

    for obj in objects:
        if obj.toMove:
            get_obj(board, obj.position).remove(obj)
            obj.position = change_position(obj.position, obj.board, direction)
            get_obj(board, obj.position).append(obj)
    
    for obj in objects:
        obj.restart_prop()

    are_nouns(game, find_rules(game))

    toRemove, count = {}, 0

    for obj in objects:
        if 'YOU' in obj.properties:
            if any(map(lambda item: 'DEFEAT' in item.properties, board[obj.position[0]][obj.position[1]])):
                toRemove[(obj.position[0],obj.position[1], count)] = obj
                count += 1

    for key, val in toRemove.items():
        board[key[0]][key[1]].remove(val)
        objects.remove(val)

    for obj in objects:
        if 'YOU' in obj.properties:
            for in_cell in board[obj.position[0]][obj.position[1]]:
                if 'WIN' in in_cell.properties:
                    return True
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

