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
# => Map
WIDTH = 1920
HEIGHT = 1080

# => Car
CAR_SIZE = (14, 35)
CAR_SIZE_X = 14
CAR_SIZE_Y = 35
CAR_SPEED = 10
ANGLE = -90

# => Start Position
START_POS = [952, 102]

# => Finish Line
FINISH_POS = [835, 462]
FINISH_COLOR = (255, 0, 0, 255)
X_FINISH_LINE = 835
Y_FINISH_LINE = 462

# => Utility
MAX_TIME = 100
PROB_EXPLORE = 0.15
BORDER_COLOR = (255, 255, 255, 255)
WEIGHT_TIME = 0.7
WEIGHT_DISTANCE = 0.3
LIMIT_GENERATION = 50
# -=== END: Config ===-


current_generation = 0


# -=== START: Car Class ===-
class Car:
    # => Construct
    def __init__(self, car_id):
        self.car_id = car_id
        self.end_position = None
        self.sprite = pygame.image.load('./assets/car.png').convert()
        self.sprite = pygame.transform.scale(self.sprite, CAR_SIZE)
        self.rotated_sprite = self.sprite
        
        self.position = START_POS
        self.angle = ANGLE
        self.speed = CAR_SPEED
        
        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]
        self.radars = []
        self.drawing_radars = []
        
        self.speed_set = False 
        self.alive = True 
        self.distance = 0
        self.time = 0
        
    # => Finish Function
    def finish(self):
        self.alive = False 
        self.end_position = self.position[:]
        print("Mobil telah melewati garis finish!")
        print(f"Time: {self.time}\t-\tDistance: {self.distance}")

    # => Draw Function
    def draw(self, screen):
        rotated_sprite,new_rect = self.rotate_center(self.sprite, self.angle)
        screen.blit(rotated_sprite, self.position)
        self.draw_radar(screen)
    
    # => Draw Radar   
    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5) 
    
    # => Check Collision Function
    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            if game_map.get_at( (int(point[0]), int(point[1])) ) == BORDER_COLOR: 
                self.alive = False 
                break
            
    # => Fungsi Check Radar 
    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
          
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1 
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
  
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    

    # => Fyngsi Update
    def update(self, game_map):
        if not self.speed_set:
            self.speed = CAR_SPEED
            self.speed_set = True

        self.rotated_sprite = self.rotate_center(self.sprite, self.angle) 
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], CAR_SPEED)
        self.position[0] = min(self.position[0], WIDTH - 120)

        self.distance += self.speed
        self.time += 1
        
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], CAR_AVG_SPEED)
        self.position[1] = min(self.position[1], WIDTH - 120)

        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]
        
        length = 0.5 * CAR_SIZE_X 
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]
        
        self.check_collision(game_map)
        if game_map.get_at((int(self.center[0]), int(self.center[1]))) == FINISH_COLOR:
            self.finish()
                        
        self.radars.clear()

        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)
    

    # => Fungsi mengambil data radar
    def get_data(self):
        radars = self.radars 
        return_values = [0, 0, 0, 0, 0] 
        
        for i, radar in enumerate(radars): 
            return_values[i] = int(radar[1] / 30)
            
        return return_values
    

    # ==> Reward Function
    def get_reward(self):
        finish_line_x = X_FINISH_LINE  
        finish_line_y = Y_FINISH_LINE  

        distance_to_finish = ((self.position[0] - finish_line_x) ** 2 + (self.position[1] - finish_line_y) ** 2) ** 0.5
        max_distance = ((WIDTH - finish_line_x) ** 2 + (HEIGHT - finish_line_y) ** 2) ** 0.5
 
        normalized_distance = 1 - (distance_to_finish / max_distance)
        normalized_time = 1 - (self.time / MAX_TIME)

        weight_distance = WEIGHT_DISTANCE  
        weight_time = WEIGHT_TIME

        final_reward = (weight_distance * normalized_distance) + (weight_time * normalized_time)
        
        return final_reward
    

    # 
    def rotate_center(self, image, angle):
        rotated_image = pygame.transform.rotatee(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect().center)
        rotated_image = pygame.transform.scale(rotated_image, (CAR_SIZE_X, CAR_SIZE_Y))
        return rotated_image, new_rect
    
# -=== END: Car Class ===-
    
    

# -=== START: Function ===-
def second_largest_index(arr):
    max_val = max(arr)
    arr.remove(max_val)
    second_max = max(arr)
    return arr.index(second_max)


simulation_data = []
def run_simulation(genomes, config):
    nets = []
    cars = []

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car(i, START_POS))

        clock = pygame.time.Clock()
        generation_font = pygame.font.SysFont("Arial", 30) 
        alive_font = pygame.font.SysFont("Arial", 20)  
        game_map = pygame.image.load('assets/Rute_cabang.png').convert()

        global current_generation
        current_generation += 1

        counter = 0
        while current_generation <= LIMIT_GENERATION:
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)

            for i, car in enumerate(cars):
                output = nets[i].activate(car.get_data())
                choice = output.index(max(output))

                if random.random() < PROB_EXPLORE:
                    choice = second_largest_index(output)
                
                if choice == 0:
                    car.angle -= 17
                elif choice == 1:
                    car.angle += 17
            
            still_alive = 0
            for i, car in enumerate(cars):
                if car.is_alive():
                    still_alive += 1
                    car.update(game_map)
                    genomes[i][1].fitness += car.get_reward()
                else:
                    simulation_data.append({
                        'generation': current_generation,
                        'car_id': car.car_id, 
                        'start_position_x': START_POS[0],
                        'start_position_y': START_POS[1],
                        'end_position_x': car.end_position[0],
                        'end_position_y': car.end_position[1],
                        'is_alive': car.is_alive,
                        'total_distance': car.total_distance,
                        'total_time': car.total_time,
                        'reward': car.get_reward(),
                    })

            if still_alive == 0:
                break

            screen.blit(game_map, (0, 0))
            for car in cars:
                if car.is_alive():
                    car.draw(screen)

            text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
            text_rect = text.get_rect()
            text_rect.center = (245, 144)
            screen.blit(text, text_rect)

            text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.center = (245, 194)
            screen.blit(text, text_rect)

            pygame.display.flip()
            clock.tick(60)
# -=== END: Function ===-



# -=== START: Main ===-
if __name__ == "__main__":
    config_path = "./config.txt"
    config = neat.config.Config(
                                neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                )
    
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    population.run(run_simulation, LIMIT_GENERATION)
# -=== END: Main ===-