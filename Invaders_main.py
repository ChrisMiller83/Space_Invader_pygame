import pygame
import os
import time
import random
pygame.mixer.init()
pygame.font.init()

WIDTH, HEIGHT = 900, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Shooter")

#Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255,0)
BLUE = (0, 0, 255)
TEAL = (0, 255,255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

#Define the spaceship image's width and height
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 70, 70

# Background and sound
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space.png")), (WIDTH, HEIGHT))
BG_SOUND = pygame.mixer.Sound(os.path.join("assets", "Vilified.mp3"))

# Player 
PLAYER_SPACESHIP_IMAGE = pygame.image.load(os.path.join("assets", "J-10.png"))
PLAYER_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(PLAYER_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 180)
# Load images
RED_ENEMY_SPACESHIP_IMAGE = pygame.image.load(os.path.join("assets", "A-02.png"))
RED_ENEMY_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_ENEMY_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 180)
GREEN_ENEMY_SPACESHIP_IMAGE = pygame.image.load(os.path.join("assets", "C-11.png"))
GREEN_ENEMY_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(GREEN_ENEMY_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 180)
BLUE_ENEMY_SPACESHIP_IMAGE = pygame.image.load(os.path.join("assets", "G-14.png"))
BLUE_ENEMY_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(BLUE_ENEMY_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 180)
# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

def pause():
    paused = True
    pause_font = pygame.font.SysFont("comicsans", 70)
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    paused = False
                elif event.key == pygame.K_q:
                    pygame.quit()    
                    quit()
        WIN.blit(BG, (0, 0))
        pause_label = pause_font.render("PAUSED", 1, (TEAL))
        WIN.blit(pause_label, (WIDTH/2 - pause_label.get_width()/2, 350))
        pause_label_2 = pause_font.render("Press c to Continue or q to Quit", 1, (TEAL))
        WIN.blit(pause_label_2, (WIDTH/2 - pause_label_2.get_width()/2, 550))
        pygame.display.update()                    
        pygame.time.delay(100)

class Ship: #Crates a parent class Ship
    COOLDOWN = 10
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Enemy(Ship): #Inherits attributes from the parent Ship class
    #Create a color list for the enemy ships
    Enemy_Colors = {
                "red": (RED_ENEMY_SPACESHIP, RED_LASER),
                "green": (GREEN_ENEMY_SPACESHIP, GREEN_LASER),
                "blue": (BLUE_ENEMY_SPACESHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.Enemy_Colors[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel): #moves enemy ship down 
        self.y += vel

    def shoot(self): #Creates a cool down counter and creates a new shot once cooldown counter resets
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2): #Creates a mask to define the pixels of the objects for hit markers
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

class Player(Ship): #Inherits attributes from the parent Ship class  
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER_SPACESHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) #defines which pixels are the ship for collision events
        self.max_health = health

    def move_lasers(self, vel, objects): #shoots lasers and registers hits 
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objects:
                    if laser.collision(obj):                        
                        objects.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (RED), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (GREEN), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

 
def main():
    run = True
    FPS = 60
    level = 0 #starting level
    lives = 1 #number of lives a player
    score = 0
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = [] #list stores all enemies
    wave_length = 5 #enemies per level
    enemy_vel = 1 #enemy speed

    player_vel = 10 #how fast a player can move
    laser_vel = 8 #how fast the lasers move

    player = Player(300, 630) #player start position on screen

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0
    
    

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (TEAL))
        level_label = main_font.render(f"Level: {level}", 1, (TEAL))
        score_label = main_font.render(f"Score: {score}", 1, (TEAL))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (WIDTH / 2 - score_label.get_width(), 10))
                
        for enemy in enemies:
            enemy.draw(WIN) #Draws enemies on screen from Ship class

        player.draw(WIN)

        if lost: #If player dies prints You Lost in the center of the screen
            lost_label = lost_font.render("You Lost!!", 1, (WHITE))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
   
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost: #Shows you lost for 3 seconds then restarts the game
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0: #Once all enemies are gone
            level += 1 #Level increases
            wave_length += 10 #Increases 10 enemies per level
            player.health = 100 #Players health returns at new level
            lives += 1
           
            for i in range(wave_length): #Spawns all the enemies at once but some are higher up off screen
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-3000 * level / 5, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy) 
            for enemy in enemies:                
                score += 25

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # move left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # move right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # move up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # move down
            player.y += player_vel
        if keys[pygame.K_SPACE]: #shoot lasers
            player.shoot()
        if keys[pygame.K_p]:
            pause()     
                
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player): #If you run into an enemy you lose health and enemy disappears
                player.health -= 10
                score -= 25
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT: #If enemy goes below player screen you lose a life
                lives -= 1
                score -= 100
                enemies.remove(enemy)

        player.move_lasers(-laser_vel, enemies)
        BG_SOUND.play(loops=5)   
 
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True

    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (TEAL))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        controls_label1 = title_font.render("Move: Arrow Keys", 1, (TEAL))
        WIN.blit(controls_label1, (WIDTH/2 - controls_label1.get_width()/2, 500))
        controls_label2 = title_font.render("Shoot: Spacebar", 1, (TEAL))
        WIN.blit(controls_label2, (WIDTH/2 - controls_label2.get_width()/2, 600))
        controls_label3 = title_font.render("Pause Game: P", 1, (TEAL))
        WIN.blit(controls_label3, (WIDTH/2 - controls_label2.get_width()/2, 700)) 
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()


