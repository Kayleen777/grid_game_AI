import time
import numpy as np
from gridgame import *

##############################################################################################################################

# You can visualize what your code is doing by setting the GUI argument in the following line to true.
# The render_delay_sec argument allows you to slow down the animation, to be able to see each step more clearly.

# For your final submission, please set the GUI option to False.

# The gs argument controls the grid size. You should experiment with various sizes to ensure your code generalizes.
# Please do not modify or remove lines 18 and 19.

##############################################################################################################################

game = ShapePlacementGrid(GUI=False, render_delay_sec=0.5, gs=6, num_colored_boxes=5)
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
np.savetxt('initial_grid.txt', grid, fmt="%d")

##############################################################################################################################

# Initialization

# shapePos is the current position of the brush.

# currentShapeIndex is the index of the current brush type being placed (order specified in gridgame.py, and assignment instructions).

# currentColorIndex is the index of the current color being placed (order specified in gridgame.py, and assignment instructions).

# grid represents the current state of the board.

    # -1 indicates an empty cell
    # 0 indicates a cell colored in the first color (indigo by default)
    # 1 indicates a cell colored in the second color (taupe by default)
    # 2 indicates a cell colored in the third color (veridian by default)
    # 3 indicates a cell colored in the fourth color (peach by default)

# placedShapes is a list of shapes that have currently been placed on the board.

    # Each shape is represented as a list containing three elements: a) the brush type (number between 0-8),
    # b) the location of the shape (coordinates of top-left cell of the shape) and c) color of the shape (number between 0-3)

    # For instance [0, (0,0), 2] represents a shape spanning a single cell in the color 2=veridian, placed at the top left cell in the grid.

# done is a Boolean that represents whether coloring constraints are satisfied. Updated by the gridgames.py file.

##############################################################################################################################

shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

print(shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done)

####################################################
# Timing your code's execution for the leaderboard.
####################################################

start = time.time()  # <- do not modify this.

##########################################
# Write all your code in the area below.
##########################################

import random

# There are a lot of helper functions I created as I worked through errors
# but the main part that show case FIRST CHOICE HILL CLIMBING should be at the bottom

# Helper Functions:

# Count all the cells that are not empty.
def num_colored_cells(grid):
    # -1 means empty cell
    return int(np.sum(grid != -1))

# Returns true if there is any orthogonally adjacent pair of cells
# with the same color and ignore empty cells.
def conflict(grid):
    # number of rows (y)
    rows = grid.shape[0]
    # number of cols (x)
    cols = grid.shape[1]

    for y in range(rows):
        for x in range(cols):
            c = grid[y, x]
            if c == -1:
                continue

            # compare with right neighbor
            if x + 1 < cols and grid[y, x + 1] == c:
                return True

            # compare with down neighbor
            if y + 1 < rows and grid[y + 1, x] == c:
                return True
    return False

def colors_used(placedShapes):
    # Count how many different colors are used
    if not placedShapes:
        return 0
    return len({s[2] for s in placedShapes})

def shapes_used(placedShapes):
    # counts how many times a shape is
    return len(placedShapes)

# Find how many trapped cells exist aka empty cell with all 4 neighbor colors used
# This helps prevent reaching states where no legal color that can be placed.
def count_trapped_cells(grid):
    rows, cols = grid.shape
    trapped = 0

    for y in range(rows):
        for x in range(cols):
            if grid[y, x] != -1:
                continue

            neighbors = set()
            for nx, ny in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
                if 0 <= nx < cols and 0 <= ny < rows:
                    c = grid[ny, nx]
                    if c != -1:
                        neighbors.add(c)

            if len(neighbors) == 4:
                trapped += 1

    return trapped

# if it has a conflict make the score negative
# else count the numbers of colored cell and make it the score
def score(grid, placedShapes, done):
    # Hard reject any conflicting grid
    if conflict(grid):
        return -1000000000000

    colored = num_colored_cells(grid)
    shapes = shapes_used(placedShapes)
    colors = colors_used(placedShapes)

    # Penalize trapped cells 
    traps = count_trapped_cells(grid)

    # Big points for completion! Search strongly for reaching done=True
    if done:
        done_perf = 1000000000
    else:
        done_perf = 0

    # Penalize colors and shapes
    # done_bonus is best state, then coverage, then shapes, then colors, then traps.
    return (
        done_perf
        + colored * 10000000
        - traps * 500000000
        - colors * 100000
        - shapes * 100
    )

# Move brush from current shapePos to (x, y)
def move_brush(game, x, y):
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

    shape_w, shape_h = game.shapesDims[currentShapeIndex]
    max_x = grid.shape[1] - shape_w
    max_y = grid.shape[0] - shape_h
    x = max(0, min(x, max_x))
    y = max(0, min(y, max_y))

    while shapePos[0] < x:
        ogPos = shapePos[0]
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('right')
        if shapePos[0] == ogPos:
            break

    while shapePos[0] > x:
        ogPos = shapePos[0]
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('left')
        if shapePos[0] == ogPos:
            break

    while shapePos[1] < y:
        ogPos = shapePos[1]
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('down')
        if shapePos[1] == ogPos:
            break

    while shapePos[1] > y:
        ogPos = shapePos[1]
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('up')
        if shapePos[1] == ogPos:
            break

    return game.execute('export')

# Cycle through until we get the desired shape index
def set_shape(game, shape):
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
    while currentShapeIndex != shape:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('switchshape')
    return game.execute('export')

# Cycle through until we get the desired color index
def set_color(game, color):
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
    while currentColorIndex != color:
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('switchcolor')
    return game.execute('export')

# Finds all grid (x,y) cells that would be painted by shape at pos
def shape_cells(shape, pos):
    color_cells = []
    h, w = shape.shape
    for y in range(h):
        for x in range(w):
            if shape[y, x] == 1:
                color_cells.append((pos[0] + x, pos[1] + y))
    return color_cells

# Finds colors that can not be used for this shape placement due to conflict
def illegal_placement(grid, shape, pos):
    rows, cols = grid.shape
    no_color = set()
    # for every grid cell that the shape would paint
    for (x, y) in shape_cells(shape, pos):
        # check four orthogonal neighbors
        for (nx, ny) in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
            # check sure neighbor is inside grid bounds
            if 0 <= nx < cols and 0 <= ny < rows:
                c = grid[ny, nx]
                # ignore empty cells
                if c != -1:
                    no_color.add(c)
    return no_color

# Returns a list of valid colors that can be used to place
# this shape at this position without causing conflicts.
def available_colors(grid, shape, pos, num_colors=4):
    no_color = illegal_placement(grid, shape, pos)
    return [c for c in range(num_colors) if c not in no_color]

# Find a empty cell close to becoming trapped cells with 3 adjacent colors
def find_dangerous_cell(grid):
    rows, cols = grid.shape
    for y in range(rows):
        for x in range(cols):
            if grid[y, x] == -1:
                neighbors = set()
                for nx, ny in [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]:
                    if 0 <= nx < cols and 0 <= ny < rows and grid[ny, nx] != -1:
                        neighbors.add(grid[ny, nx])
                # 3 colors used = dangerous, only 1 valid color left
                if len(neighbors) == 3:
                    avail_color = [c for c in range(4) if c not in neighbors]
                    return (x, y, avail_color[0] if avail_color else None)
    return None

# Beginning of main code using helpers

# Get the current state without any change
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

# find score of current with score(grid, placedShapes, done)
current_score = score(grid, placedShapes, done)

rows = grid.shape[0]
cols = grid.shape[1]

# Maximum tries so it doesn't loop forever
max_attempts = 200000

for step in range(max_attempts):
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
    if done:
        break

    # Handle dangerous cells when coming up with new candidate.
    dangerous = find_dangerous_cell(grid)

    forced_color = None

    if dangerous:
        # Pick a dangerous cell and try to fill it with its only available color
        dx, dy, only_color = dangerous
        if only_color is not None:
            new_shape = 0
            new_x, new_y = dx, dy
            forced_color = only_color
        else:
            # go to normal random color
            forced_color = None

    if dangerous is None or forced_color is None:
        empty = int(np.sum(grid == -1))
        total = rows * cols
        fill = 1 - (empty / total)

        # brush buckets
        small  = [0, 1, 2]
        medium = [3, 7, 8]
        large  = [4, 5, 6]

        # finish gaps with single cell
        if empty <= max(6, total // 60):
            new_shape = 0
            empties = np.argwhere(grid == -1)
            ay, ax = random.choice(empties)
            new_x, new_y = int(ax), int(ay)
        else:
            # bigger grid bigger brush
            if total >= 225 and fill < 0.35:
                choices, weights = large + medium + small, [6,6,6, 3,3,3, 1,1,1]
            elif fill < 0.70:
                choices, weights = medium + large + small, [5,5,5, 3,3,3, 1,1,1]
            else:
                choices, weights = small + medium + large, [6,6,6, 2,2,2, 1,1,1]

            new_shape = random.choices(choices, weights=weights, k=1)[0]
            shape_w, shape_h = game.shapesDims[new_shape]
            new_x = random.randint(0, cols - shape_w)
            new_y = random.randint(0, rows - shape_h)

    # set the new shape first so movement limits match the shape
    set_shape(game, new_shape)

    # Move brush to new position
    move_brush(game, new_x, new_y)

    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

    # find a color available for the new position
    shape = game.shapes[new_shape]
    pos = shapePos
    avail = available_colors(grid, shape, pos, num_colors=4)
    if not avail:
        continue

    # If handling a dangerous cell, force the only legal color
    if forced_color is not None:
        if forced_color not in avail:
            continue
        new_color = forced_color
    else:
        new_color = random.choice(avail)

    # Switch brush color until reached new_color
    set_color(game, new_color)

    # Get new state after changing
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

    # Check for no overlap
    if not game.canPlace(grid, game.shapes[currentShapeIndex], shapePos):
        continue

    before_score = current_score

    # Try placing the shape
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('place')
    shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')

    new_score = score(grid, placedShapes, done)

    # FIST CHOICE HILL CLIMBING:
    # keep the move only if it improves the score
    if new_score > before_score:
        current_score = new_score
    else:
        game.execute('undo')
        shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
        current_score = score(grid, placedShapes, done)

# Final export so it ends with the final best state
shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done = game.execute('export')
print(grid)

########################################
# Do not modify any of the code below.
########################################

end = time.time()

np.savetxt('grid.txt', grid, fmt="%d")
with open("shapes.txt", "w") as outfile:
    outfile.write(str(placedShapes))
with open("time.txt", "w") as outfile:
    outfile.write(str(end - start))