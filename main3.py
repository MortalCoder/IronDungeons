# TODO:
#      structurize the settings and make them more flexible - DONE
#      add tile loading function
#      use the tiles on the map
#      deal with the border-error - DONE
#      add chests and/or coins
import random
import sys

import pygame
import numpy as np
import scipy as sp

# prf stands for preferences
prf = {'MAP': None, 'BORDER_VALUE': 75, 'VIEW_SIZE': (38, 24), 'VIEW_BORDER': (6, 4), 'DEFAULT_MAP_SIZE': (38 * 5+1, 24 * 5+1)}
screen = pygame.display.set_mode((prf['VIEW_SIZE'][0] * 32, prf['VIEW_SIZE'][1] * 32))

tiles = {'solid': [], 'bg': []}


def load_tiles():
    global tiles
    for i in range(16):
        tiles['solid'].append(pygame.image.load(f'sprites/new_tileset/tile{i}.png').convert())
    for i in range(10):
        tiles['bg'].append(pygame.image.load(f'sprites/bg_tileset/bg_tile{i}.png').convert())
    tiles['bg'].extend([tiles['bg'][0] for i in range(3)])


load_tiles()


def check_pos(x, y):
    if view_map[y][x] >= prf['BORDER_VALUE'] or view_map[y][x] == 0:
        bit_mask = (bool(view_map[y-1][x] >= prf['BORDER_VALUE']) if 0 < y - 1 else game_map[player.global_pos[1]+y-1] \
                                                                                    [player.global_pos[0]+x] >= prf['BORDER_VALUE'],
                    bool(view_map[y][x - 1] >= prf['BORDER_VALUE']) if 0 < x - 1 else game_map[player.global_pos[1]+y] \
                                                                                            [player.global_pos[0]+x-1] >= prf['BORDER_VALUE'],
                    bool(view_map[y][x + 1] >= prf['BORDER_VALUE']) if x + 1 < prf['VIEW_SIZE'][0] else game_map[player.global_pos[1]+y] \
                                                                                            [player.global_pos[0]+x+1] >= prf['BORDER_VALUE'],
                    bool(view_map[y + 1][x] >= prf['BORDER_VALUE']) if y + 1 < prf['VIEW_SIZE'][1] else game_map[player.global_pos[1]+y+1] \
                                                                                            [player.global_pos[0]+x] >= prf['BORDER_VALUE'])
        return tiles['solid'][1*bit_mask[0] + 2*bit_mask[1] + 4*bit_mask[2] + 8*bit_mask[3]]
    elif 0 < view_map[y][x] < prf['BORDER_VALUE']:
        return tiles['bg'][int(view_map[y][x]) // int(prf['BORDER_VALUE'])//len(tiles['bg'])]


def generate_map(width, height, bd=20, m=101):
    # Making blank matrix fulled with 0s
    temp_map = np.full((height+bd, width+bd), 0)
    # Creates an inbound matrix filled with 100s
    temp_map[bd: height - bd,
             bd: width - bd] = np.full((height - 2*bd, width - 2*bd), 100)

    #temp_map[bd: height - bd,
    #         bd: width - bd] = sp.signal.sepfir2d(np.random.randint(0, 100),
    #                                     sp.signal.windows.gaussian(m, 1), sp.signal.windows.gaussian(1, m))
    temp_map[bd: height - bd,
             bd: width - bd] = sp.signal.sepfir2d(
        np.random.randint(0, 100, (prf['DEFAULT_MAP_SIZE'][1] - 2*bd,
                                   prf['DEFAULT_MAP_SIZE'][0] - 2*bd)),
        sp.signal.windows.gaussian(m, 1), sp.signal.windows.gaussian(1, m))
    prf['BORDER_VALUE'] = np.max(temp_map) * 0.65

    return temp_map


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # self.image = pygame.image.load('sprites/player.png').convert_alpha()
        # self.image = pygame.transform.scale2x(self.image)
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 30, 30))
        self.x, self.y = prf['VIEW_SIZE'][0] // 2, prf['VIEW_SIZE'][1] // 2
        self.global_pos = [prf['DEFAULT_MAP_SIZE'][0] // 2, prf['DEFAULT_MAP_SIZE'][1] // 2]

        self.rect = self.image.get_rect(topleft=(self.x*32, self.y*32))

        self.strength = 0
        self.agility = 0
        self.intelligence = 0

        self.health = round(self.strength * 3.5, 1)
        self.damage = round(self.agility * 1.5, 1)
        self.mana = round(self.intelligence * 5.5, 1)

    def act(self, direction):
        global view_map
        try:
            t_x, t_y = None, None
            if direction == 'up':
                assert self.y - 1 >= 0
                t_x, t_y = self.x, self.y - 1
            elif direction == 'down':
                assert self.y + 1 <= prf['VIEW_SIZE'][1]
                t_x, t_y = self.x, self.y + 1
            elif direction == 'right':
                assert self.x + 1 <= prf['VIEW_SIZE'][0]
                t_x, t_y = self.x + 1, self.y
            elif direction == 'left':
                assert self.x - 1 >= 0
                t_x, t_y = self.x - 1, self.y
            if view_map[t_y][t_x] > prf['BORDER_VALUE']:
                pass
            elif view_map[t_y][t_x] <= prf['BORDER_VALUE'] and view_map[t_y][t_x] != 0:
                d_x, d_y = t_x-self.x, t_y-self.y
                if (self.x == prf['VIEW_BORDER'][0] and d_x == -1) \
                        or (self.x == prf['VIEW_SIZE'][0]-prf['VIEW_BORDER'][0] and d_x == 1) \
                        or (self.y == prf['VIEW_BORDER'][1] and d_y == -1) \
                        or (self.y == prf['VIEW_SIZE'][1]-prf['VIEW_BORDER'][1] and d_y == 1):
                    if prf['VIEW_SIZE'][0]//2 <= self.global_pos[0]+d_x <= prf['DEFAULT_MAP_SIZE'][0]-prf['VIEW_SIZE'][0]//2:
                        self.global_pos[0] += d_x
                    if prf['VIEW_SIZE'][1]//2 <= self.global_pos[1]+d_y <= prf['DEFAULT_MAP_SIZE'][1]-prf['VIEW_SIZE'][1]//2:
                        self.global_pos[1] += d_y

                    view_map = game_map[player.global_pos[1]-prf['VIEW_SIZE'][0]//2+d_y:
                                        player.global_pos[1]+prf['VIEW_SIZE'][0]//2+d_y,
                                        player.global_pos[0]-prf['VIEW_SIZE'][0]//2+d_x:
                                        player.global_pos[0]+prf['VIEW_SIZE'][0]//2+d_x]
                elif 6 <= self.x <= 32 and 4 <= self.y <= 20:
                    self.rect.topleft = (t_x * 32, t_y * 32)
                    self.x, self.y = t_x, t_y
                print(d_x, d_y)

        except AssertionError:
            print('AssertionError')
        except IndexError:
            print('IndexError')
        finally:
            print(self.global_pos)
            view_map = game_map[player.global_pos[1] - prf['VIEW_SIZE'][1]//2: player.global_pos[1] + prf['VIEW_SIZE'][1]//2,
                                player.global_pos[0] - prf['VIEW_SIZE'][0]//2: player.global_pos[0] + prf['VIEW_SIZE'][0]//2]


player = Player()


game_map = generate_map(prf['DEFAULT_MAP_SIZE'][0], prf['DEFAULT_MAP_SIZE'][1])


print(game_map)
print(np.shape(game_map))
view_map = game_map[player.global_pos[1]-prf['VIEW_SIZE'][1]//2:
                    player.global_pos[1]+prf['VIEW_SIZE'][1]//2,
                    player.global_pos[0]-prf['VIEW_SIZE'][0]//2:
                    player.global_pos[0]+prf['VIEW_SIZE'][0]//2]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player.act('up')
            if event.key == pygame.K_s:
                player.act('down')
            if event.key == pygame.K_a:
                player.act('left')
            if event.key == pygame.K_d:
                player.act('right')

    # Logics
    # Renders
    screen.fill((35, 35, 35))

    for y in range(prf['VIEW_SIZE'][1]):
        for x in range(prf['VIEW_SIZE'][0]):
            cell = check_pos(x, y)
            screen.blit(cell, (x*32, y*32))

    screen.blit(player.image, player.rect)
    # F-ING FLIP!
    pygame.display.flip()

pygame.quit()
sys.exit()
