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
        self.currentPlayer = 1
        self.fillMatrix()


    def fillMatrix(self):
         for row in range(self.dim):
            for col in range(self.dim):
                if(row != 0 and row != self.dim - 1):
                    if(row%2 == 0 and col %2 == 0 or row%2 == 1 and col%2 == 1):
                        if(row %2 == 0):
                            self.writeBit(row, col, 1, self.board[row][col][1])
                        else:
                            self.writeBit(row, col, 0, self.board[row][col][1])


    def drawMatrix(self, screen):
        x_offset = 0
        y_offset = 0
        color = ()

        for row in range(self.dim):
            for col in range(self.dim):
                rect = [self.rectStart[0] + x_offset, self.rectStart[1] + y_offset, self.squareSize, self.squareSize]
                stack_offset = 0
               
                if(row%2 == 0 and col %2 == 0 or row%2 == 1 and col%2 == 1):
                    color = (210,115,187)
                    pygame.draw.rect(screen, color, rect)

                    if(self.board[row][col][1]>0):
                        for (i) in range(self.board[row][col][1]):
                            if(self.readBit(row, col, i+1)):
                                bit_image = pygame.image.load('BYTE\\assets\\white.gif')
                            else:
                                bit_image = pygame.image.load('BYTE\\assets\\black.gif') 

                            bit_image = pygame.transform.scale(bit_image, (self.squareSize/2, self.squareSize/2))    
                            pygame.Surface.blit(screen, bit_image, (rect[0] + self.squareSize / 4, rect[1] + self.squareSize / 2 + stack_offset))
                            stack_offset -= 10 #bice druga vrednost

                else:
                    color = (242,206,234)
                    pygame.draw.rect(screen, color, rect)

                x_offset += self.squareSize

            x_offset = 0
            y_offset += self.squareSize


    def readBit(self, row, col, pos): #positionFrom
        # pos = self.board[row][col][1]
        if pos > 0:
            byte = self.board[row][col][0]
            mask = 1 << (pos - 1)
            result = int.from_bytes(byte, byteorder="big") & mask
            return result > 0
        else:
            return None


    def writeBit(self, row, col, bit, positionTo): #dodati poziciju sa koje se pomera
        pos = self.board[row][col][1]
        
        byte = self.board[row][col][0]

        mask = 1 << pos
        negatedMask = bitwise_not_bytes(bytes([mask]))
        maskedByte = bitwise_and_bytes(byte, negatedMask)

        if(bit == 1):
            writtenByte = bitwise_or_bytes(maskedByte, bytes([1 << pos]))
        else:            
            writtenByte = bitwise_or_bytes(maskedByte, bytes([0 << pos]))

        # u kom uslovu =
        if(positionTo >= pos):
            pos += 1
        else:
            pos -= 1

        self.board[row][col] = (writtenByte, pos)


    def move(self, screen, movement, positionFrom):   
        
        x1, y1 = self.get_field_start(movement[0], movement[1])
        x2, y2 = self.get_field_start(movement[2], movement[3])

        row1 = int(y1 / self.squareSize)
        col1 = int(x1 / self.squareSize)
        row2 = int(y2 / self.squareSize)
        col2 = int(x2 / self.squareSize)

        print(row1, col1, "to", row2, col2)

        isValid = self.valid_move(row1, col1, row2, col2)
        if( isValid == None):
            return

        if(self.board[row1][col1][1] == 1):
            self.writeBit(row1, col1, 0, positionFrom)
            pos = self.board[row1][col1][1]
            self.board[row1][col1] = (self.board[row1][col1][0], pos)

            self.writeBit(row2, col2, self.currentPlayer, self.board[row2][col2][1])

            self.currentPlayer = 0 if self.currentPlayer == 1 else 1
            return

        #prvo procita bitove sa pozicije sa koje se pomera i cuvam ih u nizu
        bits = []
        
        #brise sa pozicije sa koje se pomera
        numOfBits = self.board[row1][col1][1]
        for i in range(positionFrom, numOfBits):
            bits.append(self.readBit(row1, col1, i + 1))

            self.writeBit(row1, col1, 0, i)
            pos = self.board[row1][col1][1]
            self.board[row1][col1] = (self.board[row1][col1][0], pos)

        #dodaje na poziciju na koju se pomera
        j=0
        for i in range(positionFrom, numOfBits):
            self.writeBit(row2, col2, bits[j], numOfBits + i)
            j+=1


        
    def valid_move(self, row1, col1, row2, col2):
        if(row1 == row2 or col1 == col2):
            return None
        if(row1 < 0 or row1 >= self.dim or col1 < 0 or col1 >= self.dim):
            return None
        if(row2 < 0 or row2 >= self.dim or col2 < 0 or col2 >= self.dim):
            return None
        if(self.board[row1][col1][1] == 0):
            return None
        if(self.board[row2][col2][1] == 0):
            return None
        
        if(self.currentPlayer == 1 and row1 % 2 != 0 or self.currentPlayer == 0 and row1 % 2 != 1):
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