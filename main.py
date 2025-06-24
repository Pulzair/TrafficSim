import random
import time

def read_grid(filename):
    with open(filename, 'r') as file:
        grid = []
        for line in file:
            row = line.strip().split()
            grid.append(row)
    return grid

def print_grid(grid):    
    for row in grid:
        print(' '.join(row))
    print("-" * 40)

class TrafficLight:
    def __init__(self, grid, x, y, direction='NS'):
        self.grid = grid
        self.x = x
        self.y = y
        self.direction = direction  
        self.state = 'R' if direction == 'NS' else 'G'
        self.timer = 0
        self.green_time = 8
        self.yellow_time = 2
        self.red_time = 10
        
    def update(self):
        self.timer += 1
        if self.state == 'G' and self.timer >= self.green_time:
            self.state = 'Y'
            self.timer = 0
        elif self.state == 'Y' and self.timer >= self.yellow_time:
            self.state = 'R'
            self.timer = 0
        elif self.state == 'R' and self.timer >= self.red_time:
            self.state = 'G'
            self.timer = 0
        self.grid[self.x][self.y] = self.state

class Car:
    def __init__(self, grid, x, y, direction):
        self.grid = grid
        self.x = x
        self.y = y
        self.direction = direction  
        self.stopped = False
        self.last_position = '.'
        
    def can_move(self, new_x, new_y):
        if new_x < 0 or new_x >= len(self.grid) or new_y < 0 or new_y >= len(self.grid[0]):
            return False
        cell = self.grid[new_x][new_y]
        if cell == '#':
            return False
        if cell == 'C':
            return False
        if cell in ['R', 'Y']:
            return False
        return True
    
    def move(self):
        directions = {
            'N': (-1, 0),
            'S': (1, 0),
            'E': (0, 1),
            'W': (0, -1)
        }
        
        dx, dy = directions[self.direction]
        new_x, new_y = self.x + dx, self.y + dy
        
        if self.can_move(new_x, new_y):
            self.grid[self.x][self.y] = self.last_position
            self.x, self.y = new_x, new_y
            self.last_position = self.grid[self.x][self.y]
            self.grid[self.x][self.y] = 'C'
            self.stopped = False
            return True
        else:
            self.stopped = True
            return False
    
    def is_out_of_bounds(self):
        return (self.x < 0 or self.x >= len(self.grid) or 
                self.y < 0 or self.y >= len(self.grid[0]))

class Pedestrian:
    def __init__(self, grid, x, y, target_x, target_y):
        self.grid = grid
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.last_position = '.'
        
    def move(self):
        if self.x == self.target_x and self.y == self.target_y:
            return False  
        dx = 0 if self.x == self.target_x else (1 if self.target_x > self.x else -1)
        dy = 0 if self.y == self.target_y else (1 if self.target_y > self.y else -1)
        
        new_x, new_y = self.x + dx, self.y + dy

        if (0 <= new_x < len(self.grid) and 0 <= new_y < len(self.grid[0]) and
            self.grid[new_x][new_y] not in ['#', 'C']):
            
            self.last_position = self.grid[self.x][self.y]
            if self.grid[self.x][self.y] == 'P':
                self.grid[self.x][self.y] = self.last_position
            
            self.x, self.y = new_x, new_y

            if self.grid[self.x][self.y] in ['.', 'X']:
                self.grid[self.x][self.y] = 'P'
                
        return True

class TrafficSimulator:
    def __init__(self, grid_file='simin.txt'):
        self.grid = read_grid(grid_file)
        self.traffic_lights = []
        self.cars = []
        self.pedestrians = []
        self.tick_count = 0
        
        self.setup_traffic_lights()
        
    def setup_traffic_lights(self):
        height, width = len(self.grid), len(self.grid[0])
        for i in range(height):
            for j in range(width):
                if self.grid[i][j] in ['R', 'G', 'Y']:
                    direction = 'NS' if j == 7 else 'EW'  
                    light = TrafficLight(self.grid, i, j, direction)
                    self.traffic_lights.append(light)
    
    def spawn_car(self):
        if random.random() < 0.3: 
            edges = []
            height, width = len(self.grid), len(self.grid[0])

            for i in range(height):
                if self.grid[i][0] == '.':
                    edges.append((i, 0, 'E'))
                if self.grid[i][width-1] == '.':
                    edges.append((i, width-1, 'W'))
            
            for j in range(width):
                if self.grid[0][j] == '.':
                    edges.append((0, j, 'S'))
                if self.grid[height-1][j] == '.':
                    edges.append((height-1, j, 'N'))
            
            if edges:
                x, y, direction = random.choice(edges)
                if self.grid[x][y] == '.':  
                    car = Car(self.grid, x, y, direction)
                    self.grid[x][y] = 'C'
                    self.cars.append(car)
    
    def spawn_pedestrian(self):
        if random.random() < 0.2:  
            height, width = len(self.grid), len(self.grid[0])

            sidewalks = []
            for i in range(1, height-1):
                for j in range(1, width-1):
                    if (self.grid[i][j] == '#' and 
                        any(self.grid[i+di][j+dj] == '.' 
                            for di, dj in [(-1,0), (1,0), (0,-1), (0,1)])):
                        sidewalks.append((i, j))
            
            if len(sidewalks) >= 2:
                start = random.choice(sidewalks)
                target = random.choice(sidewalks)
                
                if start != target:
                    self.grid[start[0]][start[1]] = 'P'
                    pedestrian = Pedestrian(self.grid, start[0], start[1], 
                                          target[0], target[1])
                    self.pedestrians.append(pedestrian)
    
    def update_traffic_lights(self):
        for light in self.traffic_lights:
            light.update()
    
    def update_cars(self):
        cars_to_remove = []
        
        for i, car in enumerate(self.cars):
            if not car.move() or car.is_out_of_bounds():
                if car.is_out_of_bounds():
                    cars_to_remove.append(i)

        for i in reversed(cars_to_remove):
            self.cars.pop(i)
    
    def update_pedestrians(self):
        pedestrians_to_remove = []
        
        for i, pedestrian in enumerate(self.pedestrians):
            if not pedestrian.move():
                if self.grid[pedestrian.x][pedestrian.y] == 'P':
                    self.grid[pedestrian.x][pedestrian.y] = '.'
                pedestrians_to_remove.append(i)

        for i in reversed(pedestrians_to_remove):
            self.pedestrians.pop(i)
    
    def run_simulation(self, ticks):
        print(f"Starting traffic simulation for {ticks} ticks...")

        while ticks > 0:
            self.tick_count += 1

            self.update_traffic_lights()
            self.update_cars()
            self.update_pedestrians()

            self.spawn_car()
            self.spawn_pedestrian()

            print_grid(self.grid)
            print(f"Tick: {self.tick_count} | Cars: {len(self.cars)} | Pedestrians: {len(self.pedestrians)}")

            time.sleep(0.5)
            ticks -= 1

if __name__ == "__main__":
    simulator = TrafficSimulator()
    try:
        ticks = int(input("Enter the number of ticks to run the simulation: "))
        if ticks <= 0:
            print("Please enter a positive number")
        else:
            simulator.run_simulation(ticks)
    except ValueError:
        print("Please enter a valid number")
    except KeyboardInterrupt:
        print("\nGoodbye!")