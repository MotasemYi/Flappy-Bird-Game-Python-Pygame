import pygame as pg
import random
import json
import sys
from pygame.locals import *

pg.init()

# Screen setup
screen_width = 864
screen_height = 936
screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("Flappy Bird")

# Game constants
fps = 60
clock = pg.time.Clock()
font = pg.font.SysFont('Bauhaus 93', 60)
number_font = pg.font.SysFont('Arial Black', 60)  # or choose another one like 'Courier', 'Impact', etc.


white = (255, 255, 255)

# Game variables
ground_tick = 0
ground_speed = 4
pipe_gap = 180
pipe_freq = 1500
last_pipe = pg.time.get_ticks() - pipe_freq
flying = False
game_over = False
score = 0
pass_pipe = False
game_state = "menu"

def load_save():
    try:
        with open("save_data.json", "r") as f:
            return json.load(f)
    except:
        return {"best_score": 0, "selected_skin": "default", "total_score": 0}

def save_data(data):
    with open("save_data.json", "w") as f:
        json.dump(data, f)

save = load_save()
best_score = save.get("best_score", 0)
selected_skin = save.get("selected_skin", "default")
total_score = save.get("total_score", 0)

# Load images
bg_img = pg.image.load("img/bg.png")
ground_img = pg.image.load("img/ground.png")
main_menu_img = pg.image.load("img/main_menu.png")
res_button_img = pg.image.load("img/restart.png")
back_button_img = pg.image.load("img/back.png")
selected_check_img = pg.image.load("img/selected.png")
selected_check_img = pg.transform.scale(selected_check_img, (selected_check_img.get_width()*1.2 , selected_check_img.get_height() *1.2))




bg1_img = pg.image.load("img/bg1.png")
ground1_img = pg.image.load("img/ground1.png")

bg2_img = pg.image.load("img/bg2.png")
ground2_img = pg.image.load("img/ground2.png")

pipe1_img = pg.image.load("img/pipe1.png")
pipe2_img = pg.image.load("img/pipe2.png")

start_img = pg.image.load("img/start_button.png")
start_img = pg.transform.scale(start_img, (start_img.get_width() * 3, start_img.get_height() * 3))

skins_img = pg.image.load("img/skins_button.png")
skins_img = pg.transform.scale(skins_img, (skins_img.get_width() * 3, skins_img.get_height() * 3))

exit_img = pg.image.load("img/exit_button.png")
exit_img = pg.transform.scale(exit_img, (exit_img.get_width() * 3, exit_img.get_height() * 3))

lock_img = pg.image.load("img/lock.png")
lock_img = pg.transform.scale(lock_img, (lock_img.get_width() * 3, lock_img.get_height() * 3))

skins_bg = pg.image.load("img/skins_menu.png")

default_skin_img = pg.image.load("img/bird2.png")
default_skin_img = pg.transform.scale(default_skin_img, (default_skin_img.get_width() * 3, default_skin_img.get_height() * 3))

blue_skin_img = pg.image.load("img/blue_bird2.png")
blue_skin_img = pg.transform.scale(blue_skin_img, (blue_skin_img.get_width() * 3, blue_skin_img.get_height() * 3))

zbird_skin_img = pg.image.load("img/zbird2.png")
zbird_skin_img = pg.transform.scale(zbird_skin_img, (zbird_skin_img.get_width() * 3, zbird_skin_img.get_height() * 3))

# Load sounds
flap_sound = pg.mixer.Sound("sound/flap.wav")
score_sound = pg.mixer.Sound("sound/score.mp3")
death_sound = pg.mixer.Sound("sound/dead.wav")



# Change map based on score
# if the score more than 10 the bird will go to volcano map
# if the score more than 20 the will will go to space map
def change_map(score):
    global ground_speed, pipe_freq, pipe_gap
    if score >= 20:
        ground_speed = 6
        pipe_freq = 1100
        pipe_gap = 140  
        return bg2_img, ground2_img, pipe2_img
    elif score >= 10:
        ground_speed = 5
        pipe_freq = 1300
        pipe_gap = 160  
        return bg1_img, ground1_img, pipe1_img
    else:
        ground_speed = 4 # pixel per frame 
        pipe_freq = 1500 # millsecound
        pipe_gap = 180  # pixel
        return bg_img, ground_img, pg.image.load("img/pipe.png")

# Text drawing
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Button class
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pg.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

# Bird class
class Bird(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        skin_prefix = {
            "default": "bird",
            "blue": "blue_bird",
            "zbird": "zbird"
        }.get(selected_skin, "bird")

        # we have 3 images of each bird consitis 3 movment of the bird(up , down , middle)
        for i in range(1, 4):
            img = pg.image.load(f"img/{skin_prefix}{i}.png")
            self.images.append(img)

        self.index = 0
        # show the image of the bird and put it in the rectangle
        # we will controll the moving of the image by moving this rectangle
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        # default values for starting
        self.vel = 0
        self.clicked = False
        self.counter = 0

    # gravity, if we dont press the space the bird will fall to the ground
    def update(self):
        global flying, game_over
        if flying:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)
    # if the player press the sapce key the gravity will be -10 and the bird rectangle will move up 
        if not game_over:
            keys = pg.key.get_pressed()
            if keys[pg.K_SPACE] and not self.clicked:
                self.vel = -10
                flap_sound.play()
                self.clicked = True
            if not keys[pg.K_SPACE]:
                self.clicked = False

    # here we controlled the movment of the birds wings 
    # we have 3 image for each skin so we move the 3 images frequently with 
    # a time bound by a counter variable        self.counter += 1
            if self.counter > 5:
                self.counter = 0
                self.index = (self.index + 1) % len(self.images)

            self.image = pg.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pg.transform.rotate(self.images[self.index], -90)

# Pipe class
class Pipe(pg.sprite.Sprite):
    # making new pipe with constructer
    def __init__(self, x, y, position, pipe_image):
        super().__init__()
        # show the image of the pipe and put it in the rectangle
        # we will controll place of pipes by moving the rectangle
        self.image = pipe_image
        self.rect = self.image.get_rect()
        
        #to create a pipe at the top and bottom , we defined postion variable
        # if the postion is 1 we will reverse the image of the pipe so it will be
        # at the top else that it will be in the bottom

        if position == 1:
            self.image = pg.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap // 2]
        if position == -1:
            self.rect.topleft = [x, y + pipe_gap // 2]
    # the movment of pipes on the screen
    def update(self):
        self.rect.x -= ground_speed
        if self.rect.right < 0:
            # if we pass an pipe we will delete it from the memory by kill()
            self.kill()

# Reset game ,if the game is finish we will restart all game variables to default
def reset_game():
    global score, flying, flappy, bird_group
    pipe_group.empty()
    flappy = Bird(100, screen_height // 2)
    bird_group = pg.sprite.Group()
    bird_group.add(flappy)
    score = 0
    flying = False

# Unlock logic
def is_skin_unlocked(skin, best_score):
    if skin == "blue":
        return best_score >= 10
    if skin == "zbird":
        return best_score >= 20
    return True

# Skins menu
def draw_skins_menu():
    global selected_skin
    data = load_save()
    best = data.get("best_score", 0)
    selected_skin = data.get("selected_skin", "default")

    screen.blit(skins_bg, (0, 0))

    skins = [("default", default_skin_img), ("blue", blue_skin_img), ("zbird", zbird_skin_img)]
    positions = [(130, 300), (350, 300), (580, 300)]

    # Flag to control click once per press
    if not hasattr(draw_skins_menu, "clicked"):
        draw_skins_menu.clicked = False

    for i, (key, img) in enumerate(skins):
        x, y = positions[i]
        unlocked = is_skin_unlocked(key, best)
        screen.blit(img, (x, y))
        rect = pg.Rect(x, y, img.get_width(), img.get_height())

        # Draw checkmark if this is the selected skin
        if key == selected_skin:
            screen.blit(selected_check_img, (x, y))

        # Draw lock if not unlocked
        if not unlocked:
            screen.blit(lock_img, (x, y))
        else:
            if rect.collidepoint(pg.mouse.get_pos()):
                if pg.mouse.get_pressed()[0] and not draw_skins_menu.clicked:
                    selected_skin = key
                    data["selected_skin"] = selected_skin
                    save_data(data)
                    draw_skins_menu.clicked = True
            else:
                draw_skins_menu.clicked = False

    if back_button_skins.draw():
        return "menu"

    return "skins"


# Buttons 
start_button = Button(screen_width // 2 - 170, 300, start_img)
skins_button = Button(screen_width // 2 - 170, 500, skins_img)
exit_button = Button(screen_width // 2 - 170, 700, exit_img)
res_button = Button(screen_width // 2 - 50, screen_height // 2 - 100, res_button_img)
back_button = Button(screen_width // 2 - 50, screen_height // 2 + 20, back_button_img)
back_button_skins = Button(screen_width - 150, screen_height - 100, back_button_img)

# Sprite groups
bird_group = pg.sprite.Group()
pipe_group = pg.sprite.Group()

# for drawing main menu page on the screen we will use this function 
def draw_main_menu():
    screen.blit(main_menu_img, (0, 0))
    draw_text(str(best_score), number_font, white, 450, screen_height - 110)
    if start_button.draw():
        global flappy, bird_group
        flappy = Bird(100, screen_height // 2)
        bird_group = pg.sprite.Group()
        bird_group.add(flappy)
        return "playing"
    if skins_button.draw():
        return "skins"
    if exit_button.draw():
        pg.quit()
        sys.exit()
    return "menu"

# Game loop
run = True
while run:
    clock.tick(fps)
    

    # Main menu page 
    if game_state == "menu":
        game_state = draw_main_menu()

    # Skins page
    elif game_state == "skins":
        game_state = draw_skins_menu()

    #The game 
    elif game_state == "playing":
        # here the game will show the map depending on the score by get_current_assets funtion
        bg, ground, pipe_img = change_map(score)
        screen.blit(bg, (0, 0))
        pipe_group.draw(screen)
        bird_group.draw(screen)
        bird_group.update()
        screen.blit(ground, (ground_tick, 768))

        # randomly generating pipes with constant time (pipe freq)
        if not game_over:
            time_now = pg.time.get_ticks()
            if time_now - last_pipe > pipe_freq:
                pipe_height = random.randint(-100, 100)
                bottom_pipe = Pipe(screen_width, screen_height // 2 + pipe_height, -1, pipe_img)
                top_pipe = Pipe(screen_width, screen_height // 2 + pipe_height, 1, pipe_img)
                pipe_group.add(bottom_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

            #screen moving 
            ground_tick -= ground_speed
            if abs(ground_tick) > 35:
                ground_tick = 0
            pipe_group.update()

            # score +1  if the bird pass the pass the pipes
            if len(pipe_group) > 0:
                first_pipe = pipe_group.sprites()[0]
                if flappy.rect.left > first_pipe.rect.left and flappy.rect.right < first_pipe.rect.right and not pass_pipe:
                    pass_pipe = True
                if pass_pipe and flappy.rect.left > first_pipe.rect.right:
                    score += 1
                    score_sound.play()
                    pass_pipe = False

            # cheking for coll. between bird and pipes if there any coll the player lose
            if pg.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0 or flappy.rect.bottom >= 768:
                death_sound.play()
                game_over = True
        else:
            if score > best_score:
                best_score = score
            total_score += score
            # if the game finish saving the score in the file
            save_data({
                "best_score": best_score,
                "selected_skin": selected_skin,
                
            })

            # if the game finish show the restart buttun
            if res_button.draw():
                game_over = False
                reset_game()
            # if the game finish show the back buttun to back to main menu    
            if back_button.draw():
                game_state = "menu"
                game_over = False
                reset_game()
        
        # show main menu score in the screen
        draw_text(str(score), font, white, screen_width // 2, 20)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE and game_state == "playing" and not flying and not game_over:
            flying = True

    pg.display.update()

pg.quit()
