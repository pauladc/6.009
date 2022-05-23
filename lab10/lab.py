"""6.009 Lab 10: Snek Is You Video Game"""

import doctest
from operator import truediv

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
NOT_ALL_WORDS = NOUNS | PROPERTIES
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def inside_board(original, board, direction = (0,0)):
    """
    Checks if the location is inside the board
    """
    if original[0] + direction[0] >= len(board) or original[1] + direction[1] >= len(board[0]):
        return False
    elif original[0] + direction[0] < 0 or original[1] + direction[1] < 0:
        return False
    else:
        return True

def change_position(original, direction):
    """
    Returns a tuple containing the changed position (in the direction of movement)
    """
    return (original[0] + direction[0], original[1] + direction[1])


def get_obj(board, coordinates):
    """
    Returns an object if it is inside the board, otherwise returns empty list
    """
    if inside_board(coordinates, board):
        return board[coordinates[0]][coordinates[1]]
    else:
        return []


class gameObj():
    def __init__(self, value, board, position):
        """
        Initiates a gameObj
        """
        self.properties = set()
        self.value = value
        self.board = board
        self.position = position
        self.moveable = None
        self.toMove = None
    
    def restart_self(self):
        """
        Restarts the moveable properties of an object
        """
        self.moveable = None
        self.toMove = None

    def restart_prop(self):
        """
        Restarts the properties (actions and nouns) of an object
        """
        self.properties = set()

    def is_moveable(self, direction):
        """
        Checks if an object is moveable considering its surroundings
        """
        toTry = change_position(self.position,  direction)
        next_obj = get_obj(self.board, toTry)
        #if the object hasnt been assigned already
        if self.moveable != None:
            pass
        #saves all the objects that will be pushed from subsequent pushes
        potential_push = []
        for obj in next_obj:
            #if the object cant be moved assign it False
            if 'PUSH' not in obj.properties and 'STOP' in obj.properties:
                self.moveable = False
                return
            #finds all objects that could be pushed (if they are moveable)
            elif 'PUSH' in obj.properties:
                potential_push.append(obj)
        #checks that all the moveable objects can be pushed to assign original object 
        self.moveable = inside_board(toTry, self.board) and all(map(lambda obj: obj.is_moveable(direction), potential_push)) 
        return self.moveable

    def will_move(self, direction):
        """
        Checks which objects a moveable object will move in turn 
        and updates their moveable properties.
        """
        next_position = change_position(self.position, direction)
        next_obj = get_obj(self.board, next_position)
        if self.toMove != None:
            pass
        else:
            self.toMove = True
            for obj in next_obj:
                #assignes False if any objects are blocking the way
                if 'STOP' in obj.properties and 'PUSH' not in obj.properties:
                    self.toMove = False
            #if no objects block the way
            if self.toMove:
                #evaluate all objects in following cell
                for obj in next_obj:
                    #recursively evaluate all subsequent push objects
                    if 'PUSH' in obj.properties:
                        obj.will_move(direction)
                #evaluates previous cell
                pull_position = change_position(self.position, (-direction[0], -direction[1]))
                pulled_obj = get_obj(self.board, pull_position)
                for obj in pulled_obj:
                    #recursively evaluates pullable objects
                    if 'PULL' in obj.properties and obj.is_moveable(direction):
                        obj.will_move(direction)
        
def find_rules(game):
    """
    Finds and parses the rules associated with each game
    """
    def search_neighbors(toAssign, nouns, game_board, direction, active, assignment):
        for direct in direction:
            """
            Searches the neighbors of an object in the reading directions recursively
            """
            #finds object at next position
            new_position = change_position(toAssign.position, direct)
            if not inside_board(new_position, game_board):
                continue
            if get_obj(toAssign.board, new_position) != []:
                new_obj = get_obj(toAssign.board, new_position)[0]
                #if next object is "IS" then search recursively and flag activation
                if new_obj.value == 'IS':
                    if inside_board(new_position, toAssign.board, direct) and get_obj(toAssign.board, change_position(new_position, direct)) != [] and get_obj(toAssign.board, change_position(new_position, direct))[0].value in NOT_ALL_WORDS:
                        assignment.append(toAssign)
                        search_neighbors(new_obj, nouns, game_board, [direct], True, assignment)
                #if next object is "IS" then search recursively and keep flaged/not flaged activation
                elif new_obj.value == 'AND':
                        assignment.append(toAssign)
                        search_neighbors(new_obj, nouns, game_board, [direct], active, assignment)
                #if the object has been activated, assign nouns to properties/nouns
                elif assignment != [] and active:
                    for e in assignment:
                        if e.value in NOT_ALL_WORDS:
                            nouns[e.value.lower()].add(new_obj.value)
                #if next object is not valid deactivate
                else:
                    active = False

    objects, game_board = game['objects'], game['board']
    
    #intializes dictionary holding properties/other nouns associated with each noun
    nouns = {val.lower():set() for val in NOUNS}
    for obj in objects:
        if obj.value.isupper():
            #adds object to property dictionary
            if obj.value in PROPERTIES:
                obj.properties.add(obj.value)
            #searches the neighbors of a noun
            elif obj.value in NOUNS:
                search_neighbors(obj, nouns, game_board, [(1, 0), (0, 1)], False, [])

    #assigns each noun the properties associated to it in nouns dic and each property 'PUSH'
    for noun_or_prop in objects:
        if noun_or_prop.value in nouns:
            for props in nouns[noun_or_prop.value]:
                noun_or_prop.properties.add(props)
        elif noun_or_prop.value in WORDS:
            noun_or_prop.properties = {'PUSH'}
    return nouns

def are_nouns(game, nouns):
    """
    Input: noun list from find_rules
    Transforms any objects that have been reassigned in the manner
    SNEK IS ROCK or WALL IS ROCK
    Returns: all objects transformed into their reassignes graphical objects
    """
    for noun in game['objects']:
        if noun.value in nouns:
            for props in nouns[noun.value]:
                if props in NOUNS:
                    noun.value = props.lower()
                    noun.properties = {p if p != props else {} for p in nouns[props.lower()]}
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
    #creates game board replacing string for gameObj objects
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
                    #creates an instance of gameObj for each string to board
                    new_obj = gameObj(obj, board, (r_idx, c_idx))
                    #appends gameObj to board
                    this_level.append(new_obj)
                    #appends all gamObj instances to a list of objects
                    game_objs.append(new_obj)
                new_row.append(this_level)
        board.append(new_row)

    game = {
        'board': board,
        'objects': game_objs
    }

    #initalizes game rules without changing objects 
    find_rules(game)
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

    #restarts moveability in all objects
    for obj in objects:
        obj.restart_self()

    #checks if each object is moveable considering current rules
    for obj in objects:
        if 'YOU' in obj.properties:
            if obj.is_moveable(direction):
                obj.will_move(direction)

    #updates location for each object
    for obj in objects:
        if obj.toMove:
            get_obj(board, obj.position).remove(obj)
            obj.position = change_position(obj.position, direction)
            get_obj(board, obj.position).append(obj)
    
    #restarts properties since rules may have changes
    for obj in objects:
        obj.restart_prop()

    #recalculates rules, reassignes properties and changes nouns
    are_nouns(game, find_rules(game))

    #removes all objects that have been defeated
    toRemove, count = {}, 0
    for obj in objects:
        if 'YOU' in obj.properties:
            if any(map(lambda item: 'DEFEAT' in item.properties, board[obj.position[0]][obj.position[1]])):
                toRemove[(obj.position[0],obj.position[1], count)] = obj
                count += 1
    for key, val in toRemove.items():
        board[key[0]][key[1]].remove(val)
        objects.remove(val)

    #checks if any objects ended up in a winning cell
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

