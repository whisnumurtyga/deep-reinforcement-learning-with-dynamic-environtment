# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)

import math
import random
import sys
import os

import neat
import pygame

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1920 #lebar sama ukuran layar 
HEIGHT = 1080

CAR_SIZE_X = 15 #ini nge set ukuran mobilnya
CAR_SIZE_Y = 15

BORDER_COLOR = (255, 255, 255, 255) # ini buat batas jalan atau border nya

current_generation = 0 #inisialisai generation

class Car:

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load('car.png').convert() 
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y)) 
        self.rotated_sprite = self.sprite 

        #Line 30 - 32 itu dia ngambil gambar mobilnya terus di scale sesuai CAR_SIZE_X sama Y
        # terus rotated_sprite itu buat nge rotate gambarnya sesuai sama arah pergerakkan mobilnya
        
    
        self.position = [1070, 191] # Titik awal mobil (start line nya)
        self.angle = 270 #ini buat sudut mobilya di set 0 supaya dia lurus (arah hadap mobilnya)
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
        print("Mobil telah melewati garis finish!")
        
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
            self.speed =25
            self.speed_set = True
        
        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Ningkatin jarak (self.distance) dan waktu (self.time) berdasarkan kecepatan mobil
        self.distance += self.speed
        self.time += 1
        
        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Hitung kembali pusat mobil (self.center) berdasarkan posisi mobil yang udah diupdate
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        # Calculate the coordinates of the car's corners
        length = 0.5 * CAR_SIZE_X
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check for collision and clear the radar list for the next measurements
        self.check_collision(game_map)
        current_color = game_map.get_at((int(self.center[0]), int(self.center[1])))
        target_color = (255, 230, 0, 255)
        tolerance = 10  # Adjust as needed

        if all(abs(a - b) <= tolerance for a, b in zip(current_color, target_color)):
            # Logic to handle the detection of the yellow color
            self.angle += 180  # Rotate the car by 180 degrees (adjust as needed)
            self.speed = 3   # Set a new speed (adjust as needed)
            print("Yellow color detected -------")
            self.alive = False

        if game_map.get_at((int(self.center[0]), int(self.center[1]))) == (255, 0, 0, 255):
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

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)
    
    def rotate_center(self, image, angle):
        # Rotate The Image
        rotated_image = pygame.transform.rotate(image, angle)

        # Get The New Rect
        new_rect = rotated_image.get_rect(center=image.get_rect().center)

        # Resize The Image
        rotated_image = pygame.transform.scale(rotated_image, (CAR_SIZE_X, CAR_SIZE_Y))

        return rotated_image, new_rect


    # def rotate_center(self, image, angle):
    #     # Rotate The Rectangle
    #     rectangle = image.get_rect() # Membuat objek rectangle yang merupakan objek rect (persegi panjang) dari gambar (image). Rect ini digunakan untuk menghitung pusat gambar sebelum rotasi.
    #     rotated_image = pygame.transform.rotate(image, angle) # buat muter gambar sebesar sudut yang ditentui samma parameter angle
    #     rotated_rectangle = rectangle.copy() # copy objek rectangle,buat simpen informasi persegii panjang (image) sebelum di rotate
    #     rotated_rectangle.center = rotated_image.get_rect().center # Mengatur pusat dari rotated_rectangle menjadi pusat dari rect hasil rotasi (rotated_image). Hal ini memastikan bahwa rotasi dilakukan terhadap pusat gambar 
    #     rotated_image = rotated_image.subsurface(rotated_rectangle).copy() # Mengatur pusat dari rotated_rectangle menjadi pusat dari rect hasil rotasi (rotated_image). Hal ini memastikan bahwa rotasi dilakukan terhadap pusat gambar 
    #     return rotated_image

    # rotate_center intinya buat mastiin ketika gambar nya diputar pusat rotasinya tetep dipertahanin

def run_simulation(genomes, config):
    
    # Empty Collections For Nets and Cars
    nets = [] # nets itu sebuah list yang menyimpan objek jaringan saraf yang digunakan untuk mengendalikan perilaku mobil dalam simulasi. 
    cars = []

    # Inisialisasi modul Pygame dan membuat layar dengan ukuran yang telah ditentukan
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    #-----Genomes-----#
    for i, g in genomes: # Melakukan iterasi melalui setiap genom dalam genomes,Variabel g akan mewakili genom saat ini,i diabaikan
        net = neat.nn.FeedForwardNetwork.create(g, config) # Membuat jaringan saraf feedforward baru (net) menggunakan informasi genom (g) dan konfigurasi (config). Setiap mobil dalam simulasi akan memiliki jaringan sarafnya sendiri.
        nets.append(net) # Menambahkan jaringan saraf yang baru dibuat ke dalam list nets. List ini akan menyimpan semua jaringan saraf yang digunakan untuk mengontrol mobil dalam simulasi.
        g.fitness = 0 # Mengatur nilai fitness genom saat ini menjadi 0. Nilai fitness ini akan diakumulasikan selama simulasi berjalan, tergantung seberapa baik mobil berkinerja.

        cars.append(Car()) # Menambahkan objek mobil baru (Car()) ke dalam list cars. Setiap mobil dalam simulasi akan diwakili oleh satu objek mobil.

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock() # buat mengatur kecepatan frame (60 FPS)
    generation_font = pygame.font.SysFont("Arial", 30) # gaya tulisan nampilin informasi generasi 
    alive_font = pygame.font.SysFont("Arial", 20) # gaya tulisan nampilin informasi alive
    game_map = pygame.image.load('Rute_obstacle.png').convert() # load gambar peta lintasan terus di convert() ke format yang lebih efisien untuk kecepatan pemrosesan 
    # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1 # Meningkatkan nilai variabel global current_generation sebanyak 1. Variabel ini digunakan untuk melacak generasi saat ini dalam simulasi neuroevolusi.

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Penanganan event untuk keluar dari permainan jika tombol keluar di klik
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # ---- Aksi mobil --- #
        for i, car in enumerate(cars): # terasi melalui setiap mobil dalam list cars menggunakan fungsi enumerate untuk mendapatkan indeks dan objek mobil.
            output = nets[i].activate(car.get_data()) # Mengaktifkan jaringan saraf mobil ke-i dengan memberikan data dari mobil tersebut sebagai input. Output dari jaringan saraf merupakan nilai aktivasi untuk setiap node output
            choice = output.index(max(output)) # Memilih tindakan (choice) berdasarkan indeks node output dengan nilai aktivasi maksimum
           
            # if choice == 2:
            #     if(car.speed - 2 >= 100):
            #         car.speed -= 2 # Slow Down
            # else:
            #         car.speed += 10 # Speed Up
            #         break   
            if choice == 0:
                car.angle += 10 # Left
            elif choice == 1:
                car.angle -= 10 # Right
            elif choice == 2:
                if(car.speed - 2 >= 12):
                    car.speed -= 2 # Slow Down
            else:
                car.speed += 2 # Speed Up

        #  setiap mobil dalam simulasi mengambil keputusan berdasarkan output dari jaringan sarafnya.
        
        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break
        # Jika tidak ada mobil yang masih hidup, loop utama dihentikan.

        counter += 1
        if counter == 30 * 40: # Stop After About 20 Seconds
            break

        # Menggunakan counter untuk membatasi waktu simulasi, dihentikan setelah sekitar 20 detik (30 frames/detik * 40 detik).

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)
        # Menampilkan peta dan semua mobil yang masih hidup pada layar.
        
        # Display Info
        text = generation_font.render("Generation: " + str(current_generation), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        # ini buat nampilin informasi mobil yang hidup ada berapa aja

        pygame.display.flip() # Fungsi ini digunakan untuk memperbarui tampilan pada layar. Semua perubahan yang telah dilakukan dalam satu frame diaplikasikan dan ditampilkan pada layar. Ini termasuk pergerakan objek, pembaruan skor
        clock.tick(60) # 60 FPS


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