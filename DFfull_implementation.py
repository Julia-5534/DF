# Import module
import random
import sys
import pygame
from pygame.locals import *

# All the Game Variables
window_width = 600
window_height = 499

# set height and width of window
window = pygame.display.set_mode((window_width, window_height))
elevation = window_height * 0.8
game_images = {}
framepersecond = 32
spikeimage = 'images/spike.png'
background_image = 'images/background.jpg'
dfplayer_image = 'images/df.png'
foreground_image = 'images/foreground.jfif'


def dfgame():
    """Death Farts Game"""
    your_score = 0
    horizontal = int(window_width/5)
    vertical = int(window_width/2)
    ground = 0
    mytempheight = 100
    first_spike = createSpike()
    second_spike = createSpike()

    down_spikes = [
        {'x': window_width+300-mytempheight,
         'y': first_spike[1]['y']},
        {'x': window_width+300-mytempheight+(window_width/2),
         'y': second_spike[1]['y']},
    ]

    up_spikes = [
        {'x': window_width+300-mytempheight,
         'y': first_spike[0]['y']},
        {'x': window_width+200-mytempheight+(window_width/2),
         'y': second_spike[0]['y']},
    ]

    pipeVelX = -4

    df_velocity_y = -9
    df_Max_Vel_Y = 10
    df_Min_Vel_Y = -8
    dfAccY = 1

    df_fart_velocity = -8
    df_farted = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and
                                      event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or
                                          event.key == K_UP):
                if vertical > 0:
                    df_velocity_y = df_fart_velocity
                    df_farted = True

        game_over = isGameOver(horizontal,
                               vertical,
                               up_spikes,
                               down_spikes)
        if game_over:
            return

        playerMidPos = horizontal + game_images['death_farter'].get_width()/2
        for spike in up_spikes:
            spikeMidPos = spike['x'] + game_images['spikeimage'][0].get_width()/2
            if spikeMidPos <= playerMidPos < spikeMidPos + 4:
                your_score += 1
                print(f"Your your_score is {your_score}")

            if df_velocity_y < df_Max_Vel_Y and not df_farted:
                df_velocity_y += dfAccY

            if df_farted:
                df_farted = False
            playerHeight = game_images['death_farter'].get_height()
            vertical = vertical + \
                min(df_velocity_y, elevation - vertical - playerHeight)

            # move pipes to the left
            for upperSpike, lowerSpike in zip(up_spikes, down_spikes):
                upperSpike['x'] += pipeVelX
                lowerSpike['x'] += pipeVelX

            # Add a new pipe when the first is
            # about to cross the leftmost part of the screen
            if 0 < up_spikes[0]['x'] < 5:
                newspike = createSpike()
                up_spikes.append(newspike[0])
                down_spikes.append(newspike[1])

            # if the pipe is out of the screen, remove it
            if up_spikes[0]['x'] < -game_images['spikeimage'][0].get_width():
                up_spikes.pop(0)
                down_spikes.pop(0)

            # Lets blit our game images now
            window.blit(game_images['background'], (0, 0))
            for upperSpike, lowerSpike in zip(up_spikes, down_spikes):
                window.blit(game_images['spikeimage'][0],
                            (upperSpike['x'], upperSpike['y']))
                window.blit(game_images['spikeimage'][1],
                            (lowerSpike['x'], lowerSpike['y']))

        window.blit(game_images['foreground'], (ground, elevation))
        window.blit(game_images['death_farter'], (horizontal, vertical))

        numbers = [int(x) for x in list(str(your_score))]
        width = 0

        for num in numbers:
            width += game_images['scoreimages'][num].get_width()
            Xoffset = (window_width - width)/1.1

            for num in numbers:
                window.blit(game_images['scoreimages'][num],
                            (Xoffset, window_width*0.02))
                Xoffset += game_images['scoreimages'][num].get_width()

        pygame.display.update()
        framepersecond_clock.tick(framepersecond)


def isGameOver(horizontal, vertical, up_spikes, down_spikes):
    if vertical > elevation - 25 or vertical < 0:
        return True

    for spike in up_spikes:
        spikeHeight = game_images['spikeimage'][0].get_height()
        if(vertical < spikeHeight + spike['y'] and
           abs(horizontal - spike['x']) <
           game_images['spikeimage'][0].get_width()):
            return True

    for spike in down_spikes:
        if (vertical + game_images['death_farter'].get_height() >
            spike['y']) and abs(horizontal - spike['x']) < game_images['spikeimage'][0].get_width():
            return True
    return False


def createSpike():
    offset = window_height/3
    spikeHeight = game_images['spikeimage'][0].get_height()
    y2 = offset + \
		random.randrange(
			0, int(window_height - game_images['foreground'].get_height() - 1.2 * offset))
    SpikeX = window_width + 10
    y1 = spikeHeight - y2 + offset
    spike = [
		# upper Spike
		{'x': SpikeX, 'y': -y1},

		# lower Spike
		{'x': SpikeX, 'y': y2}
	]
    return spike


# program where the game starts
if __name__ == "__main__":

		# For initializing modules of pygame library
	pygame.init()
	framepersecond_clock = pygame.time.Clock()

	# Sets the title on top of game window
	pygame.display.set_caption('Death Farts')

	# Load all the images which we will use in the game

	# images for displaying score
	game_images['scoreimages'] = (
		pygame.image.load('images/0.png').convert_alpha(),
		pygame.image.load('images/1.png').convert_alpha(),
		pygame.image.load('images/2.png').convert_alpha(),
		pygame.image.load('images/3.png').convert_alpha(),
		pygame.image.load('images/4.png').convert_alpha(),
		pygame.image.load('images/5.png').convert_alpha(),
		pygame.image.load('images/6.png').convert_alpha(),
		pygame.image.load('images/7.png').convert_alpha(),
		pygame.image.load('images/8.png').convert_alpha(),
		pygame.image.load('images/9.png').convert_alpha()
	)
	game_images['death_farter'] = pygame.image.load(
		dfplayer_image).convert_alpha()
	game_images['foreground'] = pygame.image.load(
		foreground_image).convert_alpha()
	game_images['background'] = pygame.image.load(
		background_image).convert_alpha()
	game_images['spikeimage'] = (pygame.transform.rotate(pygame.image.load(
		spikeimage).convert_alpha(), 180), pygame.image.load(
        spikeimage).convert_alpha())

	print("WELCOME TO DEATH FARTS")
	print("Press space or enter to start the game")

	# Here starts the main game

	while True:

		# sets the coordinates of Death Farter

		horizontal = int(window_width/5)
		vertical = int(
			(window_height - game_images['death_farter'].get_height())/2)
		ground = 0
		while True:
			for event in pygame.event.get():

				# if user clicks on cross button, close the game
				if event.type == QUIT or (event.type == KEYDOWN and
                                          event.key == K_ESCAPE):
					pygame.quit()
					sys.exit()

				# If the user presses space or
				# up key, start the game for them
				elif event.type == KEYDOWN and (event.key == K_SPACE or
												event.key == K_UP):
					dfgame()

				# if user doesn't press anykey Nothing happen
				else:
					window.blit(game_images['background'], (0, 0))
					window.blit(game_images['death_farter'],
                                (horizontal, vertical))
					window.blit(game_images['foreground'], (ground, elevation))
					pygame.display.update()
					framepersecond_clock.tick(framepersecond)
