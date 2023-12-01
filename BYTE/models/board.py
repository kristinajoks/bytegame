import pygame

class Board:
    def __init__(self, dim):
        self.dim = dim
        self.board=[[(bytes([0]), 0) for _ in range(dim)] for _ in range(dim)]
        self.bit = (dim-2)*dim/2
        self.byte = self.bit/8
        self.squareSize = 70

    def drawInitial(self, screen):
        x_offset = 0
        y_offset = 0
        color = ()

        for row in range(self.dim):
            for col in range(self.dim):
                rect = [100 + x_offset, 50 + y_offset, self.squareSize, self.squareSize]

                if(row%2 == 0 and col %2 == 0 or row%2 == 1 and col%2 == 1):
                    color = (210,115,187)
                    pygame.draw.rect(screen, color, rect)
                    self.initialBits(screen, rect, row)
                else:
                    color = (242,206,234)
                    pygame.draw.rect(screen, color, rect)

                x_offset += self.squareSize

            x_offset = 0
            y_offset += self.squareSize
            
    def initialBits(self, screen, rect, row):
        if(row != 0 and row != self.dim - 1):
            if(row % 2 == 0):
                bit_image = pygame.image.load('BYTE\\assets\\white.gif')
            else:
                bit_image = pygame.image.load('BYTE\\assets\\black.gif') 
            bit_image = pygame.transform.scale2x(bit_image)
            pygame.Surface.blit(screen, bit_image, (rect[0] + self.squareSize / 4, rect[1] + self.squareSize / 4))
