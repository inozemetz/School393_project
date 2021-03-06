import pygame
import os
import sys
import time
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow

# объявление глобальных переменных
CELL_SIZE = 100
TOPLEFT = 100
WHITE = 0
BLACK = 1
all_sprites = pygame.sprite.Group()
global ai_moved
global all_positions
global moved_positions
global running
white_won = None
global moved_positions
moved_positions = [(-5, -5), (-5, -5)]


# есть ли фигура в данном поле
def is_figure(x, y):
    for j in board.figures:
        if j.get_coords()[0] == x and j.get_coords()[1] == y:
            return True
    return False


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    pygame.init()
    clock = pygame.time.Clock()
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    while True:
        if ex.is_pushed:
            return ex.player_color, ex.ai_color
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        clock.tick(60)


# оценка доски
def evaluate_board():
    summ_cost1 = 0
    summ_cost2 = 0
    for i in board.figures:
        if i.color == player_color:
            summ_cost1 += i.cost
        else:
            summ_cost2 += i.cost
    return summ_cost1 - summ_cost2


# загрузка изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(fullname)
        sys.exit()
    image = pygame.image.load(fullname)
    return image


# может ли кто-то съесть короля
def smb_can_eat_king(color, fig):
    x_king = y_king = -1
    for i in board.figures:
        if i.__class__.__name__ == 'King' and i.color == color:
            (x_king, y_king) = i.get_coords()
    for i in board.figures:
        if i == fig:
            return False
        else:
            if i.color != color and i.__class__.__name__ != 'King' and i.can_eat(x_king, y_king):
                return True
    return False


# родительский класс фигуры
class Figure(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(load_image('white_pawn.png'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(y * CELL_SIZE + TOPLEFT, x * CELL_SIZE + TOPLEFT)
        self.clicked = False
        self.color = WHITE

    # подвинуть фигуру
    def move(self, x, y):
        global ai_moved
        global moved_positions
        global white_won
        global running
        moved = False
        if self.can_move(x, y) == '0-0-0' and self.color == WHITE:
            self.x = 2
            for i in board.figures:
                if i.__class__.__name__ == 'Rook' and i.get_coords() == (0, 0):
                    i.x = 3
                    i.rect = i.image.get_rect().move(i.x * CELL_SIZE + TOPLEFT, (7 - i.y) * CELL_SIZE + TOPLEFT)
                    break
            self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
            self.moved = True
            moved = True
        elif self.can_move(x, y) == '0-0' and self.color == WHITE:
            self.x = 6
            for i in board.figures:
                if i.__class__.__name__ == 'Rook' and i.get_coords() == (7, 0):
                    i.x = 5
                    i.rect = i.image.get_rect().move(i.x * CELL_SIZE + TOPLEFT, (7 - i.y) * CELL_SIZE + TOPLEFT)
                    break
            self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
            moved = True
            self.moved = True
        elif self.can_move(x, y) == '0-0-0' and self.color == BLACK:
            self.x = 2
            for i in board.figures:
                if i.__class__.__name__ == 'Rook' and i.get_coords() == (0, 7):
                    i.x = 3
                    i.rect = i.image.get_rect().move(i.x * CELL_SIZE + TOPLEFT, (7 - i.y) * CELL_SIZE + TOPLEFT)
                    break
            self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
            moved = True
            self.moved = True
        elif self.can_move(x, y) == '0-0' and self.color == BLACK:
            self.x = 6
            for i in board.figures:
                if i.__class__.__name__ == 'Rook' and i.get_coords() == (7, 7):
                    i.x = 5
                    i.rect = i.image.get_rect().move(i.x * CELL_SIZE + TOPLEFT, (7 - i.y) * CELL_SIZE + TOPLEFT)
                    break
            self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
            moved = True
            self.moved = True
        elif self.can_move(x, y):
            for i in board.figures:
                if i.get_coords() == (x, y):
                    i.kill()
                    board.figures.remove(i)
            moved_positions[0] = (self.x, self.y)
            self.x = x
            self.y = y
            moved_positions[1] = (x, y)
            self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
            moved = True
            if self.__class__.__name__ == "Pawn":
                if self.color == BLACK and self.y == 0:
                    board.figures.remove(self)
                    board.figures.append(Queen(self.x, self.y, BLACK))
                    self.kill()
                elif self.color == WHITE and self.y == 7:
                    board.figures.remove(self)
                    board.figures.append(Queen(self.x, self.y, WHITE))
                    self.kill()
        if self.__class__.__name__ == "King":
            self.moved = True
        if moved:
            if self.color == BLACK and smb_can_eat_king(WHITE, 0):
                n = False
                for i in board.figures:
                    if i.__class__.__name__ == 'King' and i.color == WHITE:
                        for x in range(8):
                            for y in range(8):
                                if i.can_move(x, y):
                                    n = True
                if n is False:
                    white_won = False
                    screen.fill((0, 0, 0))
                    board.render()
                    all_sprites.draw(screen)
                    pygame.display.flip()
                    return None
            if self.color == WHITE and smb_can_eat_king(BLACK, 0):
                n = False
                for i in board.figures:
                    if i.__class__.__name__ == 'King' and i.color == BLACK:
                        for x in range(8):
                            for y in range(8):
                                if i.can_move(x, y):
                                    n = True
                if n is False:
                    white_won = True
                    screen.fill((0, 0, 0))
                    board.render()
                    all_sprites.draw(screen)
                    pygame.display.flip()
                    return None
            screen.fill((0, 0, 0))
            board.render()
            all_sprites.draw(screen)
            pygame.display.flip()
            if self.color == player_color:
                ai_moved = False
            if not ai_moved:
                ai_moved = True
                ai.find_and_make_move(3, False)  # при низкой производмтельности уменьшить 1 аргумент

    # может ли фигура подвинуться на эту клетку
    def can_move(self, x, y):
        return True

    # может ли фигура съесть фигуру по этим координатам
    def can_eat(self, x, y):
        return True

    # нажать на фигуру
    def click(self):
        self.clicked = True

    # перестать нажимать на фигуру
    def unclick(self):
        self.clicked = False

    # координаты фигуры
    def get_coords(self):
        return (self.x, self.y)


# дочерний класс короля
class King(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_king.png'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_king.png'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
        self.color = color
        self.clicked = False
        self.moved = False
        self.n_cost = 90
        self.cost_modify = [
        [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
        [ -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
        [ -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
        [  2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0],
        [  2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0]]
        if self.color == WHITE:
            self.cost = self.n_cost + (self.cost_modify[abs(self.y - 7)][self.x]) / 10
        else:
            self.cost = self.n_cost + (self.cost_modify[::-1][abs(self.y - 7)][self.x]) / 10

    def can_move(self, x, y):
        if not self.moved and self.color == WHITE and x == 6:
            for i in board.figures:
                if i.get_coords() == (7, 0) and i.__class__.__name__ == 'Rook' and i.color == WHITE:
                    return '0-0'
        if not self.moved and self.color == WHITE and x == 2:
            for i in board.figures:
                if i.get_coords() == (0, 0) and i.__class__.__name__ == 'Rook' and i.color == WHITE:
                    return '0-0-0'
        if not self.moved and self.color == BLACK and x == 6:
            for i in board.figures:
                if i.get_coords() == (7, 7) and i.__class__.__name__ == 'Rook' and i.color == BLACK:
                    return '0-0'
        if not self.moved and self.color == BLACK and x == 2:
            for i in board.figures:
                if i.get_coords() == (0, 7) and i.__class__.__name__ == 'Rook' and i.color == BLACK:
                    return '0-0-0'
        can = True
        if (abs(x - self.x) == 1 and abs(y - self.y) == 0) or (abs(x - self.x) == 0 and abs(y - self.y) == 1) or (abs(x - self.x) == 1 and abs(y - self.y) == 1):
            for i in board.figures:
                if i.get_coords()[0] == x and i.get_coords()[1] == y and i.color == self.color:
                    can = False
                    break
        else:
            can = False
        for i in board.figures:
            if i.color != self.color and i.can_eat(x, y):
                can = False
        self.moved = True
        return can

    def can_eat(self, x, y):
        if abs(x - self.x) <= 1 and abs(y - self.y) <= 1:
            return True


# дочерний класс коня
class Knight(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_knight.png'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_knight.png'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
        self.color = color
        self.clicked = False
        self.n_cost = 3
        self.cost_modify = [
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
        [-4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0],
        [-3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0],
        [-3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0],
        [-3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0],
        [-3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0],
        [-4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0],
        [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]]
        self.cost = self.n_cost + (self.cost_modify[abs(self.y - 7)][self.x]) / 10

    def can_move(self, x, y):
        can = True
        if (abs(x - self.x) == 1 and abs(y - self.y) == 2) or (abs(x - self.x) == 2 and abs(y - self.y) == 1):
            for i in board.figures:
                if i.get_coords()[0] == x and i.get_coords()[1] == y and i.color == self.color:
                    can = False
        else:
            return False
        n, m = self.x, self.y
        fig = ind = None
        for j in board.figures:
            if j.get_coords() == (x, y):
                fig = j
                ind = board.figures.index(fig)
                board.figures.remove(j)
        self.x, self.y = x, y
        if smb_can_eat_king(self.color, self):
            can = False
        self.x, self.y = n, m
        if fig is not None:
            board.figures.insert(ind, fig)
        if can:
            return True

    def can_eat(self, x, y):
        return self.can_move(x, y)


# дочерний класс пешки
class Pawn(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_pawn.png'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_pawn.png'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
        self.color = color
        self.clicked = False
        self.n_cost = 1
        self.cost_modify = [[90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0, 90.0],
        [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
        [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
        [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
        [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
        [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
        [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
        if self.color == WHITE:
            self.cost = self.n_cost + (self.cost_modify[abs(self.y - 7)][self.x]) / 10
        else:
            self.cost = self.n_cost + (self.cost_modify[::-1][abs(self.y - 7)][self.x]) / 10

    def can_move(self, x, y):
        can = True
        if abs(x - self.x) == 1 and ((y == self.y + 1 and self.color == WHITE) or (y == self.y - 1 and self.color == BLACK)):
            is_fig = False
            for i in board.figures:
                if i.get_coords()[0] == x and i.get_coords()[1] == y and i.color != self.color:
                    is_fig = True
            if not is_fig:
                can = False
        elif (y == self.y + 1 and x == self.x and self.color == WHITE) or (y == self.y + 2 and self.y == 1 and x == self.x and self.color == WHITE) or \
                (y == self.y - 1 and x == self.x and self.color == BLACK) or (y == self.y - 2 and self.y == 6 and x == self.x and self.color == BLACK):
            for i in board.figures:
                if i.get_coords()[0] == x and i.get_coords()[1] == y:
                    can = False
            for i in board.figures:
                if i.get_coords()[0] == x and i.get_coords()[1] == self.y + 1 and self.color == WHITE:
                    can = False
                if i.get_coords()[0] == x and i.get_coords()[1] == self.y - 1 and self.color == BLACK:
                    can = False
        else:
            can = False
        n, m = self.x, self.y
        fig = ind = None
        for j in board.figures:
            if j.get_coords() == (x, y):
                fig = j
                ind = board.figures.index(fig)
                board.figures.remove(j)
        self.x, self.y = x, y
        if smb_can_eat_king(self.color, self):
            can = False
        self.x, self.y = n, m
        if fig is not None:
            board.figures.insert(ind, fig)
        if can:
            return True

    def can_eat(self, x, y):
        return abs(x - self.x) == 1 and ((y == self.y + 1 and self.color == WHITE) or (y == self.y - 1 and self.color == BLACK))


# дочерний класс ладьи
class Rook(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_rook.png'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_rook.png'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
        self.color = color
        self.clicked = False
        self.n_cost = 5
        self.cost_modify = [
        [  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
        [  0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5],
        [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [ -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5],
        [  0.0,   0.0, 0.0,  0.5,  0.5,  0.0,  0.0,  0.0]]
        if self.color == WHITE:
            self.cost = self.n_cost + (self.cost_modify[abs(self.y - 7)][self.x]) / 10
        else:
            self.cost = self.n_cost + (self.cost_modify[::-1][abs(self.y - 7)][self.x]) / 10

    def can_move(self, x, y):
        can = True
        if (x == self.x and y != self.y) or (y == self.y and x != self.x):
            if x == self.x:
                if y > self.y:
                    for i in range(self.y + 1, y):
                        if is_figure(x, i):
                            can = False
                            break
                elif self.y > y:
                    for i in range(self.y - 1, y, -1):
                        if is_figure(x, i):
                            can = False
                            break
            else:
                if x > self.x:
                    for i in range(self.x + 1, x):
                        if is_figure(i, y):
                            can = False
                            break
                elif self.x > x:
                    for i in range(self.x - 1, x, -1):
                        if is_figure(i, y):
                            can = False
                            break
            for i in board.figures:
                if i.get_coords()[0] == x and i.get_coords()[1] == y and i.color == self.color:
                    can = False
        else:
            can = False
        n, m = self.x, self.y
        fig = ind = None
        for j in board.figures:
            if j.get_coords() == (x, y):
                fig = j
                ind = board.figures.index(fig)
                board.figures.remove(j)
        self.x, self.y = x, y
        if smb_can_eat_king(self.color, self):
            can = False
        self.x, self.y = n, m
        if fig is not None:
            board.figures.insert(ind, fig)
        if can:
            return True

    def can_eat(self, x, y):
        return self.can_move(x, y)


# дочерний класс слона
class Bishop(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_bishop.png'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_bishop.png'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
        self.color = color
        self.clicked = False
        self.n_cost = 3
        self.cost_modify = [
        [ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
        [ -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
        [ -1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0],
        [ -1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0],
        [ -1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0],
        [ -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0],
        [ -1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0],
        [ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]]
        if self.color == WHITE:
            self.cost = self.n_cost + (self.cost_modify[abs(self.y - 7)][self.x]) / 10
        else:
            self.cost = self.n_cost + (self.cost_modify[::-1][abs(self.y - 7)][self.x]) / 10

    def can_move(self, x, y):
        can = True
        if abs(self.x - x) == abs(self.y - y):
            if self.x > x and self.y > y:
                for i in range(1, abs(x - self.x)):
                    if is_figure(self.x - i, self.y - i):
                        can = False
                        break
            elif self.x > x and self.y < y:
                for i in range(1, abs(x - self.x)):
                    if is_figure(self.x - i, self.y + i):
                        can = False
                        break
            elif self.x < x and self.y > y:
                for i in range(1, abs(x - self.x)):
                    if is_figure(self.x + i, self.y - i):
                        can = False
                        break
            elif self.x < x and self.y < y:
                for i in range(1, abs(x - self.x)):
                    if is_figure(self.x + i, self.y + i):
                        can = False
                        break
        else:
            can = False
        for i in board.figures:
            if i.get_coords()[0] == x and i.get_coords()[1] == y and i.color == self.color:
                can = False
        n, m = self.x, self.y
        fig = ind = None
        for j in board.figures:
            if j.get_coords() == (x, y):
                fig = j
                ind = board.figures.index(fig)
                board.figures.remove(j)
        self.x, self.y = x, y
        if smb_can_eat_king(self.color, self):
            can = False
        self.x, self.y = n, m
        if fig is not None:
            board.figures.insert(ind, fig)
        if can:
            return True

    def can_eat(self, x, y):
        return self.can_move(x, y)


# дочерний класс ферзя
class Queen(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_queen.png'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_queen.png'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(x * CELL_SIZE + TOPLEFT, (7 - y) * CELL_SIZE + TOPLEFT)
        self.color = color
        self.clicked = False
        self.n_cost = 9
        self.cost_modify = [
        [ -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
        [ -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0],
        [ -1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
        [ -0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
        [  0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5],
        [ -1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0],
        [ -1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0],
        [ -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]]
        self.cost = self.n_cost + (self.cost_modify[abs(self.y - 7)][self.x]) / 10

    def can_move(self, x, y):
        can = True
        if abs(self.x - x) == abs(self.y - y):
            if self.x > x and self.y > y:
                for i in range(1, abs(x - self.x)):
                    if is_figure(self.x - i, self.y - i):
                        can = False
                        break
            elif self.x > x and self.y < y:
                for i in range(1, abs(x - self.x)):
                    if is_figure(self.x - i, self.y + i):
                        can = False
                        break
            elif self.x < x and self.y > y:
                for i in range(1, abs(x - self.x)):
                    if is_figure(self.x + i, self.y - i):
                        can = False
                        break
            elif self.x < x and self.y < y:
                for i in range(1, abs(x - self.x)):
                    if is_figure(self.x + i, self.y + i):
                        can = False
                        break
        elif (x == self.x and y != self.y) or (y == self.y and x != self.x):
            can = True
            if x == self.x:
                if y > self.y:
                    for i in range(self.y + 1, y):
                        if is_figure(x, i):
                            can = False
                            break
                elif self.y > y:
                    for i in range(self.y - 1, y, -1):
                        if is_figure(x, i):
                            can = False
                            break
            else:
                if x > self.x:
                    for i in range(self.x + 1, x):
                        if is_figure(i, y):
                            can = False
                            break
                elif self.x > x:
                    for i in range(self.x - 1, x, -1):
                        if is_figure(i, y):
                            can = False
                            break
        else:
            can = False
        for i in board.figures:
            if i.get_coords()[0] == x and i.get_coords()[1] == y and i.color == self.color:
                can = False
        n, m = self.x, self.y
        fig = ind = None
        for j in board.figures:
            if j.get_coords() == (x, y):
                fig = j
                ind = board.figures.index(fig)
                board.figures.remove(j)
        self.x, self.y = x, y
        if smb_can_eat_king(self.color, self):
            can = False
        self.x, self.y = n, m
        if fig is not None:
            board.figures.insert(ind, fig)
        if can:
            return True

    def can_eat(self, x, y):
        return self.can_move(x, y)


# класс доски
class Board:
    def __init__(self):
        self.width = 8
        self.height = 8
        self.board = [[0] * width for _ in range(height)]
        self.left = self.top = TOPLEFT
        self.cell_size = CELL_SIZE
        self.figures = []
        # инициализация фигур
        self.figures.append(Knight(1, 7, BLACK))
        self.figures.append(Knight(6, 7, BLACK))
        self.figures.append(Pawn(0, 6, BLACK))
        self.figures.append(Pawn(1, 6, BLACK))
        self.figures.append(Pawn(2, 6, BLACK))
        self.figures.append(Pawn(3, 6, BLACK))
        self.figures.append(Pawn(4, 6, BLACK))
        self.figures.append(Pawn(5, 6, BLACK))
        self.figures.append(Pawn(6, 6, BLACK))
        self.figures.append(Pawn(7, 6, BLACK))
        self.figures.append(Rook(0, 7, BLACK))
        self.figures.append(Rook(7, 7, BLACK))
        self.figures.append(Bishop(2, 7, BLACK))
        self.figures.append(Bishop(5, 7, BLACK))
        self.figures.append(Queen(3, 7, BLACK))
        self.figures.append(King(4, 7, BLACK))
        self.figures.append(Pawn(0, 1, WHITE))
        self.figures.append(Pawn(1, 1, WHITE))
        self.figures.append(Pawn(2, 1, WHITE))
        self.figures.append(Pawn(3, 1, WHITE))
        self.figures.append(Pawn(4, 1, WHITE))
        self.figures.append(Pawn(5, 1, WHITE))
        self.figures.append(Pawn(6, 1, WHITE))
        self.figures.append(Pawn(7, 1, WHITE))
        self.figures.append(Rook(0, 0, WHITE))
        self.figures.append(Rook(7, 0, WHITE))
        self.figures.append(Knight(1, 0, WHITE))
        self.figures.append(Knight(6, 0, WHITE))
        self.figures.append(Bishop(2, 0, WHITE))
        self.figures.append(Bishop(5, 0, WHITE))
        self.figures.append(Queen(3, 0, WHITE))
        self.figures.append(King(4, 0, WHITE))


    # установить правую верхнюю точку
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # получить координату доски по координатам пикселя
    def get_cell(self, mouse_pos):
        for i in range(self.height):
            for j in range(self.width):
                if mouse_pos[0] > self.top + j * self.cell_size and mouse_pos[1] > self.top + i * self.cell_size and \
                    mouse_pos[0] < self.cell_size + self.top + j * self.cell_size and \
                    mouse_pos[1] < self.cell_size + self.top + i * self.cell_size:
                    return (j, abs(i - 7))

    # обработчик нажатий
    def on_click(self, cell_coords):
        try:
            for i in self.figures:
                if i.get_coords() == cell_coords and not i.clicked:
                    i.click()
                elif i.get_coords() == cell_coords and i.clicked:
                    i.unclick()
                elif i.get_coords() != cell_coords and i.clicked and i.color == player_color:
                    i.move(cell_coords[0], cell_coords[1])
                    i.unclick()
        except Exception:
            pass

    # метод связующий get_cell и on_click
    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    # нарисовать доску
    def render(self):
        global moved_positions
        k = 0
        for i in range(self.height):
            for j in range(self.width):
                if (j + k) % 2 != 0:
                    pygame.draw.rect(screen, (100, 100, 100), (self.top + j * self.cell_size, self.top + i * self.cell_size,
                                                         self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(screen, (255, 255, 255), (self.top + j * self.cell_size, self.top + i * self.cell_size,
                                                         self.cell_size, self.cell_size))
            k += 1
        pygame.draw.line(screen, (100, 0, 0), (self.top, self.left), (self.top + 800, self.left))
        pygame.draw.line(screen, (100, 0, 0), (self.top, self.left + 800), (self.top, self.left))
        pygame.draw.line(screen, (100, 0, 0), (self.top + 800, self.left + 800), (self.top, self.left + 800))
        pygame.draw.line(screen, (100, 0, 0), (self.top + 800, self.left + 800), (self.top + 800, self.left))
        if (abs(7 - moved_positions[0][1]) * 7 + abs(7 - moved_positions[0][0])) % 2 == 1:
            pygame.draw.rect(screen, (170, 255, 170), (self.top + moved_positions[0][0] * self.cell_size, self.top + abs(7 - moved_positions[0][1]) * self.cell_size,
                                                       self.cell_size, self.cell_size))
        else:
            pygame.draw.rect(screen, (70, 100, 70), (self.top + moved_positions[0][0] * self.cell_size,
                                                   self.top + abs(7 - moved_positions[0][1]) * self.cell_size,
                                                   self.cell_size, self.cell_size))
        if (abs(7 - moved_positions[1][1]) * 7 + abs(7 - moved_positions[1][0])) % 2 == 1:
            pygame.draw.rect(screen, (170, 255, 170), (self.top + moved_positions[1][0] * self.cell_size,
                                                       self.top + abs(7 - moved_positions[1][1]) * self.cell_size,
                                                       self.cell_size, self.cell_size))
        else:
            pygame.draw.rect(screen, (70, 100, 70), (self.top + moved_positions[1][0] * self.cell_size,
                                                   self.top + abs(7 - moved_positions[1][1]) * self.cell_size,
                                                   self.cell_size, self.cell_size))
        for i in range(8):
            f1 = pygame.font.Font(None, 35)
            text1 = f1.render(chr(ord('a') + i), True, (200, 200, 200))
            screen.blit(text1, (TOPLEFT + CELL_SIZE // 2 + i * CELL_SIZE - 5, 920))
        for i in range(8, 0, -1):
            f1 = pygame.font.Font(None, 35)
            text1 = f1.render(str(abs(9 - i)), True, (200, 200, 200))
            screen.blit(text1, (60, TOPLEFT + CELL_SIZE // 2 + (i - 1) * CELL_SIZE - 5))


# класс Искуственного Интеллекта
class ArtificialIntelligence:
    # рекурсивная функция нахождения лучшей позиции
    def ai_move(self, depth, alpha, beta, ismaxplayer):
        if depth == 0:
            return round(evaluate_board(), 5)
        if ismaxplayer:
            bestmove = -9999
            for i in board.figures:
                if i.color == player_color:
                    for x in range(7, -1, -1):
                        for y in range(7, -1, -1):
                            if i.can_move(x, y):
                                n, m = (i.x, i.y)
                                fig = ind = None
                                for j in board.figures:
                                    if j.get_coords() == (x, y):
                                        fig = j
                                        ind = board.figures.index(fig)
                                        board.figures.remove(j)
                                i.x = x
                                i.y = y
                                cost_undo = i.cost
                                i.cost = i.n_cost + (i.cost_modify[abs(y - 7)][x]) / 10
                                bestmove = max(bestmove, self.ai_move(depth - 1, alpha, beta, not ismaxplayer))
                                i.x = n
                                i.y = m
                                if fig is not None:
                                    board.figures.insert(ind, fig)
                                i.cost = cost_undo
                                alpha = max(alpha, bestmove)
                                if beta <= alpha:
                                    return bestmove
            return bestmove
        else:
            bestmove = 9999
            for i in board.figures:
                if i.color != player_color:
                    for x in range(7, -1, -1):
                        for y in range(7, -1, -1):
                            if i.can_move(x, y):
                                n, m = (i.x, i.y)
                                fig = ind = None
                                for j in board.figures:
                                    if j.get_coords() == (x, y):
                                        fig = j
                                        ind = board.figures.index(fig)
                                        board.figures.remove(j)
                                i.x = x
                                i.y = y
                                cost_undo = i.cost
                                i.cost = i.n_cost + (i.cost_modify[::-1][abs(y - 7)][x]) / 10
                                bestmove = min(bestmove, self.ai_move(depth - 1, alpha, beta, not ismaxplayer))
                                i.x = n
                                i.y = m
                                if fig is not None:
                                    board.figures.insert(ind, fig)
                                i.cost = cost_undo
                                beta = min(beta, bestmove)
                                if beta <= alpha:
                                    return bestmove
            return bestmove

    # нахождение лучшего хода
    def find_and_make_move(self, depth, ismaxplayer):
        a = time.time()
        bestmove = 9999
        bestmovefound = None
        for i in board.figures:
            if i.color != player_color:
                for x in range(7, -1, -1):
                    for y in range(7, -1, -1):
                        if i.can_move(x, y):
                            n, m = (i.x, i.y)
                            fig = ind = None
                            for j in board.figures:
                                if j.get_coords() == (x, y):
                                    fig = j
                                    ind = board.figures.index(fig)
                                    board.figures.remove(j)
                            i.x = x
                            i.y = y
                            cost_undo = i.cost
                            i.cost = i.n_cost + (i.cost_modify[::-1][abs(y - 7)][x]) / 10
                            value = self.ai_move(depth - 1, -10000, 10000, not ismaxplayer)
                            i.x = n
                            i.y = m
                            if fig is not None:
                                board.figures.insert(ind, fig)
                            i.cost = cost_undo
                            if value <= bestmove:
                                bestmove = value
                                bestmovefound = (n, m, x, y)
                            print(i.__class__.__name__, value, time.time() - a, x, y)
        for i in board.figures:
            if i.get_coords() == (bestmovefound[0], bestmovefound[1]):
                i.move(bestmovefound[2], bestmovefound[3])


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('start_screen.ui', self)  # Загружаем дизайн
        self.pushButton.clicked.connect(self.white_button)
        self.pushButton_2.clicked.connect(self.black_button)
        self.is_pushed = False

    def white_button(self):
        self.player_color = WHITE
        self.ai_color = BLACK
        self.is_pushed = True

    def black_button(self):
        self.player_color = BLACK
        self.ai_color = WHITE
        self.is_pushed = True


class EndWidget(QMainWindow):
    def __init__(self, white_won):
        super().__init__()
        uic.loadUi('end_screen.ui', self)  # Загружаем дизайн
        if white_won is True:
            self.label.setText('победили белые')
            self.label.adjustSize()
        elif white_won is False:
            self.label.setText('победили черные')
            self.label.adjustSize()
        else:
            self.label.setText('ничья')
            self.label.adjustSize()


# инициализация переменных и объектов
player_color, ai_color = start_screen()
if player_color == BLACK:
    ai_moved = False
else:
    ai_moved = True
size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
board = Board()
ai = ArtificialIntelligence()
fps = 100
clock = pygame.time.Clock()
running = True
first_move = False
# основной цикл
while running:
    try:
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
        if not (white_won is None):
            running = False
        if player_color == BLACK and not first_move:
            first_move = True
            ai_moved = True
            ai.find_and_make_move(3, False)
    except Exception:
        print('что-то пошло не так')
pygame.quit()
app = QApplication(sys.argv)
ex = EndWidget(white_won)
ex.show()
sys.exit(app.exec_())
