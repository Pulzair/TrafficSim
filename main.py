import random
import time

def read_grid(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        grid = [list(line.strip()) for line in lines]
    return grid

def print_grid(grid):
    for row in grid:
        print(' '.join(row))