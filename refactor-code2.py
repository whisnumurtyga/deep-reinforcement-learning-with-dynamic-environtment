import math
import random
import sys
import os

import neat
import pygame
import pandas as pd


# => Map 
WIDTH = 1920 #lebar sama ukuran layar 
HEIGHT = 1080

# => Car
CAR_SIZE_X = 14  
CAR_SIZE_Y = 35
CAR_SIZE = (CAR_SIZE_X,CAR_SIZE_Y)
CAR_SPEED = 16.5
ANGLE = -180

# => Finis line
X_FINISH_LINE = 37
Y_FINISH_LINE = 862
FINISH_POS = [X_FINISH_LINE,Y_FINISH_LINE]
FINISH_COLOR = (255, 0, 0, 255)

# => Utility
BORDER_COLOR = (255, 255, 255, 255)
MAX_TIME = 100
PROB_EXPLORE = 0.15


STATIC_OBSTACLES = [
    {"name": "lampu_merah", "colors": [(222, 89, 78, 255), (200, 80, 70, 255)], "image": None},
]


# => Koordinat obstacle dinamis
DYNAMIC_OBSTACLE_COORDINATES = [[1000, 640], [1326, 140],[1500,500]]

current_generation = 0
simulation_data = []

# -=== START : Car Class ===-
class Car:

    def __init__(self, car_id, start_position):
        self.car_id = car_id 
        self.start_position = start_position
        self.end_position = None  
   
        self.sprite = pygame.image.load('./assets/car.png').convert() 
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE)) 
        self.rotated_sprite = self.sprite 

        self.position =[1656, 665]
        self.angle = ANGLE 
        self.speed = 0 

        self.speed_set = False 

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] 

        self.radars = [] 
        self.drawing_radars = [] 

        self.alive = True 

        self.distance = 0 
        self.time = 0 


    def draw(self, screen):
        rotated_sprite,new_rect = self.rotate_center(self.sprite, self.angle)
        screen.blit(rotated_sprite, self.position)
        self.draw_radar(screen)  


    def draw_radar(self, screen):
        for radar in self.radars: 
            position = radar[0] 
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1) 
            pygame.draw.circle(screen, (0, 255, 0), position, 5) 


    def finish(self):
        self.alive = False
        self.end_position = self.position[:]  
        print("Mobil telah melewati garis finish!")
        print(f"Time: {self.time}\t-\tDistance: {self.distance}")
    

    # ----Fungsi draw_radar buat ngegambar sensor deteksi batas pada layar---- #

    def check_collision(self, game_map):
        self.alive = True  
        for point in self.corners:  
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                print(point)
                self.alive = False
                break
        
    # --- Fungi check_collison intinya buat ngecek si mobil nyentuh batas jalannya ngga ---- #

    def check_radar(self, degree, game_map):
        length = 0 # 
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
       
        # looping selama warna dari sensor ga sama kayak BORDER COLOR dan panjang garis nya <300
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1 #panjang jarak ditambahin
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
       
    # ---- Fungsi check_radar buat ngukur jarak dari sensor radar mobil ke batas ---- #
    

    def update(self, game_map):
        if not self.speed_set:
            self.speed = CAR_SPEED
            self.speed_set = True

        self.rotated_sprite = self.rotate_center(self.sprite, self.angle) # gambar mobil yang udah dirotasi dihitung untuk melakukan rotasi terhadap gambar mobil berdasarkan sudut (self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], CAR_SPEED)
        self.position[0] = min(self.position[0], WIDTH - 120)
    
        self.time += 1
        
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], CAR_SPEED)
        self.position[1] = min(self.position[1], WIDTH - 120)
        self.distance += self.speed
        
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
    
    # rotate_center intinya buat mastiin ketika gambar nya diputar pusat rotasinya tetep dipertahanin

def second_largest_index(arr):
    max_val = max(arr)
    arr.remove(max_val)
    second_max = max(arr)
    return arr.index(second_max)

simulation_data = []

def color_match(color, target_colors, tolerance=10):
    for target_color in target_colors:
        if all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color, target_color)):
            return True
    return False



#---- Buat obstacle dinamis ----#

def generate_dynamic_obstacles():
    dynamic_obstacles = []

    pedestrian_image = pygame.image.load('./assets/Obstacle_orang.png').convert_alpha()
    car_image = pygame.image.load('./assets/Obstacle_mobil.png').convert_alpha()

    obstacle_types = ["pedestrian", "car"]
    selected_coordinates = random.sample(DYNAMIC_OBSTACLE_COORDINATES, 2)

    for i in range(2):  # Menggunakan dua dari tiga koordinat pada setiap generasi
        coord = selected_coordinates[i]
        obstacle_type = random.choice(obstacle_types)
        print(f"Generated obstacle of type: {obstacle_type}")
        
        if obstacle_type == "pedestrian":
            obstacle_image = pedestrian_image
            obstacle_colors = [(255, 183, 76, 255)] 
        else:
            obstacle_image = car_image
            obstacle_colors = [(255, 188, 5, 255)]  
        
        obstacle = {
            "type": obstacle_type,
            "coordinates": coord,
            "image": obstacle_image,
            "colors": obstacle_colors
        }
        dynamic_obstacles.append(obstacle)

    return dynamic_obstacles



# => draw obstacle dinamis ke screen
def draw_obstacles(screen, obstacles):
    for obstacle in obstacles:
        if obstacle["image"] is not None:
            obstacle_rect = obstacle["image"].get_rect(topleft=obstacle["coordinates"])
            screen.blit(obstacle["image"], obstacle_rect)



def run_simulation(genomes, config):

    nets = []
    cars = []

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # ----- Genomes ----- #
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

    dynamic_obstacles = generate_dynamic_obstacles() #--Inisalisasi fungsi generate dynamic obstacles-#

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # ---- Car Actions ---- #
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

            # ---- Pause Condition ---- #
            current_color = game_map.get_at((int(car.center[0]), int(car.center[1])))

            # Check collision with static obstacles
            for obstacle in STATIC_OBSTACLES:
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
                    
            # cek tabrakan sama obstacle dinamis
            for obstacle in dynamic_obstacles:
                obstacle_rect = obstacle["image"].get_rect(topleft=obstacle["coordinates"])
                if obstacle_rect.collidepoint(int(car.center[0]), int(car.center[1])):
                    print("type obstacle =", obstacle["type"])

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

        still_alive = sum(car.is_alive() for car in cars)

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:
            break

        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Draw dynamic obstacles
        draw_obstacles(screen, dynamic_obstacles)

        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (600, 144)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (600, 194)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    
    # Load Config
    config_path = "./config.txt" # File konfigurasi ini mengandung informasi mengenai parameter-parameter yang diperlukan untuk menjalankan algoritma NEAT (NeuroEvolution of Augmenting Topologies).
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)

    population = neat.Population(config) 
    population.add_reporter(neat.StdOutReporter(True))  
    stats = neat.StatisticsReporter() 
    population.add_reporter(stats) 
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
    df = pd.DataFrame(simulation_data)
    df.to_csv('simulation_data.csv', index=False)
    print(df)