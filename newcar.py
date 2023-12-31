# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)

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
CAR_SPEED = 10
ANGLE = -180

# => Start position
START_POS = [1656, 665]

# => Finis line
X_FINISH_LINE = 37
Y_FINISH_LINE = 862
FINISH_POS = [X_FINISH_LINE,Y_FINISH_LINE]
FINISH_COLOR = (255, 0, 0, 255)

BORDER_COLOR = (255, 255, 255, 255)

MAX_TIME = 100

PROB_EXPLORE = 0.15

current_generation = 0 #inisialisai generation

class Car:

    def __init__(self, car_id, start_position):
        self.car_id = car_id 
        self.start_position = start_position
        self.end_position = None  
   
        self.sprite = pygame.image.load('./assets/car.png').convert() 
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y)) 
        self.rotated_sprite = self.sprite 

        self.position = [1656, 665] # Titik awal mobil (start line nya)
        # self.angle = 0 #ini buat sudut mobilya di set 0 supaya dia lurus (arah hadap mobilnya)
        self.angle = -180 #ini buat sudut mobilya di set 0 supaya dia lurus (arah hadap mobilnya)
        self.speed = 0 #kecepatan awal mobil (awalan di set diem)

        self.speed_set = False # flag atau penanda buat ngeset kecepatan awalnya = 0,selanjutnya diubah jadi true terus di ganti kecepatan nya jadi 20

        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2] # Mneghitung posisi center mobil berdasarkan posisi awal sama ukuran mobil

        self.radars = [] # List yang isinya data sensor atau rada mobil,sensor itu buat mendeteksi jarak ke batas lintasan (border)
        self.drawing_radars = [] # List yang isinya posisi radar yang akan di gambar di layar

        self.alive = True # Boolean buat nandain mobilnya masih idup apa engga,buat posisi awal di set hidup

        self.distance = 0 # Jarak yang ditempuh mobilnya,jaraknya bertambah seiring jalannya waktu
        self.time = 0 # Waktu yang berlalu dari dimulainya simulasi


    def finish(self):
        # Logika yang dijalankan saat mobil melewati garis finish
        self.alive = False
        self.end_position = self.position[:]  # Simpan posisi akhir mobil saat melewati garis finish
        print("Mobil telah melewati garis finish!")
        print(f"Time: {self.time}\t-\tDistance: {self.distance}")
    
    # def draw(self, screen):
    #     screen.blit(self.rotated_sprite, self.position) 
    #     self.draw_radar(screen) #OPTIONAL FOR SENSORS
    def draw(self, screen):
        rotated_sprite, new_rect = self.rotate_center(self.sprite, self.angle)
        screen.blit(rotated_sprite, self.position)
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    # Fungsi draw intinya buat nge gambar mobilnya yang udah di rotate jadi lurus

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars: # loop buat nge isi dari self.radars
            position = radar[0] # ngambil posisi sensor radar dari radar saat ini
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1) # gambar garis dari pusat mobil ke posisi sensor radar jadi bisa kasih representasi visual dari sensor radar yang menunujuk ke arah batas tertentu
            pygame.draw.circle(screen, (0, 255, 0), position, 5) # gambar lingkaran buat area deteksi dari sensor radar.

    # ----Fungsi draw_radar buat ngegambar sensor deteksi batas pada layar---- #

    def check_collision(self, game_map):
        self.alive = True  # nge set mobil nya hidup 
        for point in self.corners: # loop ngecek setiap sudut mobil (self.corners itu sudut-sudut mobil)
            # Jika ada titik yang kena border jalan = crash 
            # Mobilnya diasumsikan persegi jadi cuman ada 4 titik 

            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                print(point)
                self.alive = False
                break
            # Mengecek kalo ada warna dari posisi sudut mobil  sama dengan BORDER_COLOR,maka mobilnya mati (self.alive = false),terus di break

    # --- Fungi check_collison intinya buat ngecek si mobil nyentuh batas jalannya ngga ---- #

    def check_radar(self, degree, game_map):
        length = 0 # inisialisasi panjang jarak garis ke batas jalan
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
        # line 84 - 85 hitung koordinat X dan Y berdasarkan sudut dan panjang dari pusat mobil,buat nentuin jarak dari sensor ke batas

   
        # looping selama warna dari sensor ga sama kayak BORDER COLOR dan panjang garis nya <300
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1 #panjang jarak ditambahin
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
        # line 92 - 93 buat hitung jarak dari pusat mobil ke batas (BORDER_COLOR) dalam area tertentu
        # Calculate Distance To Border And Append To Radars List
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
        #  Jika kena batas jaraknya dihitung antara posisi radar terakhir dan pusat mobil.Hasilnya ditambahin ke dalam list slef.radars dalam bentuk [posisi_radar,jarak]

    # ---- Fungsi check_radar buat ngukur jarak dari sensor radar mobil ke batas ---- #
    
    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = CAR_SPEED
            # self.speed = 20
            self.speed_set = True

        # line 105 - 107 di cek kecepatannya udah diatur self.speed_set
        # jika belum kecepatannya diatur jadi 20 dan self.speed_test diatur menjadi True.
        # Kecepatan default = 0 hanya diatur sekali,selanjutnya konstan 20 

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle) # gambar mobil yang udah dirotasi dihitung untuk melakukan rotasi terhadap gambar mobil berdasarkan sudut (self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        # self.position[0] = max(self.position[0], 20)
        self.position[0] = max(self.position[0], CAR_SPEED)
        self.position[0] = min(self.position[0], WIDTH - 120)

        #line 116 - 118 update posisi mobil pada sumbu X (kanan) berdasarakn arah hadap mobil (self.angle) dan kecepatan (self.speed)
        # posisinya dibatasi supaya ngga mendekati border,dengan nilai minimum 20 piksel dna nilai maksimum (WIDTH - 120)

        # Ningkatin jarak (self.distance) dan waktu (self.time) berdasarkan kecepatan mobil
        
        self.time += 1
        
        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], CAR_SPEED)
        self.position[1] = min(self.position[1], WIDTH - 120)
        self.distance += self.speed
        # prinsip nya sama kayak yang X,cuman posisinya ke Y (kiri)

        # Hitung kembali pusat mobil (self.center) berdasarkan posisi mobil yang udah diupdate
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        
        length = 0.5 * CAR_SIZE_X # hitung panjang dari pusat mobil ke tiap salah satu sudut (setengah karna bentuknya persegi,jarak dari pusat ke sudut dibikin setengah)
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]
        
        # Line 138 - 142 hitung koordinat keempat sudut 
        # contoh : left_top hitungannya dibagi jadi 2 cos (X) sama sin (Y),terus 360 (lingkaran penuh) dikurnangin self.angel + 30 jadi diputer 330 derajat searah jarum jam )

        # Manggil metthod check_collision buat meriksa mobilnya bersentuhan sama batas ngga.
        # Terus di clear list radar (self.radars) buat persiapan pengukuran radar selanjutnya
        self.check_collision(game_map)
        if game_map.get_at((int(self.center[0]), int(self.center[1]))) == FINISH_COLOR:
            self.finish()
                        
        self.radars.clear()

        
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)
        # Loop di atas menciptakan sensor radar dengan arah tertentu sebanyak lima kali, masing-masing pada sudut -90, -45, 0, 45, dan 90 derajat. 
        # Jadi, sensor radarnya bakal diarahin ke lima arah yang berbeda di sekitar mobil dengan interval sudut 45 derajat.
        # 120 itu kayak batas nya gitu 

    def get_data(self):
        # Get Distances To Border
        radars = self.radars # inisialisasi data sensor dari self.radars,setiap isi dari self.radrs isinya pasangan koordinat dan jarak ke batas lintasan
        return_values = [0, 0, 0, 0, 0] # inisialisasi list yang panjangny 5,nanti dipakek buat nyimpen data jarak yang di return
        for i, radar in enumerate(radars): # looping isi radars,i indeks,radar itu data sensor radar pada posisi tertentu
            return_values[i] = int(radar[1] / 30)
            # nilai jarak dari sensor radar dibagi degan 30,dan hasilnya diubah menjadi integer
            # dibagi 30 kayaknya buat ngubah nilai jarak jadi format yang lebih kecil dan sesuai kalo giunakan sebagai masukan jaringan saraf
        return return_values

    # get_data intinya buat ngumpulin data terus dimasukin ke dalam jaringan saraf.
    # Data yang dikumpulin itu jarak dari sensor radar mobil ke batas atau halangan


    def is_alive(self):
        # Basic Alive Function
        return self.alive
    
    # is_alive buat nentuin mobilnya hidup atau crash

    # def get_reward(self):
    #     # Calculate Reward (Maybe Change?)
    #     # return self.distance / 50.0
    #     return self.distance / (CAR_SIZE_X / 2)

    def get_reward(self):
        # Koordinat garis finish
        finish_line_x = X_FINISH_LINE  # Ganti X_FINISH_LINE dengan koordinat X dari garis finish
        finish_line_y = Y_FINISH_LINE  # Ganti Y_FINISH_LINE dengan koordinat Y dari garis finish

        # Hitung jarak dari mobil ke garis finish
        distance_to_finish = ((self.position[0] - finish_line_x) ** 2 + (self.position[1] - finish_line_y) ** 2) ** 0.5

        # Normalisasi jarak agar mendekati nilai 1 saat mobil semakin mendekati garis finish
        max_distance = ((WIDTH - finish_line_x) ** 2 + (HEIGHT - finish_line_y) ** 2) ** 0.5
        normalized_distance = 1 - (distance_to_finish / max_distance)

        # Normalisasi waktu, misalnya dengan membagi waktu yang berlalu dengan batas waktu maksimal
        normalized_time = 1 - (self.time / MAX_TIME)

        # Menentukan bobot untuk kontribusi waktu dan jarak terhadap reward
        weight_distance = 0.7  # Bobot jarak
        weight_time = 0.3  # Bobot waktu

        # Menggabungkan kontribusi waktu dan jarak untuk mendapatkan reward akhir
        final_reward = (weight_distance * normalized_distance) + (weight_time * normalized_time)
        
        return final_reward



    # def rotate_center(self, image, angle):
    #     # Rotate The Rectangle
    #     rectangle = image.get_rect() # Membuat objek rectangle yang merupakan objek rect (persegi panjang) dari gambar (image). Rect ini digunakan untuk menghitung pusat gambar sebelum rotasi.
    #     rotated_image = pygame.transform.rotate(image, angle) # buat muter gambar sebesar sudut yang ditentui samma parameter angle
    #     rotated_rectangle = rectangle.copy() # copy objek rectangle,buat simpen informasi persegii panjang (image) sebelum di rotate
    #     rotated_rectangle.center = rotated_image.get_rect().center # Mengatur pusat dari rotated_rectangle menjadi pusat dari rect hasil rotasi (rotated_image). Hal ini memastikan bahwa rotasi dilakukan terhadap pusat gambar 
    #     rotated_image = rotated_image.subsurface(rotated_rectangle).copy() # Mengatur pusat dari rotated_rectangle menjadi pusat dari rect hasil rotasi (rotated_image). Hal ini memastikan bahwa rotasi dilakukan terhadap pusat gambar 
    #     return rotated_image
    
    def rotate_center(self, image, angle):
        # Rotate The Image
        rotated_image = pygame.transform.rotate(image, angle)
        # Get The New Rect
        new_rect = rotated_image.get_rect(center=image.get_rect().center)
        # Resize The Image
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

def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []
    obstacles = [
        {"name": "lampu_merah", "colors": [(222, 89, 78, 255), (200, 80, 70, 255)]},
        {"name": "Orang_nyebrang", "colors": [(255, 183, 76, 255)]},
        {"name": "mobil", "colors": [(255, 188, 5, 255)]},
        # Add more obstacles if needed
    ]
    # Initialize Pygame and create a screen with the specified size
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

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0
    # Add a new variable for tracking paused time and an initial pause flag
    paused_times = [0] * len(cars)
    initial_pause_done = [False] * len(cars)
    pause_duration = 5

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
            for obstacle in obstacles:
                if color_match(current_color, obstacle["colors"]):
                    # Check if the color at the car's position matches any colors in the current obstacle
                    if not initial_pause_done[i]:
                        paused_times[i] = pygame.time.get_ticks() / 1000  # Convert milliseconds to seconds
                        initial_pause_done[i] = True

                    current_time = pygame.time.get_ticks() / 1000  # Convert milliseconds to seconds
                    elapsed_time = current_time - paused_times[i]

                    if elapsed_time < pause_duration:
                        car.speed = 0  # Stop the car
                        continue  # Skip the rest of the loop and continue the pause

                    # Reset pause conditions after the pause duration is over
                    car.speed = CAR_SPEED  # Reset the speed

            # Track time when the car is alive
            if car.is_alive():
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = sum(car.is_alive() for car in cars)

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:  # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (245, 144)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (245, 194)
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

    # Create Population And Add Reporters
    population = neat.Population(config) # Membuat populasi awal dengan menggunakan konfigurasi yang telah dibuat. Objek populasi ini akan digunakan untuk melatih dan mengembangkan jaringan saraf.
    population.add_reporter(neat.StdOutReporter(True))  # Menambahkan reporter yang akan mencetak informasi ke konsol. Reporter neat.StdOutReporter akan mencetak informasi seperti generasi saat ini, rata-rata nilai kebugaran, dan informasi lainnya ke konsol.
    stats = neat.StatisticsReporter() # Membuat objek reporter statistik. Reporter ini akan mengumpulkan dan menyimpan data statistik selama proses evolusi, seperti nilai kebugaran terbaik dan rata-rata, jumlah spesies, dan lainnya.
    population.add_reporter(stats) #  Menambahkan reporter statistik ke dalam populasi. Dengan menambahkan reporter, informasi statistik akan tercatat dan dapat diakses setelah simulasi selesai.
    
    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)


# neat.DefaultGenome: Mengacu pada kelas default yang digunakan untuk mewakili genom dalam algoritma NEAT. Genome ini akan mencakup struktur jaringan saraf, bobot koneksi antar neuron, dan informasi genetik lainnya
# neat.DefaultReproduction: Mengacu pada kelas default yang mengimplementasikan logika reproduksi dalam algoritma NEAT. Reproduksi ini melibatkan pembuatan salinan genom, persilangan (crossover) genom, dan mutasi.
# neat.DefaultSpeciesSet: Mengacu pada kelas default yang digunakan untuk menyimpan dan mengelola populasi genom yang dibagi menjadi spesies-spesies. Spesies adalah kelompok genom-genom yang memiliki kesamaan struktural.
# neat.DefaultStagnation: Mengacu pada kelas default yang menangani stagnasi dalam algoritma NEAT. Stagnasi terjadi ketika evolusi tidak menghasilkan kemajuan yang signifikan, dan strategi untuk mengatasi stagnasi dapat diimplementasikan di sini.
# config_path: Merupakan path ke file konfigurasi yang berisi parameter-parameter yang diperlukan untuk menjalankan algoritma NEAT. File ini biasanya berisi pengaturan seperti jumlah neuron dalam lapisan input dan output, probabilitas mutasi, parameter persilangan, dan sebagainya.