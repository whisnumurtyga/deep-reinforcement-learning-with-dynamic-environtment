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
X_FINISH_LINE = 835
Y_FINISH_LINE = 462

# => Utility
MAX_TIME = 100
PROB_EXPLORE = 0.15
BORDER_COLOR = (255, 255, 255, 255)
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
        
        w
        
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1 #panjang jarak ditambahin
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
        # line 92 - 93 buat hitung jarak dari pusat mobil ke batas (BORDER_COLOR) dalam area tertentu
        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    
# -=== END: Car Class ===-
    

# -=== START: Config ===-
# -=== END: Config ===-