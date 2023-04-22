import pygame
import neat
import os
import random
import sys
import math

FPS = 60
stage = 1

# Window dimensions
WIN_WIDTH = 650
WIN_HEIGHT = 1150
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
FLOOR = 1000

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)


# Load images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dfhalf.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dfhalf.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "dfhalf.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", f"pipeBottom_stage{stage}.png")))
PIPE_BOTTOM = PIPE_IMG
#PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", f"fground_stage{stage}.png")).convert())
BG_IMG = pygame.image.load(os.path.join("imgs", f"bg_stage{stage}.png")).convert()
FART_IMGS = [pygame.image.load(os.path.join("imgs", "cloud_1.png")),
             pygame.image.load(os.path.join("imgs", "PinkCloudS.png")),
             pygame.image.load(os.path.join("imgs", "PinkCloudS.png"))]


gen = 0  # Initialize the generation counter
DRAW_LINES = True

class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.angle = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        self.fart_count = 0  # farts - Initialize the fart counter
        self.fart_imgs = FART_IMGS  # farts - Set the fart images
        self.active_farts = []  # farts - Initialize the list of active farts

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        # Calculate displacement
        d = self.vel * self.tick_count + 1.5 * self.tick_count**2

        # Set terminal velocity
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def fart(self):
        #change angle of fart
        self.active_farts.append(Fart(self.x - 20, self.y + 20, 35))

    def draw_farts(self, win):
        # update list of active farts
        for fart in self.active_farts:
            if fart.is_faded():
                self.active_farts.remove(fart)  # remove fart if it has completely faded away

        # draw remaining active farts
        for fart in self.active_farts:
            fart.draw(win)  # pass bird's position to fart's draw method

class Fart:
    def __init__(self, bird_x, bird_y, angle):
        self.x = bird_x - 0 * math.cos(math.radians(angle)) # move fart closer death
        self.y = bird_y + 20 - 60 * math.sin(math.radians(angle))
        self.imgs = FART_IMGS
        self.img_count = 0
        self.img = self.imgs[0]
        self.timer = 0  # initialize timer to 0
        self.fade_time = 1.0  # set fade time to 1 second
        self.opacity = 1.0  # initialize opacity to 100%
        self.angle = angle

        # calculate horizontal and vertical components of velocity based on angle and launch speed
        launch_speed = 10.0
        angle_rad = math.radians(angle)
        self.vx = launch_speed * math.cos(angle_rad)
        self.vy = -launch_speed * math.sin(angle_rad)

    def draw(self, win):
        # calculate time since last frame
        dt = 1 / FPS

        # update position based on velocity
        self.x += self.vx * dt
        self.y += self.vy * dt

        # update opacity based on time elapsed
        self.opacity -= dt / self.fade_time
        if self.opacity < 0:
            self.opacity = 0

        # set image alpha and draw on window
        alpha = int(255 * self.opacity)
        rotated_img = pygame.transform.rotate(self.img, self.angle)
        rotated_img.set_alpha(alpha)
        win.blit(rotated_img, (self.x, self.y))

        # cycle through fart images
        self.img_count += 1
        if self.img_count < 5:
            self.img = self.imgs[0]
        elif self.img_count < 10:
            self.img = self.imgs[1]
        elif self.img_count < 15:
            self.img = self.imgs[2]
        else:
            self.img_count = 0

    def is_faded(self):
        # check if fart has completely faded away
        return self.opacity <= 0

class Pipe:
    #values below are to change obstacle 
    GAP = 315
    VEL = 5.65

    def __init__(self, x, stage):
        self.x = x
        self.height = 0
        # alter gap between obstacles
        self.gap = 315
        self.top = 0
        self.bottom = 0
        self.PIPE_BOTTOM = pygame.image.load(os.path.join("imgs", f"pipeBottom_stage{stage}.png")).convert_alpha()
        self.PIPE_TOP = pygame.transform.flip(self.PIPE_BOTTOM, False, True)
        self.passed = False
        self.set_height()
        self.stage = stage

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y, stage):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        self.IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", f"fground_stage{stage}.png")).convert())

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

class Background:
    VEL = 1

    def __init__(self, stage):
        self.stage = stage
        self.BG_IMG = pygame.image.load(os.path.join("imgs", f"bg_stage{stage}.png")).convert()
        self.WIDTH = self.BG_IMG.get_width()
        self.HEIGHT = self.BG_IMG.get_height()
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.BG_IMG, (self.x1, 0))
        win.blit(self.BG_IMG, (self.x2, 0))

def draw_window(win, birds, pipes, base, background, score, gen, pipe_ind, draw_lines=True):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    if gen == 0:
        gen = 1

    background.draw(win)  # Draw the scrolling background

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        bird.draw(win)
        bird.draw_farts(win)
        if draw_lines:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass

    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()

def get_current_stage(score):
    if score < 10:
        return 1
    elif score < 20:
        return 2
    elif score < 30:
        return 3
    else:
        return 3

def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    score = 0
    stage = get_current_stage(score)
    base = Base(FLOOR, stage)
    background = Background(stage)
    pipes = [Pipe(WIN_WIDTH, stage)]

	# Create a clock object before the game loop begins
    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(60) # set fps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
                pipe_ind = 1                                                                 # pipe on the screen for neural network input

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            # 3. farts - Pass delta_time to the bird's draw method
            #bird.draw(WIN, delta_time)

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()


        base.move()
        background.move() # Update the scrolling background

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            for genome in ge:
                genome.fitness += 5

            new_stage = get_current_stage(score)
            if new_stage != stage:
                stage = new_stage
                background = Background(stage)

            pipes.append(Pipe(WIN_WIDTH, stage))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, background, score, gen, pipe_ind)

        # break if score gets large enough
        '''if score > 20:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break'''


def run_game(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))



def start_menu():
    menu_image = pygame.image.load(os.path.join("imgs", "DFMenuFinal.png"))    
    screen_width, screen_height = WIN.get_size()
    image_width, image_height = menu_image.get_size()
    x = (screen_width - image_width) // 2
    y = (screen_height - image_height) // 2

    run = True
    while run:
        WIN.blit(menu_image, (x, y))

        button_font = pygame.font.SysFont("comicsans", 40)
        manual_button = button_font.render("Play Manually", 1, (0, 0, 0))
        ai_button = button_font.render("Watch AI", 1, (0, 0, 0))
        WIN.blit(manual_button, (WIN_WIDTH // 2 - manual_button.get_width() // 2, 350))
        WIN.blit(ai_button, (WIN_WIDTH // 2 - ai_button.get_width() // 2, 450))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if (WIN_WIDTH // 2 - manual_button.get_width() // 2 <= mouse_x <= WIN_WIDTH // 2 + manual_button.get_width() // 2) and (350 <= mouse_y <= 390):
                    run = False
                    manual_play()
                elif (WIN_WIDTH // 2 - ai_button.get_width() // 2 <= mouse_x <= WIN_WIDTH // 2 + ai_button.get_width() // 2) and (450 <= mouse_y <= 490):
                    run = False
                    local_dir = os.path.dirname(__file__)
                    config_path = os.path.join(local_dir, 'config-feedforward.txt')
                    run_game(config_path)

def manual_play():
    bird = Bird(230, 350)
    score = 0

    stage = get_current_stage(score)
    base = Base(FLOOR, stage)
    background = Background(stage)
    pipes = [Pipe(WIN_WIDTH, stage)]

    clock = pygame.time.Clock()
    win = WIN

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                        bird.jump()
                        bird.fart()

        bird.move()
        base.move()
        background.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            if pipe.collide(bird):
                running = False

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            pipes.append(Pipe(WIN_WIDTH, stage))

            new_stage = get_current_stage(score)
            if new_stage != stage:
                stage = new_stage
                background = Background(stage)

        for r in rem:
            pipes.remove(r)

        if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
            game_over_screen(score)

        draw_window(win, [bird], pipes, base, background, score, 0, 0, draw_lines=False)

    print("Game Over!")

def game_over_screen(score):
    """
    Displays the game over screen and waits for 3 seconds before returning to the start menu
    :param score: the final score of the game
    """
    font = pygame.font.SysFont("comicsans", 80)
    text = font.render("Game Over", 1, (255, 255, 255))
    score_text = font.render("Score: " + str(score), 1, (255, 255, 255))

    WIN.fill((0, 0, 0))
    WIN.blit(text, (WIN_WIDTH / 2 - text.get_width() / 2, WIN_HEIGHT / 2 - text.get_height()))
    WIN.blit(score_text, (WIN_WIDTH / 2 - score_text.get_width() / 2, WIN_HEIGHT / 2))
    pygame.display.update()

    # Wait for 3 seconds
    pygame.time.delay(3000)

    # Return to the start menu
    start_menu()

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    start_menu()
