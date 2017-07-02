import itertools

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    """
    Return list formed by all the possible concatenations
    of a letter s in string a with a letter t in string b
    """
    return [s+t for s in a for t in b]

# create labels of the boxes and units
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
# Element example:
# row_units[0] = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9']
# This is the top most row.

column_units = [cross(rows, c) for c in cols]
# Element example:
# column_units[0] = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1']
# This is the left most column

square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Element example:
# square_units[0] = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
# This is the top left square.

diag_units = [[r+c for r, c in zip(rows, cols)],
              [r+c for r, c in zip(rows, cols[::-1])]]
# Element example:
# diag_units[0] = ['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9']
# This is the diagonal going from top left box to down right box.

unitlist = row_units + column_units + square_units

# for each box find units the box belongs to
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)

# for each box find the box's peers - all other boxes
# that belong to a common unit
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def grid_values(grid):
    """Convert grid string into {<box>: <value>} dict with '.' value for empties.

    Args:
        grid: Sudoku grid in string form, 81 characters long
    Returns:
        Sudoku grid in dictionary form:
        - keys: Box labels, e.g. 'A1'
        - values: Value in corresponding box, e.g. '8', or '.' if it is empty.
    """
    values = []
    all_digits = '123456789'

    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
    return dict(zip(boxes, values))

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                if len(values[dplaces[0]]) > 1:
                    values[dplaces[0]] = digit
                    #display(values)
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of possible naked twins and triplets
    for n_twins in (2, 3):
        possible_twins = {}

        for box, possible_values in values.items():
            if len(possible_values) == n_twins:
                possible_twins.setdefault(possible_values, []).append(box)
        #print(possible_twins)

        # remove possible_values that belong to too few boxes
        possible_twins = { twin_digits : boxes
                           for twin_digits, boxes in possible_twins.items()
                           if len(boxes) >= n_twins}
        #print(possible_twins)
        #display(values)
        # Eliminate the naked twins as possibilities for their peers
   
        for twin_digits, twin_boxes in possible_twins.items():
            # check there are 2 or 3 boxes with the same twin_digits in the same unit
            for unit in unitlist:
                for comb in itertools.combinations(twin_boxes, n_twins):
                    if set(comb).issubset(set(unit)) == True:
                        #print(comb, 'belong to unit', unit)
                        # exclude twin_boxes' values from values of other boxes in the unit
                        for digit in twin_digits:
                            for box in unit:
                                if box not in comb:
                                    values[box] = values[box].replace(digit, '')
        #display(values)
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy
        #print("solved_values_before:", solved_values_before)
        vales = eliminate(values)
        #print("After applying elimination")
        #display(values)

        # Use the Only Choice Strategy
        values = only_choice(values)
        #print("After applying only_choice")
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        #print("solved_values_after:", solved_values_after)
        #display(values)

        # Use the Naked Twins Strategy
        values = naked_twins(values)
        #print("After applying naked_twins")
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        #print("solved_values_after:", solved_values_after)
        #display(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)
