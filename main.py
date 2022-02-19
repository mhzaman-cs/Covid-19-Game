import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vaccinator")

# Load images
covid_uk = pygame.image.load("assets/uk_var.png")
covid_sa = pygame.image.load("assets/sa_var.png")
covid_br = pygame.image.load("assets/br_var.png")

# Player player
vaccine = pygame.image.load("assets/vaccine.png")

#Vaccine Shots
shots_vaccine = pygame.image.load("assets/pixel_laser_yellow.png")

# Background
BG = pygame.transform.scale(pygame.image.load("assets/background.png"), (WIDTH, HEIGHT))

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


class moving_obj:
    COOLDOWN = 40

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.obj_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.obj_img, (self.x, self.y))
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
            laser = Laser(self.x-33, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.obj_img.get_width()

    def get_height(self):
        return self.obj_img.get_height()


class Player(moving_obj):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.obj_img = vaccine
        self.laser_img = shots_vaccine
        self.mask = pygame.mask.from_surface(self.obj_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.obj_img.get_height() + 10, self.obj_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.obj_img.get_height() + 10, self.obj_img.get_width() * (self.health/self.max_health), 10))


class Virus(moving_obj):

    COLOR_MAP = {
                "red": (covid_uk),
                "green": (covid_sa),
                "blue": (covid_br)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.obj_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.obj_img)

    def move(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():

    run = True
    FPS = 120
    level = 0
    lives = 7
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    viruses = []
    wave_length = 5
    virus_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(362, 430) #Starting point, found manually

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        level_label = main_font.render(f"Outbreak: {level}", 1, (0,0,0))
        lives_label = main_font.render(f"People Uninfected: {lives}/7", 1, (0,0,0))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for virus in viruses:
            virus.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (0,0,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > 180: # This is to make sure the game restarts after 4 seconds
                run = False
            else:
                continue

        if len(viruses) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                virus = Virus(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                viruses.append(virus)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.x - player_vel > 0: # left or
            player.x -= player_vel
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.y - player_vel > 0: # up
            player.y -= player_vel
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for virus in viruses[:]:
            virus.move(virus_vel)

            if collide(virus, player):
                player.health -= 30
                viruses.remove(virus)
            elif virus.y + virus.get_height() > 700: #Instead of using height it uses 700 to make sure the viruses stop at the people and not at the end
                lives -= 1
                viruses.remove(virus)

        player.move_lasers(-laser_vel, viruses)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        title_label = title_font.render("Press the mouse to begin...", 1, (0,0,0))
        WIN.blit(BG, (0,0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()
