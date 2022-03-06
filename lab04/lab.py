#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION
def create_board_and_visible(num_rows, num_cols, bombs):
    """
    Create a readable representaion of the board and the visible cells.
    Inputs: num_rows (integer of rows), num_cols(integer of columns), bombs(list of tuple(coordinates))
    Output: board (list of lists), visible (list of lists)
    """
    board, visible = [], []
    set_bombs = set(bombs)
    for row in range(num_rows):
        append_row = []
        visible_row = []
        for col in range(num_cols):
            visible_row.append(False)
            if (row, col) in set_bombs:
                append_row.append('.')
            else:
                append_row.append(0)
        board.append(append_row)
        visible.append(visible_row)
    return board, visible


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    board, visible = create_board_and_visible(num_rows, num_cols, bombs)

    for r in range(num_rows):
        for c in range(num_cols):
            neighbor_bombs = 0
            neighbor_coords = ((r-1, r, r+1), (c-1, c, c+1))
            for row in neighbor_coords[0]:
                for col in neighbor_coords[1]:
                    if 0 <= row < num_rows and 0 <= col < num_cols:
                        if board[row][col] == '.':
                            neighbor_bombs += 1
            if board[r][c]=='.':
                next
            else:
                board[r][c] = neighbor_bombs
    return {
        'dimensions': (num_rows, num_cols),
        'board': board,
        'visible': visible,
        'state': 'ongoing'}

def bombs_and_covered_squares(game):
    """
    Write docstring
    """
    num_rows, num_cols = game['dimensions'] 
    state = 'ongoing'
    covered_squares = 0
    for r in range(num_rows):
        for c in range(num_cols):
            if game['board'][r][c] == '.':
                if game['visible'][r][c] == True:
                    return 'defeat'
            elif game['visible'][r][c] == False:
                covered_squares += 1
    if covered_squares == 0:
        state = 'victory'
    return state

def valid_square(game, n_row, n_col):
    """
    Write docstring
    """
    num_rows, num_cols = game['dimensions'] 
    if 0 <= n_row < num_rows and 0 <= n_col < num_cols:
        if game['board'][n_row][n_col] != '.' and game['visible'][n_row][n_col] == False:
            return dig_2d(game, n_row, n_col)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    game['state'] = bombs_and_covered_squares(game)

    if game['state'] == 'victory' or game['state'] == 'defeat':
        return 0

    if game['board'][row][col] == '.':
        game['visible'][row][col] = True
        game['state'] = 'defeat'
        return 1
  
    if game['visible'][row][col] != True:
        game['visible'][row][col] = True
        revealed = 1

    else:
        return 0

    if game['board'][row][col] == 0:
        neighbor_coords = ((row-1, row, row+1), (col-1, col, col+1))
        for r in range(3):
            for c in range(3):
                valid = valid_square(game, neighbor_coords[0][r], neighbor_coords[1][c])
                if valid is None:
                    continue
                else:
                    revealed += valid

    state = bombs_and_covered_squares(game)
    if state != 'defeat':
        game['state'] = state
        return revealed

def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    dump_rep = game.copy()
    dump_rep['board'] = [[str(e)  if e != 0 else ' ' for e in dump_rep['board'][i]] for i in range(len(dump_rep['board']))]
    if xray:
        return dump_rep['board']
    return [[dump_rep['board'][row][col] if dump_rep['visible'][row][col] == True else '_' for col in range(dump_rep['dimensions'][1])]for row in range(dump_rep['dimensions'][0])]




def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    list_locations = render_2d_locations(game, xray)
    str = []
    for row in range(len(list_locations)):
        for col in range(len(list_locations[0])):
            str.append(list_locations[row][col])
        if row != len(list_locations) - 1:
            str.append('\n')
    return ''.join(str)


# N-D IMPLEMENTATION

def create_array(dimensions, value):
    """
    Creates a multi-dimensional array
    """
    if len(dimensions) == 1:
        return [value for i in range(dimensions[0])]
    else:
        return [create_array(dimensions[1:], value) for j in range(dimensions[0])]


def all_coords(dimensions):
    def iterate(dimensions, j, dim={}):
        if j < len(dimensions):
            dim[j] = []
            for i in range(dimensions[j]):
                dim[j] += [i]
            return iterate(dimensions, j+1, dim)
        else:
            return dim
    total_possible =  iterate(dimensions, 0)
    possible = list(total_possible.values())
    def permute(possible, coords = [], sol=[]):
        if len(possible)==0:
           sol.append(tuple(coords))
           return
        for e in possible[0]:
            permute(possible[1:], coords + [e])
        return sol
    return permute(possible)

def get_val(array, coords):
    if len(coords)== 1:
        val = array[coords[0]]
        return val
    else:
        return get_val(array[coords[0]], coords[1:])

def check_game_state(visited, dimensions, bombs):
    """
    Checks the state of the game.
    """
    squares = 1
    for e in dimensions:
        squares *= e
    if visited == squares - bombs:
        return True
    return False

def change_val(array, coord, val):
    if len(coord)== 1:
        index = coord[0]
        array[index] = val
    else:
        new_coords = coord[1:]
        change_val(array[coord[0]], new_coords, val)

def find_neighbors(board, dimensions, coords):
    changeVars = (-1, 0, 1)
    neighbors = []
    def recursive_func(board, coords, dimensions, i=0):
        if i == len(coords) - 1:
            for change in changeVars:
                possible_neighbor = list(coords[:i]) + [ coords[i]+change ] + list(coords[i+1:])
                if 0 <= possible_neighbor[i] < dimensions[i]:
                    neighbors.append(tuple(possible_neighbor))
        else:
            for change in changeVars:
                possible_neighbor = list(coords[:i]) + [ coords[i]+change ] + list(coords[i+1:])
                if 0 <= possible_neighbor[i] < dimensions[i]:
                    recursive_func(board, possible_neighbor, dimensions, i+1)
    recursive_func(board, coords, dimensions)
    return set(neighbors)
        


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    bombs: 3
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    board = create_array(dimensions, 0)
    visible = create_array(dimensions, False)
    for e in bombs:
        change_val(board, e, '.')
        neighbors = find_neighbors(board, dimensions, e)
        # print('neighbors ', neighbors)
        # print('neigbor values', neighboring_values)
        for e in neighbors:
            if get_val(board, e) != '.':
                change_val(board, e, get_val(board, e)+1)
    return {'board':board, 'dimensions': dimensions, 'state': 'ongoing', 'visible': visible, 'bombs': len(bombs)}


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'bombs': 3,
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    bombs: 3
    dimensions: (2, 4, 2)
    revealed: 8
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'bombs': 3,
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    bombs: 3
    dimensions: (2, 4, 2)
    revealed: 1
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    if game.get('revealed', None) == None:
        game['revealed'] = 0

    # game['state'] = check_game_state(game['revealed'], game['dimensions'], game['bombs'])

    if game['state'] == 'victory' or game['state'] == 'defeat':
        return 0

    if get_val(game['board'], coordinates) == '.':
        change_val(game['visible'], coordinates, True)
        game['state'] = 'defeat'
        game['revealed'] += 1
        return 1

    if get_val(game['visible'], coordinates):
        return 0

    queue = [coordinates]
    visited = set()
    visited.add(tuple(coordinates))
    while len(queue) != 0:
        f_coords = queue.pop(0)
        change_val(game['visible'], f_coords, True)
        if get_val(game['board'], f_coords) == 0:
            for neighbor in find_neighbors(game['board'], game['dimensions'], f_coords):
                if tuple(neighbor) not in visited and not get_val(game['visible'], neighbor):
                    visited.add(tuple(neighbor))
                    if get_val(game['board'], neighbor) == 0:
                        queue.append(neighbor)
                    else:
                        change_val(game['visible'], neighbor, True)
        else:
            break
          
    game['revealed'] += len(visited)
    if check_game_state(game['revealed'], game['dimensions'], game['bombs']):
        game['state'] = 'victory'
    else:
        game['state'] = 'ongoing'
    return len(visited)


def display_game(game, board, coords, dimensions, i, bool):
    if len(coords) - 1 == i:
        for curr_index in range(dimensions[i]):
            coords = coords[:i] + [curr_index] + coords[i+1:]
            past_val = get_val(game['board'], coords)
            if past_val == 0:
                new_val = ' '
            else:
                new_val = str(past_val)
            if bool:
                change_val(board, coords, new_val)
            else:
                if get_val(game['visible'], coords):
                    change_val(board, coords, new_val)
    else:
        for curr_index in range(game['dimensions'][i]):
            coords = coords[:i] + [curr_index] + coords[i+1:]
            display_game(game, board, coords, dimensions, i+1, bool)
    return board

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """


    iterable = create_array(game['dimensions'], '_')

    display_game(game, iterable, list(game['dimensions']).copy(), game['dimensions'], 0, xray)

    return iterable



if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests
    # print(create_array([2, 3, 4], 0))
    # twod = {'board': [['.', 3, 1, 0], ['.', '.', 1, 0]], 'dimensions': [2, 4], 'state': 'defeat', 'visible':
    #     [[False, True, False, True], [False, False, True, True]]}
    # threed = [[[[1, 1], ['.', 2], [2, 2]], [[1, 1], [2, 2], ['.', 2]],
    #          [[1, 1], [2, 2], [1, 1]], [[1, '.'], [1, 1], [0, 0]]]]
    # g = {'dimensions': (2, 4, 2),
    #       'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    #                 [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    #       'visible': [[[False, False], [False, True], [False, False],
    #                 [False, False]],
    #                [[False, False], [False, False], [False, False],
    #                 [False, False]]],
    #       'state': 'ongoing'}
    # print(dig_nd(g, (0, 3, 0)))
    # g = {'dimensions': (2, 4, 2),
    #       'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    #                 [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    #       'visible': [[[False, False], [False, True], [False, False],
    #                 [False, False]],
    #                [[False, False], [False, False], [False, False],
    #                 [False, False]]],
    #       'state': 'ongoing'}
    # dig_nd(g, (0, 0, 1))
    # dump(g)
    # change_value(threed, [[0, 1, 0], [1, 0, 0], [1, 1, 1]], 8)
    # print(threed)
    # print(find_neighbors(threed, (2, 4, 2), (0, 2, 1)))
    # print(all_coords((2, 3, 4)))

    # print(render_2d_locations({'dimensions': (2, 4), 
    #          'state': 'ongoing',
    #          'board': [['.', 3, 1, 0],
    #                    ['.', '.', 1, 0]],
    #          'visible':  [[False, True, False, True],
    #                    [False, False, False, True]]}, False))
    # [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    # game = {'dimensions': (2, 4),
    #          'board': [['.', 3, 1, 0],
    #                    ['.', '.', 1, 0]],
    #          'visible': [[False, True, False, False],
    #                   [False, False, False, False]],
    #          'state': 'ongoing'}
    # print(dig_2d(game, 0, 3))
    # dump(game)

    # g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    # dump(g)

    # print(all_coords([2, 4, 2]))
    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
