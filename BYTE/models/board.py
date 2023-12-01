import pygame
from helpers.binary_helper import * 


class Board:
    def __init__(self, dim, rectSize, rectStart):
        self.dim = dim
        self.board=[[(bytes([0]), 0) for _ in range(dim)] for _ in range(dim)]
        self.bit = (dim-2)*dim/2
        self.byte = self.bit/8
        self.squareSize = rectSize / dim
        self.rectStart = rectStart

    def drawInitial(self, screen):
        x_offset = 0
        y_offset = 0
        color = ()

        for row in range(self.dim):
            for col in range(self.dim):
                rect = [self.rectStart[0] + x_offset, self.rectStart[1] + y_offset, self.squareSize, self.squareSize]

                if(row%2 == 0 and col %2 == 0 or row%2 == 1 and col%2 == 1):
                    color = (210,115,187)
                    pygame.draw.rect(screen, color, rect)
                    self.initialBits(screen, rect, row, col)

                else:
                    color = (242,206,234)
                    pygame.draw.rect(screen, color, rect)

                x_offset += self.squareSize

            x_offset = 0
            y_offset += self.squareSize
            
    def initialBits(self, screen, rect, row, col):
        if(row != 0 and row != self.dim - 1):
            if(row % 2 == 0):
                bit_image = pygame.image.load('BYTE\\assets\\white.gif')
                self.writeBit(row, col, 1)
            else:
                bit_image = pygame.image.load('BYTE\\assets\\black.gif') 
                self.writeBit(row, col, 0)

            bit_image = pygame.transform.scale(bit_image, (self.squareSize/2, self.squareSize/2))    
            pygame.Surface.blit(screen, bit_image, (rect[0] + self.squareSize / 4, rect[1] + self.squareSize / 2))


    def writeBit(self, row, col, bit):
        pos = self.board[row][col][1]
        
        if(bit == 1):
            byte = self.board[row][col][0]

            mask = 1 << pos
            negatedMask = bitwise_not_bytes(bytes([mask]))
            maskedByte = bitwise_and_bytes(byte, negatedMask)
            writtenByte = bitwise_or_bytes(maskedByte, bytes([1 << pos]))
            pos += 1

            self.board[row][col] = (writtenByte, pos)
        else:
            self.board[row][col] = (self.board[row][col][0], pos + 1)


    def move(self, screen, movement):   
        
        x1, y1 = self.get_field_start(movement[0], movement[1])
        x2, y2 = self.get_field_start(movement[2], movement[3])

        row1 = int(y1 / self.squareSize)
        col1 = int(x1 / self.squareSize)
        row2 = int(x2 / self.squareSize)
        col2 = int(y2 / self.squareSize)

        isValid = self.valid_move(row1, col1, row2, col2)
        if( isValid == None):
            return
        
        #samo treba da izmenimo matricu da bi odgovarala pomerenoj slici
        # return isValid 
        # validan potez   

        #brisanje slika sa jednog i crtanje na drugom polju
        #brisanje bita iz elementa matrice i dodavanje u drugi element matrice

        #brisanje slike sa polja
        # pygame.draw.rect(screen, (242, 206, 234), (row1 * self.squareSize + self.rectStart[0], col1 * self.squareSize + self.rectStart[1], self.squareSize, self.squareSize))
        pygame.draw.rect(screen, (242, 206, 232), (0,0, 100, 100))
        # rectst  = [self.rectStart[0] + row1 * self.squareSize, self.rectStart[1] + col1 * self.squareSize, self.squareSize, self.squareSize]
        # pygame.draw.rect(screen, (242, 206, 234), rectst)

    def valid_move(self, row1, col1, row2, col2):
        if(row1 == row2 or col1 == col2):
            return None
        if(row1 < 0 or row1 >= self.dim or col1 < 0 or col1 >= self.dim):
            return None
        if(row2 < 0 or row2 >= self.dim or col2 < 0 or col2 >= self.dim):
            return None
        if(self.board[row1][col1][1] == 0):
            return None
        
        diag = self.diagonal(row1, col1, row2, col2)
        if(diag == None):
            return None
        else:
            return diag

        
    def diagonal(self, row1, col1, row2, col2):
        if(row2 == row1-1 and col2 == col1-1):
            return "GL"
        elif(row2 == row1-1 and col2 == col1+1):
            return "GD"
        elif(row2 == row1+1 and col2 == col1-1):
            return "DL"
        elif(row2 == row1+1 and col2 == col1+1):
            return "DD"

    def get_field_start(self, x, y):
        return [x-self.rectStart[0], y-self.rectStart[1]]