# -=== START: Import Library ===-
import math
import random 
import sys 
import os
import pandas as pd 
from datetime import datetime

import neat 
import pygame
# -=== END: Import Library ===-


# -=== START: Config ===-
WIDTH = 1920
HEIGHT = 1080

START_POS = [952, 102]

CAR_SIZE_X = 18
CAR_SIZE_Y = 45

X_FINISH_LINE = 835
Y_FINISH_LINE = 462
FINISH_COLOR = (255, 0, 0, 255)

CAR_SPEED = 16.5
BORDER_COLOR = (255, 255, 255, 255)

MAX_TIME = 100
PROB_EXPLORE = 0.35

current_generation = 0
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
    return game_map.get_at((int(center[0]), int(center[1]))) == (255, 0, 0, 255)

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


def save_car_data(car, current_generation):
    try:
        car_data = {
            "generation" : current_generation,
            "car_id" : car.car_id,
            "start_position": "1656 - 665",
            "end_position": [f"{round(car.end_position[0], 2)} - {round(car.end_position[1], 2)}"],
            # "end_position": car.end_position,
            "is_finish" : car.is_finish,
            "total_distance" : car.distance,
            "total_time" : car.time,
            "reward" : car.get_reward(),
        }

        car_data = pd.DataFrame(car_data)
        file_name = 'data_append.csv'

        if not os.path.isfile(file_name):
            car_data.to_csv(file_name, index=False)
        else:
            with open(file_name, 'a') as file:
                car_data.to_csv(file, header=False, index=False, mode='a')
        print('car die data appended success')

    except Exception as e:
        print(e)
        print('car die but data not appended')
# -=== End: Global Function ===-


# -=== START: Car Class ===-
class Car:
    
    def __init__(self, car_id, start_position):
        self.car_id = car_id
        self.end_position = None 

        self.sprite = pygame.image.load('assets/car.png').convert()
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        # self.position = start_position
        self.position = start_position
        self.angle = -180 
        self.speed = 0 
        self.speed_set = False

        self.center = get_center(self.position)

        self.radars = []
        self.drawing_radars = []

        self.alive = True 
        self.distance = 0
        self.time = 0
        self.is_finish = False


    def finish(self):
        self.alive = False 
        self.end_position = self.position[:]
        self.is_finish = True
        save_car_data(self, current_generation)
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
                self.end_position = self.position[:]
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
        # if is_finish(game_map, self.center):
        if game_map.get_at((int(self.center[0]), int(self.center[1]))) == (255, 0, 0, 255):
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
        x1, y1 = self.position
        x2, y2 = (X_FINISH_LINE, Y_FINISH_LINE)

        distance_to_finish = calculate_distance(x1, y1, x2, y2)
        max_distance = calculate_max_distance(WIDTH, HEIGHT, x2, y2)

        normalized_distance = 1 - (distance_to_finish/ max_distance)
        normalized_time = 1 - (self.time / MAX_TIME)


        weight_distance = 0.3
        weight_time = 0.7
        # print(self.time, normalized_distance, normalized_time, MAX_TIME)

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


    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
    
        g.fitness = 0
        cars.append(Car(i, [1656, 665]))

    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load('./assets/Rute_final_tanpa_obstacle.png').convert()

    global current_generation
    current_generation += 1

    counter = 0

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
                car.angle -= 15
            elif choice == 1:
                car.angle += 15

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
            else:
                save_car_data(car, current_generation)
                None
            if car.is_finish:
                print("finish coiiiiiiiiiiiiiiiii", car.is_finish)  
            # if car.is_finish:
            #     save_car_data(car, current_generation)


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

# -=== End: Main ===-
