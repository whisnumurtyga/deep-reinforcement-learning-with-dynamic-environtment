# -=== START: Import Library ===-
import math
import random 
import sys 
import os
import pandas as pd 

import neat 
import pygame
# -=== END: Import Library ===-


# -=== START: Config ===-
WIDTH = 1920
HEIGHT = 1080

CAR_SIZE_X = 14
CAR_SIZE_Y = 35

X_FINISH_LINE = 37
Y_FINISH_LINE = 862
FINISH_COLOR = (255, 0, 0, 255)

CAR_SPEED = 16.5
BORDER_COLOR = (255, 255, 255, 255)

MAX_TIME = 100
PROB_EXPLORE = 0.15

current_generation = 0
simulation_data = []
# -=== END: Config ===-



# -=== Start: Global Function ===-
def get_center(position):
    return [int(position[0]) + CAR_SIZE_X / 2, int(position[1]) + CAR_SIZE_Y / 2]

def corner_color_collision(game_map, point):
    return game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR

def calculate_radar_length(center, angle, degree, length):
    x = int(center[0] + math.cos(math.radians(360 - (angle + degree))) * length)
    y = int(center[1] + math.sin(math.radians(360 - (angle + degree))) * length)
    return x, y

def check_border_and_length(game_map, x, y, length):
    return game_map.get_at((x, y)) == BORDER_COLOR and length < 300

def calculate_radar_distance_to_border(center, x, y):
    return int(math.sqrt(math.pow(x - center[0], 2) + math.pow(y - center[1], 2)))

def update_position(position, angle, speed, car_speed, width):
    cos_val = math.cos(math.radians(360 - angle)) * speed 
    sin_val = math.sin(math.radians(360 - angle)) * speed

    new_x = position[0] + cos_val
    new_x = min(max(new_x, car_speed), width - 120)
    
    new_y = position[1] + sin_val
    new_y = min(max(new_y, car_speed), width - 120)
    
    return new_x, new_y

def calculate_car_corner(center, angle, length):
    left_top = [center[0] + math.cos(math.radians(360 - (angle + 30))) * length, center[1] + math.sin(math.radians(360 - (angle + 30))) * length]
    right_top = [center[0] + math.cos(math.radians(360 - (angle + 150))) * length, center[1] + math.sin(math.radians(360 - (angle + 150))) * length]
    left_bottom = [center[0] + math.cos(math.radians(360 - (angle + 210))) * length, center[1] + math.sin(math.radians(360 - (angle + 210))) * length]
    right_bottom = [center[0] + math.cos(math.radians(360 - (angle + 330))) * length, center[1] + math.sin(math.radians(360 - (angle + 330))) * length]

    return left_top, right_top, left_bottom, right_bottom

def is_finish(game_map, center):
    return game_map.get_at((int(center[0]), int(center[1]))) == FINISH_COLOR

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calculate_max_distance(WIDTH, HEIGHT, finish_line_x, finish_line_y):
    return ((WIDTH - finish_line_x) ** 2 + (HEIGHT - finish_line_y) ** 2) ** 0.5

def second_largest_index(arr):
    try: 
        max_val = max(arr)
        return arr.index(max(filter(lambda x: x != max_val, arr)))
    except:
        print(arr)

def draw_text(screen, font, text, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def color_match(color, target_colors, tolerance=10):
    for target_color in target_colors:
        if all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color, target_color)):
            return True
    return False

# -=== End: Global Function ===-



# -=== START: Car Class ===-
class Car:
    
    def __init__(self, car_id, start_position):
        self.car_id = car_id
        self.start_position = start_position
        self.end_position = None 

        self.sprite = pygame.image.load('assets/car.png').convert()
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        self.position =[1656, 665]
        self.angle = -180
        self.speed = 0 
        self.speed_set = False

        self.center = get_center(self.position)

        self.radars = []
        self.drawing_radars = []

        self.alive = True 
        self.distance = 0
        self.time = 0


    def finish(self):
        self.alive = False 
        self.end_position = self.position[:]
        print("Mobil telah melewati garis finish!")
        # print(f"Time: {self.time}\t-\tDistance: {self.distance}")

    
    def draw(self, screen):
        rotated_sprite, new_rect = self.rotate_center(self.sprite, self.angle)
        screen.blit(rotated_sprite, self.position)
        self.draw_radar(screen)

    
    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)


    def check_collision(self, game_map):
        self.alive = True 
        for point in self.corners:
            if corner_color_collision(game_map, point):
                self.alive = False
                break
    
    
    def check_radar(self, degree, game_map):
        length = 0
        x, y = calculate_radar_length(self.center, self.angle, degree, length)

        try:
            # while not check_border_and_length(game_map, x, y, length):
            while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
                length = length + 1
                x, y = calculate_radar_length(self.center, self.angle, degree, length)
        except:
            print(length, x, y)
        
        
        dist = calculate_radar_distance_to_border(self.center, x, y)
        self.radars.append([(x, y), dist])

    
    def update(self, game_map):
        if not self.speed_set:
            self.speed = CAR_SPEED
            self.speed_set = True

        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)

        self.position[0], self.position[1] = update_position(self.position, self.angle, self.speed, CAR_SPEED, WIDTH)

        self.distance += self.speed
        self.time += 1

        self.center = get_center(self.position)
        length = 0.5 * CAR_SIZE_X

        left_top, right_top, left_bottom, right_bottom = calculate_car_corner(self.center, self.angle, length)
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(game_map)
        if is_finish(game_map, self.center):
            self.finish()

        self.radars.clear()
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)
    
    def get_data(self):
        radars = self.radars 
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)
        return return_values
    
    
    def is_alive(self):
        return self.alive
    

    def get_reward(self):
        
        finish_line_x = X_FINISH_LINE  
        finish_line_y = Y_FINISH_LINE  
       
        distance_to_finish = ((self.position[0] - finish_line_x) ** 2 + (self.position[1] - finish_line_y) ** 2) ** 0.5
      
        max_distance = ((WIDTH - finish_line_x) ** 2 + (HEIGHT - finish_line_y) ** 2) ** 0.5
        normalized_distance = 1 - (distance_to_finish / max_distance)
        normalized_time = 1 - (self.time / MAX_TIME)
       
        weight_distance = 0.4 
        weight_time = 0.6  

        final_reward = (weight_distance * normalized_distance) + (weight_time * normalized_time)
        
        return final_reward
    
    def rotate_center(self, image, angle):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect().center)
    
        rotated_image = pygame.transform.scale(rotated_image, (CAR_SIZE_X, CAR_SIZE_Y))
        return rotated_image, new_rect
# -=== End: Car Class ===-



def run_simulation(genomes, config):
    nets = []
    cars = []
    obstacles = [
        {"name": "lampu_merah", "colors": [(222, 89, 78, 255), (200, 80, 70, 255)]},
        {"name": "Orang_nyebrang", "colors": [(255, 183, 76, 255)]},
        {"name": "mobil", "colors": [(255, 188, 5, 255)]},
    ]
   
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)

        g.fitness = 0
        cars.append(Car(i, [952, 102]))

    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load('./assets/Rute_final_Obstacle2.png').convert()

    global current_generation
    current_generation += 1

    counter = 0   
    paused_times = [0] * len(cars)
    initial_pause_done = [False] * len(cars)
    pause_duration = 3
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))

            if random.random() < PROB_EXPLORE:
                choice = second_largest_index(output)

            if choice == 0:
                car.speed /= 2
                car.angle -= 17  # Left
                car.speed *= 2
            elif choice == 1:
                car.speed /= 2
                car.angle += 17  # Right
                car.speed *= 2
            current_color = game_map.get_at((int(car.center[0]), int(car.center[1])))
            for obstacle in obstacles:
                if color_match(current_color, obstacle["colors"]):
                 
                    if not initial_pause_done[i]:
                        paused_times[i] = pygame.time.get_ticks() / 1000  
                        initial_pause_done[i] = True

                    current_time = pygame.time.get_ticks() / 1000  
                    elapsed_time = current_time - paused_times[i]

                    if elapsed_time < pause_duration:
                        car.speed = 0  
                        continue  

                   
                    car.speed = CAR_SPEED  


            if car.is_alive():
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()
            else:
                simulation_data.append({
                'generation': current_generation,
                'car_id': car.car_id, 
                'start_position_x': car.start_position[0],
                'start_position_y': car.start_position[1],
                'end_position_x': car.end_position[0] if car.end_position is not None else None,
                'end_position_y': car.end_position[1] if car.end_position is not None else None,
                'is_alive': car.is_alive(),
                'total_distance': car.distance,
                'total_time': car.time,
                'reward': car.get_reward(),

            })
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break 

        counter += 1 
        # Limit per car buat nyelesaiin
        if counter == 30*40:
            break

        screen.blit(game_map, (0,0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        generation_text = "Generation: " + str(current_generation)
        draw_text(screen, generation_font, generation_text, (0, 0, 0), 245, 144)
        alive_text = "Still Alive: " + str(still_alive)
        draw_text(screen, alive_font, alive_text, (0, 0, 0), 245, 194)

        pygame.display.flip()
        clock.tick(60)



# -=== Start: Main ===-
if __name__ == "__main__":
    config_path = "./config.txt"
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path
                                )
    
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()

    population.run(run_simulation, 1000)
    df = pd.DataFrame(simulation_data)
    df.to_csv('simulation_data.csv', index=False)