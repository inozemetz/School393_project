import pygame
import os
import sys
import time


CELL_SIZE = 100
TOPLEFT = 100
WHITE = 0
BLACK = 1
all_sprites = pygame.sprite.Group()
global ai_moved
global all_positions
global moved_positions
moved_positions = [(), ()]
ai_moved = False


def is_figure(x, y):
    for j in board.figures:
        if j.get_coords()[0] == x and j.get_coords()[1] == y:
            return True
    return False


def evaluate_board():
    summ_cost1 = 0
    summ_cost2 = 0
    for i in board.figures:
        if i.color == player_color:
            summ_cost1 += i.cost
        else:
            summ_cost2 += i.cost
    return summ_cost1 - summ_cost2


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(fullname)
        sys.exit()
    image = pygame.image.load(fullname)
    return image


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


class Figure(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(load_image('white_pawn.jpg'), (CELL_SIZE, CELL_SIZE))
        self.rect = self.image.get_rect().move(y * CELL_SIZE + TOPLEFT, x * CELL_SIZE + TOPLEFT)
        self.clicked = False
        self.color = WHITE

    def move(self, x, y):
        global ai_moved
        global moved_positions
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
            self.x = x
            self.y = y
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
            screen.fill((0, 0, 0))
            board.render()
            all_sprites.draw(screen)
            pygame.display.flip()
            if self.color == player_color:
                ai_moved = False
            if not ai_moved:
                ai_moved = True
                ai.find_and_make_move(3, False)  # при низкой производмтельности уменьшить 1 аргумент

    def can_move(self, x, y):
        return True

    def click(self):
        self.clicked = True

    def unclick(self):
        self.clicked = False

    def get_coords(self):
        return (self.x, self.y)


class King(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_king.jpg'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_king.jpg'), (CELL_SIZE, CELL_SIZE))
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
            if i.__class__.__name__ != "King" and i.color != self.color and i.can_eat(x, y):
                can = False
        self.moved = True
        return can

    def can_eat(self, x, y):
        return self.can_move(x, y)


class Knight(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_knight.jpg'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_knight.jpg'), (CELL_SIZE, CELL_SIZE))
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


class Pawn(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_pawn.jpg'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_pawn.jpg'), (CELL_SIZE, CELL_SIZE))
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


class Rook(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_rook.jpg'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_rook.jpg'), (CELL_SIZE, CELL_SIZE))
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


class Bishop(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_bishop.jpg'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_bishop.jpg'), (CELL_SIZE, CELL_SIZE))
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


class Queen(Figure):
    def __init__(self, x, y, color):
        super().__init__(x, y)
        if color == WHITE:
            self.image = pygame.transform.scale(load_image('white_queen.jpg'), (CELL_SIZE, CELL_SIZE))
        else:
            self.image = pygame.transform.scale(load_image('black_queen.jpg'), (CELL_SIZE, CELL_SIZE))
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


class Board:
    def __init__(self):
        self.width = 8
        self.height = 8
        self.board = [[0] * width for _ in range(height)]
        self.left = self.top = TOPLEFT
        self.cell_size = CELL_SIZE
        self.figures = []

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

        '''self.figures.append(King(7, 7, BLACK))
        self.figures.append(Pawn(0, 6, BLACK))
        self.figures.append(Pawn(3, 6, BLACK))
        self.figures.append(Pawn(0, 1, WHITE))
        self.figures.append(Pawn(3, 1, WHITE))
        self.figures.append(King(0, 0, WHITE))'''


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
        for i in self.figures:
            if i.get_coords() == cell_coords and not i.clicked:
                i.click()
            elif i.get_coords() == cell_coords and i.clicked:
                i.unclick()
            elif i.get_coords() != cell_coords and i.clicked:
                i.move(cell_coords[0], cell_coords[1])
                i.unclick()



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
        pygame.draw.line(screen, (255, 0, 0), (self.top, self.left), (self.top + 800, self.left))
        pygame.draw.line(screen, (255, 0, 0), (self.top, self.left + 800), (self.top, self.left))
        pygame.draw.line(screen, (255, 0, 0), (self.top + 800, self.left + 800), (self.top, self.left + 800))
        pygame.draw.line(screen, (255, 0, 0), (self.top + 800, self.left + 800), (self.top + 800, self.left))


class ArtificialIntelligence:
    def __init__(self, color):
        self.color = color

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
                            print(i, value, time.time() - a, x, y)
        print(bestmove)
        for i in board.figures:
            if i.get_coords() == (bestmovefound[0], bestmovefound[1]):
                i.move(bestmovefound[2], bestmovefound[3])


size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)
board = Board()
player_color = WHITE
ai = ArtificialIntelligence(BLACK)
fps = 100
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