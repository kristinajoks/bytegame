import pygame

class Board:
    def __init__(self, dim):
        self.dim = dim
        self.board=[[(bytes([0]), 0) for _ in range(dim)] for _ in range(dim)]
        self.bit = (dim-2)*dim/2
        self.byte = self.bit/8

    def drawInitial(self, screen):
        squareSize = 50
        x_offset = 0
        y_offset = 0
        color = ()

        for row in range(self.dim):
            for col in range(self.dim):
                if(row%2 == 0 and col %2 == 0 or row%2 == 1 and col%2 == 1):
                    color = (210,115,187)
                else:
                    color = (242,206,234)
                pygame.draw.rect(screen, color, [200 + x_offset, 100 + y_offset, squareSize, squareSize])
                x_offset += squareSize
            x_offset = 0
            y_offset += squareSize
            
