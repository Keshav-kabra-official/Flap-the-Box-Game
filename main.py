# importing modules
import random
import sys
import pygame
from pygame.locals import *

# Global Variables
FPS = 32  # frames per second
SCREENWIDTH = 700
SCREENHEIGHT = 550
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUND_Y = SCREENHEIGHT * 0.9
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/box.png'
BACKGROUND = 'gallery/bg1.png'
PIPE = 'gallery/pipe.png'

# icon of the game -- a black square showing the box
icon = pygame.image.load('gallery/icon.jpg')
pygame.display.set_icon(icon)


# pausing and un-pausing the game
# P to pause & un-pause, Q to quit game when it is paused.
def pause():
    paused = True
    font = pygame.font.SysFont(r'C:\Windows\Fonts\vgafix.fon', 60)
    text1 = font.render('Paused', True, [255, 0, 0], [0, 0, 0])
    text1_rect = text1.get_rect()
    text1_rect.center = (SCREENWIDTH // 2 - 40, 470)
    SCREEN.blit(text1, text1_rect)

    font = pygame.font.SysFont(r'C:\Windows\Fonts\vgafix.fon', 36)
    text2 = font.render('Press P to continue and Q to quit', True, [255, 0, 0], [0, 0, 0])
    text2_rect = text1.get_rect()
    text2_rect.center = (SCREENWIDTH // 2 - 150, 510)
    SCREEN.blit(text2, text2_rect)

    pygame.display.update()

    while paused:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_p:
                    GAME_SOUNDS['pause'].play()
                    paused = False
                elif event.key == K_q:
                    pygame.quit()
                    sys.exit()
        FPS_CLOCK.tick(5)  # while screen is paused, the FPS is set to be 5 instead of 32.


# Generating random pipes
def get_random_pipe(score):
    pipe_height = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 2  # making distance between pipes... declare here to avoid warnings

    # Setting the gap between pipes as per the level
    if 0 <= score < 10:
        offset = SCREENHEIGHT/1.9
    elif 10 <= score < 20:
        offset = SCREENHEIGHT/2.6
    elif 20 <= score < 30:
        offset = SCREENHEIGHT/2.9
    elif 30 <= score < 40:
        offset = SCREENHEIGHT/3.4
    elif 40 <= score < 50:
        offset = SCREENHEIGHT/3.7
    elif 50 <= score < 60:
        offset = SCREENHEIGHT/4
    elif 60 <= score < 70:
        offset = SCREENHEIGHT/4.2
    elif 70 <= score < 80:
        offset = SCREENHEIGHT/4.6
    elif 80 <= score < 90:
        offset = SCREENHEIGHT/5

    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 0.9*offset))
    pipe_x = SCREENWIDTH + 10  # making pipe on right of game-screen
    y1 = pipe_height - y2 + offset  # making upper pipe such that there is (offset) distance between lower & upper pipes

    pipe = [
        {'x': pipe_x, 'y': -y1},  # upper pipe
        {'x': pipe_x, 'y': y2}    # lower pipe
    ]
    return pipe


# checking if box touched with pipe or upper/lower borders
def is_collide(player_x, player_y, upper_pipes, lower_pipes):
    if player_y > GROUND_Y - 62 or player_y < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upper_pipes:
        pipe_height = GAME_SPRITES['pipe'][0].get_height()
        if player_y < pipe_height + pipe['y'] and abs(player_x-pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lower_pipes:
        if player_y+GAME_SPRITES['player'].get_height() > pipe['y'] and \
                abs(player_x-pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True
    return False  # box has not been crashed yet


# message screen before the game starts
def welcome_screen():
    player_x = SCREENWIDTH//5
    player_y = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/1.3)
    message_x = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    message_y = int(SCREENWIDTH * 0.13)
    base_x = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.type == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return  # starting of main game
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (player_x, player_y))
                SCREEN.blit(GAME_SPRITES['message'], (message_x, message_y))
                SCREEN.blit(GAME_SPRITES['base'], (base_x, GROUND_Y))
                pygame.display.update()
                FPS_CLOCK.tick(FPS)


# main-game code here
def main_game():
    # extracting highest score from the scores.txt file
    scr_lst = []
    with open("scores.txt", "r") as f:
        scr_lst += f.read().split('\n')
    scr_lst.pop()  # popping the last '\n' from the file
    scr_lst = [int(i) for i in scr_lst]  # converting str-list to int-list
    max_score = max(scr_lst)

    score = 0
    player_x = SCREENWIDTH//5  # displaying box on the screen ( initial position of box when game starts)
    player_y = SCREENWIDTH//2 - 50
    base_x = 0

    # getting random pipes
    new_pipe_1 = get_random_pipe(score)
    new_pipe_2 = get_random_pipe(score)

    # upper pipe
    upper_pipes = [
        {'x': SCREENWIDTH+200, 'y': new_pipe_1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y': new_pipe_2[0]['y']}
    ]
    # lower pipe
    lower_pipes = [
        {'x': SCREENWIDTH + 200, 'y': new_pipe_1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': new_pipe_2[1]['y']}
    ]

    pipe_vel_x = -12  # moving pipes opposite to bird

    player_vel_y = -4  # box will fall down, to base, with this velocity
    player_max_vel_y = 10  # higher value => less time to fall on ground
    # player_min_vel_y = -8
    player_accel_y = 1  # acceleration when box is falling down

    player_flap_acc_v = -8  # on one flap how high the box will jump
    player_flapped = False  # turns True if box is flapping

    while True:
        # checking which key was pressed
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.type == K_ESCAPE):
                # print(f"\nF score = {score}") -- not writing score in file here
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if player_y > 0:  # bird is inside screen
                    player_vel_y = player_flap_acc_v
                    player_flapped = True
                    GAME_SOUNDS['wing'].play()

            if event.type == KEYDOWN and event.key == K_p:
                GAME_SOUNDS['pause'].play()
                pause()

        # checking if box has been collided
        crash_test = is_collide(player_x, player_y, upper_pipes, lower_pipes)
        if crash_test:
            # printing final score on console and writing the same  in scores.txt
            print(f"\nFinal Score = {score}")
            with open("scores.txt", "a") as f:
                f.write(str(score) + "\n")

            # showing a tkinter window if score made is the highest score of all times
            if score >= max_score:
                import tkinter
                from tkinter import messagebox
                root = tkinter.Tk()
                root.withdraw()  # removing Tk() window
                messagebox.showinfo("Flap-the-Box", f"Congratulations! {score} is the new highest score.")
            return  # returning when bird is crashed

        # score
        player_mid_pos = player_x + GAME_SPRITES['player'].get_width()/2
        for pipe in upper_pipes:
            pipe_mid_pos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2

            if pipe_mid_pos <= player_mid_pos < pipe_mid_pos + abs(pipe_vel_x):
                score += 1

                if score % 30 == 0:  # major-level-up
                    GAME_SOUNDS['level-30s'].play()
                    font = pygame.font.SysFont(r'C:\Windows\Fonts\vgafix.fon', 36)
                    text = font.render('Major - Level - Up', True, [255, 0, 0], [0, 0, 0])
                    text_rect = text.get_rect()
                    text_rect.center = (SCREENWIDTH//2, SCREENHEIGHT//2 - 50)
                    SCREEN.blit(text, text_rect)
                    pygame.display.update()
                    pygame.time.delay(700)

                elif score % 10 == 0:  # level-up
                    GAME_SOUNDS['level-up'].play()
                    # SCREEN.blit(pygame.image.load('gallery/lvl-up.png').convert(), (70, 10))
                    font = pygame.font.SysFont(r'C:\Windows\Fonts\vgafix.fon', 36)
                    text = font.render('Level - Up', True, [255, 0, 0], [0, 0, 0])
                    text_rect = text.get_rect()
                    text_rect.center = (SCREENWIDTH//2, SCREENHEIGHT//2 - 50)
                    SCREEN.blit(text, text_rect)
                    pygame.display.update()
                    pygame.time.delay(700)

                else:
                    GAME_SOUNDS['point'].play()

                # making changes in background and speed of pipes with each level
                global BACKGROUND
                if 10 <= score < 20:
                    pipe_vel_x = -5
                    BACKGROUND = 'gallery/bg2.png'
                    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
                elif 20 <= score < 30:
                    pipe_vel_x = -6
                    BACKGROUND = 'gallery/bg3.png'
                    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
                elif 30 <= score < 40:
                    pipe_vel_x = -8
                    BACKGROUND = 'gallery/bg4.png'
                    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
                elif 40 <= score < 50:
                    pipe_vel_x = -8
                    BACKGROUND = 'gallery/bg5.png'
                    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
                elif 50 <= score < 60:
                    pipe_vel_x = -7
                    BACKGROUND = 'gallery/bg6.png'
                    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
                elif 60 <= score < 70:
                    pipe_vel_x = -7
                    BACKGROUND = 'gallery/bg7.png'
                    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
                elif 70 <= score < 80:
                    pipe_vel_x = -7
                    BACKGROUND = 'gallery/bg8.png'
                    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
                elif 80 <= score < 90:
                    pipe_vel_x = -9
                    BACKGROUND = 'gallery/bg9.png'
                    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
                if score >= 10 and score % 10 == 0:
                    pipe_vel_x = -4  # making speed of pipes slower after displaying Level-Up msg

        if player_vel_y < player_max_vel_y and not player_flapped:
            player_vel_y += player_accel_y

        if player_flapped:
            player_flapped = False

        player_height = GAME_SPRITES['player'].get_height()
        player_y += min(player_vel_y, GROUND_Y - player_y - player_height)  # bird not go inside the base/ground

        # moving pipes to the left
        for upperPipe, lowerPipe in zip(upper_pipes, lower_pipes):
            upperPipe['x'] += pipe_vel_x
            lowerPipe['x'] += pipe_vel_x
            # pipe_vel_x is negative, thus by adding it -- pipes will move towards left

        # Adding a new pipe before any pair of pipes is about to leave screen
        if 0 < upper_pipes[0]['x'] < abs(pipe_vel_x)+1:
            new_pipe = get_random_pipe(score)
            upper_pipes.append(new_pipe[0])
            lower_pipes.append(new_pipe[1])

        # removing pipes when they are out of the screen
        if upper_pipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upper_pipes.pop(0)
            lower_pipes.pop(0)

        # blit all the sprites
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upper_pipes, lower_pipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))
        SCREEN.blit(GAME_SPRITES['base'], (base_x, GROUND_Y))
        SCREEN.blit(GAME_SPRITES['player'], (player_x, player_y))
        # blitting score
        my_score = [int(x) for x in list(str(score))]
        width = 0
        for digit in my_score:
            width += GAME_SPRITES['numbers'][digit].get_width()
        x_offset = (SCREENWIDTH - width)/2  # scores at centre of screen
        for digit in my_score:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (x_offset, SCREENHEIGHT*0.12))
            x_offset += GAME_SPRITES['numbers'][digit].get_width()  # making score digits adjacent to each other

        # blitting the highest score at bottom-right of game window
        font = pygame.font.SysFont(r'C:\Windows\Fonts\vgafix.fon', 28)
        text = font.render(f'HS : {max_score}', True, [255, 0, 0], [0, 0, 0])
        text_rect = text.get_rect()
        text_rect.center = (665, 535)  # 700, 550
        SCREEN.blit(text, text_rect)

        pygame.display.update()
        FPS_CLOCK.tick(FPS)


# the main function
if __name__ == '__main__':
    pygame.init()
    FPS_CLOCK = pygame.time.Clock()
    pygame.display.set_caption("Flap-the-Box")  # title of the game window
    # initialization for the numbers for score
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/0.png').convert_alpha(),
        pygame.image.load('gallery/1.png').convert_alpha(),
        pygame.image.load('gallery/2.png').convert_alpha(),
        pygame.image.load('gallery/3.png').convert_alpha(),
        pygame.image.load('gallery/4.png').convert_alpha(),
        pygame.image.load('gallery/5.png').convert_alpha(),
        pygame.image.load('gallery/6.png').convert_alpha(),
        pygame.image.load('gallery/7.png').convert_alpha(),
        pygame.image.load('gallery/8.png').convert_alpha(),
        pygame.image.load('gallery/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/msg.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
        pygame.image.load(PIPE).convert_alpha()
    )

    # Game Sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound("sounds/die.wav")
    GAME_SOUNDS['hit'] = pygame.mixer.Sound("sounds/hit.wav")
    GAME_SOUNDS['pause'] = pygame.mixer.Sound("sounds/pause.wav")
    GAME_SOUNDS['point'] = pygame.mixer.Sound("sounds/point.wav")
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound("sounds/swoosh.wav")
    GAME_SOUNDS['wing'] = pygame.mixer.Sound("sounds/wing.wav")
    GAME_SOUNDS['level-up'] = pygame.mixer.Sound("sounds/level-up.wav")
    GAME_SOUNDS['level-30s'] = pygame.mixer.Sound("sounds/level-30s.wav")

    # GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert()

    # the game-loop
    while True:
        BACKGROUND = 'gallery/bg1.png'
        GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
        welcome_screen()
        main_game()
