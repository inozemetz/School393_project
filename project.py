import pygame
import os
import sys


CELL_SIZE = 100
TOPLEFT = 100
WHITE = 0
BLACK = 1

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(fullname)
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Figure(pygame.sprite.Sprite):
    def __init__(self, x, y, sprites):
        super().__init__(sprites)
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(load_image('white_pawn.jpg'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(y * CELL_SIZE + TOPLEFT, x * CELL_SIZE + TOPLEFT)
        self.clicked = False
        self.color = WHITE

    def move(self, x1, y1):
        board[x1][y1] = self
        del self

    def can_move(self, x, y):
        return True

    def is_clicked(self):
        return self.clicked

    def click(self):
        self.clicked = True

    def get_coords(self):
        return (self.y, self.x)


class Board:
    def __init__(self):
        self.width = 8
        self.height = 8
        self.board = [[0] * width for _ in range(height)]
        self.left = self.top = TOPLEFT
        self.cell_size = CELL_SIZE

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def get_cell(self, mouse_pos):
        for i in range(self.height):
            for j in range(self.width):
                if mouse_pos[0] > self.top + j * self.cell_size and mouse_pos[1] > self.top + i * self.cell_size and \
                    mouse_pos[0] < self.cell_size + self.top + j * self.cell_size and \
                    mouse_pos[1] < self.cell_size + self.top + i * self.cell_size:
                    return (j, abs(i - 7))

    def on_click(self, cell_coords):
        print(cell_coords)



    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def render(self):
        k = 0
        for i in range(self.height):
            for j in range(self.width):
                if (j + k) % 2 != 0:
                    pygame.draw.rect(screen, (0, 0, 0), (self.top + j * self.cell_size, self.top + i * self.cell_size,
                                                         self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(screen, (255, 255, 255), (self.top + j * self.cell_size, self.top + i * self.cell_size,
                                                         self.cell_size, self.cell_size))
            k += 1
        pygame.draw.line(screen, (255, 255, 255), (self.top, self.left), (self.top + 800, self.left))
        pygame.draw.line(screen, (255, 255, 255), (self.top, self.left + 800), (self.top, self.left))
        pygame.draw.line(screen, (255, 255, 255), (self.top + 800, self.left + 800), (self.top, self.left + 800))
        pygame.draw.line(screen, (255, 255, 255), (self.top + 800, self.left + 800), (self.top + 800, self.left))


size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
board = Board()
fps = 10
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos)
    screen.fill((0, 0, 0))
    board.render()
    all_sprites.draw(screen)
    clock.tick(fps)
    pygame.display.flip()
