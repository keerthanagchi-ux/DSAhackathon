import random
import csv
import time
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.animation import FuncAnimation
from collections import deque

# ==========================================
# STEP 1: GENERATE A RANDOM, SOLVABLE MAZE
# ==========================================

def generate_maze(T):
    n = max(10, 3 * T + 4)

    grid = [['#' for _ in range(n)] for _ in range(n)]

    # Create a guaranteed route that zigzags
    # through different rows and columns.
    path = []

    for r in range(n):
        if r % 2 == 0:
            cols = range(n) if (r // 2) % 2 == 0 else range(n - 1, -1, -1)

            for c in cols:
                path.append((r, c))

        else:
            # Connect consecutive rows at alternating ends.
            previous_end = path[-1][1]
            path.append((r, previous_end))

    # Open every cell along the guaranteed route.
    for r, c in path:
        grid[r][c] = '.'

    # Place start and exit on the route.
    start = path[0]
    end = path[-1]

    grid[start[0]][start[1]] = 'S'
    grid[end[0]][end[1]] = 'E'

    # Select positions along the route, excluding S and E.
    available = path[1:-1]

    # Spread keys and doors across the route.
    # Keys appear before their matching doors.
    required = 2 * T

    if len(available) < required:
        raise ValueError("Maze is too small for the requested keys and doors.")

    # Pick well-spaced route positions.
    indices = [
        round(i * (len(available) - 1) / (required - 1))
        for i in range(required)
    ] if required > 1 else [0]

    selected = [available[i] for i in indices]

    # Place all keys first, then their matching doors.
    for i in range(T):
        r, c = selected[i]
        grid[r][c] = chr(ord('a') + i)

    for i in range(T):
        r, c = selected[T + i]
        grid[r][c] = chr(ord('A') + i)

    # Add random open spaces away from the guaranteed route.
    route_set = set(path)

    for r in range(n):
        for c in range(n):
            if (r, c) not in route_set and random.random() < 0.30:
                grid[r][c] = '.'

    return grid
# ==========================================
# STEP 2: SAVE THE ORIGINAL MAZE AS CSV
# ==========================================

def save_input_csv(grid):
    with open("maze_input.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(grid)

    print("Original maze saved to maze_input.csv")


# ==========================================
# STEP 3: FIND SHORTEST PATH USING BFS
# ==========================================

def shortest_path(grid):
    n = len(grid)
    start = None
    end = None

    for r in range(n):
        for c in range(n):
            if grid[r][c] == 'S':
                start = (r, c)
            elif grid[r][c] == 'E':
                end = (r, c)

    if start is None or end is None:
        return -1, []

    # Each state includes position and collected keys
    queue = deque([(start[0], start[1], 0, 0)])

    visited = {(start[0], start[1], 0)}

    parent = {
        (start[0], start[1], 0): None
    }

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    while queue:
        r, c, keys, dist = queue.popleft()

        state = (r, c, keys)

        # Exit reached
        if (r, c) == end:
            path = []

            while state is not None:
                path.append((state[0], state[1], state[2]))
                state = parent[state]

            path.reverse()

            return dist, path

        for dr, dc in directions:
            nr = r + dr
            nc = c + dc

            if not (0 <= nr < n and 0 <= nc < n):
                continue

            cell = grid[nr][nc]

            # Wall
            if cell == '#':
                continue

            new_keys = keys

            # Pick up key
            if 'a' <= cell <= 'f':
                bit = 1 << (ord(cell) - ord('a'))
                new_keys |= bit

            # Check whether matching key is available
            if 'A' <= cell <= 'F':
                bit = 1 << (ord(cell) - ord('A'))

                if not (keys & bit):
                    continue

            new_state = (nr, nc, new_keys)

            if new_state not in visited:
                visited.add(new_state)

                parent[new_state] = (r, c, keys)

                queue.append(
                    (nr, nc, new_keys, dist + 1)
                )

    return -1, []


# ==========================================
# STEP 4: SAVE THE SOLUTION AS CSV
# ==========================================

def save_solution_csv(grid, path):
    result = [row[:] for row in grid]

    for r, c, keys in path:
        if result[r][c] == '.':
            result[r][c] = 'x'

    with open("maze_solution.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(result)

    print("Solved maze saved to maze_solution.csv")


# ==========================================
# STEP 5: DISPLAY THE MAZE
# ==========================================

def display_maze(grid):
    n = len(grid)

    # Assign numerical values to maze cells
    colors = {
        '.': 0,
        '#': 1,
        'S': 2,
        'E': 3,
        'a': 4,
        'A': 4,
        'b': 5,
        'B': 5,
        'c': 6,
        'C': 6,
        'd': 7,
        'D': 7,
        'e': 8,
        'E': 8,
        'f': 9,
        'F': 9,
        'x': 10
    }

    # The exit symbol E must remain distinct from a key colour.
    # Store the exit as its own numerical category.
    colors['E'] = 3

    cmap = ListedColormap([
        'white',       # Open cell
        'black',       # Wall
        'green',       # Start
        'red',         # Exit
        'yellow',      # Key/door pair a/A
        'orange',      # Key/door pair b/B
        'cyan',        # Key/door pair c/C
        'magenta',     # Key/door pair d/D
        'purple',      # Key/door pair e/E
        'brown',       # Key/door pair f/F
        'deepskyblue'  # Path
    ])

    matrix = [
        [colors[cell] for cell in row]
        for row in grid
    ]

    fig, ax = plt.subplots(figsize=(8, 8))

    ax.imshow(
        matrix,
        cmap=cmap,
        vmin=0,
        vmax=10
    )

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks(
        [i - 0.5 for i in range(1, n)],
        minor=True
    )
    ax.set_yticks(
        [i - 0.5 for i in range(1, n)],
        minor=True
    )
    ax.grid(which='minor', color='gray', linewidth=0.5)

    for r in range(n):
        for c in range(n):
            ax.text(
                c, r, grid[r][c],
                ha='center',
                va='center',
                color='white' if grid[r][c] == '#' else 'black',
                fontsize=12,
                fontweight='bold'
            )

    ax.set_title("Generated Maze")
    plt.tight_layout()
    plt.show()



# ==========================================
# STEP 6: ANIMATE THE SOLUTION - FIXED
# ==========================================

def animate_solution(grid, path):
    if not path:
        print("No path available to animate.")
        return

    n = len(grid)

    pair_colors = {
        'a': 4, 'A': 4,
        'b': 5, 'B': 5,
        'c': 6, 'C': 6,
        'd': 7, 'D': 7,
        'e': 8, 'E': 8,
        'f': 9, 'F': 9
    }

    cmap = ListedColormap([
        'white',       # 0: Open cell
        'black',       # 1: Wall
        'green',       # 2: Start
        'red',         # 3: Exit
        'yellow',      # 4: Key/door a/A
        'orange',      # 5: Key/door b/B
        'cyan',        # 6: Key/door c/C
        'magenta',     # 7: Key/door d/D
        'purple',      # 8: Key/door e/E
        'brown',       # 9: Key/door f/F
        'deepskyblue', # 10: Visited path/current position
        'lightgray'    # 11: Unlocked door
    ])

    def cell_value(cell):
        if cell == '.':
            return 0
        elif cell == '#':
            return 1
        elif cell == 'S':
            return 2
        elif cell == 'E':
            return 3
        return pair_colors.get(cell, 0)

    # Create the visualization window
    plt.ion()
    fig, ax = plt.subplots(figsize=(9, 9))

    inventory = set()
    collected = set()
    opened = set()
    travelled = set()

    total_steps = len(path)

    # Display each position in the solution one at a time
    for step, (r, c, keys) in enumerate(path, start=1):

        cell = grid[r][c]

        # Collect keys
        if 'a' <= cell <= 'f':
            inventory.add(cell)
            collected.add((r, c))

        # Unlock doors
        if 'A' <= cell <= 'F':
            opened.add((r, c))

        # Remember visited cells
        travelled.add((r, c))

        matrix = []

        for i in range(n):
            row_values = []

            for j in range(n):
                current_cell = grid[i][j]

                if (i, j) == (r, c):
                    value = 10
                elif (i, j) in travelled:
                    if current_cell in ('S', 'E'):
                        value = cell_value(current_cell)
                    elif current_cell == '#':
                        value = 1
                    elif 'A' <= current_cell <= 'F' and (
                        (i, j) in opened
                    ):
                        value = 11
                    else:
                        value = 10
                else:
                    value = cell_value(current_cell)

                row_values.append(value)

            matrix.append(row_values)

        # Redraw the maze for this movement step
        ax.clear()

        ax.imshow(
            matrix,
            cmap=cmap,
            vmin=0,
            vmax=11,
            interpolation='nearest'
        )

        # Draw grid lines
        ax.set_xticks(
            [i - 0.5 for i in range(1, n)],
            minor=True
        )
        ax.set_yticks(
            [i - 0.5 for i in range(1, n)],
            minor=True
        )
        ax.grid(
            which='minor',
            color='gray',
            linewidth=0.5
        )

        # Display cell symbols
        for i in range(n):
            for j in range(n):
                original = grid[i][j]

                if (i, j) == (r, c):
                    label = '@'
                elif 'a' <= original <= 'f' and (
                    (i, j) in collected
                ):
                    label = original
                elif 'A' <= original <= 'F' and (
                    (i, j) in opened
                ):
                    label = '✓'
                elif (i, j) in travelled and original == '.':
                    label = 'x'
                else:
                    label = original

                if label:
                    ax.text(
                        j, i, label,
                        ha='center',
                        va='center',
                        fontsize=11,
                        fontweight='bold',
                        color=(
                            'white'
                            if original == '#'
                            else 'black'
                        )
                    )

        ax.set_title(
            f"Shortest Path Animation\n"
            f"Movement: {step - 1}/{total_steps - 1} | "
            f"Position: ({r}, {c})\n"
            f"Keys collected: "
            f"{', '.join(sorted(inventory)) or 'None'}",
            fontsize=12
        )

        ax.set_xticks([])
        ax.set_yticks([])

        fig.tight_layout()

        # Force the window to redraw and wait before moving
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.7)

    plt.ioff()

    ax.set_title("Maze Solved! Exit Reached.")
    fig.canvas.draw_idle()
    plt.show()



# ==========================================
# STEP 7: MAIN PROGRAM
# ==========================================

def main():
    T = int(input("Enter number of key/door types (1-6): "))

    if not 1 <= T <= 6:
        print("Invalid input. T must be between 1 and 6.")
        return

    print("\nStep 1: Generating maze...")

    grid = generate_maze(T)

    for row in grid:
        print(" ".join(row))

    print("\nStep 2: Saving input maze...")
    save_input_csv(grid)

    print("\nStep 3: Finding shortest path using BFS...")

    distance, path = shortest_path(grid)

    print("\nShortest path length:", distance)

    if distance == -1:
        print("No solution exists.")
        return

    print("\nStep 4: Saving solved maze...")
    save_solution_csv(grid, path)

    print("\nStep 5: Displaying original maze...")
    display_maze(grid)

    print("\nStep 6: Animating shortest path...")
    animate_solution(grid, path)

    print("\nAll steps completed!")


if __name__ == "__main__":
    main()