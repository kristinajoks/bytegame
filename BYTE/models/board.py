import pygame
from helpers.binary_helper import * 
from models.user import User

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
        self.maxStacks = (self.dim-2 * self.dim)/16
        self.users = [User(0), User(1)] #sluzi samo za dodavanje poena
        

    def fillMatrix(self):
         for row in range(self.dim):
            for col in range(self.dim):
                if(row != 0 and row != self.dim - 1):
                    if(row%2 == 0 and col %2 == 0 or row%2 == 1 and col%2 == 1):
                        if(row %2 == 0):
                            self.writeBits(row, col, [1], 1, False)
                        else:
                            self.writeBits(row, col, [0], 1, False)


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
                            if(self.readBit(row, col, i)): #obrisano +1
                                bit_image = pygame.image.load('BYTE\\assets\\white.gif')
                            else:
                                bit_image = pygame.image.load('BYTE\\assets\\black.gif') 

                            bit_image = pygame.transform.scale(bit_image, (self.squareSize/2, self.squareSize/2))    
                            pygame.Surface.blit(screen, bit_image, (rect[0] + self.squareSize / 4, rect[1] + self.squareSize / 2 + stack_offset))
                            stack_offset -= 10 

                else:
                    color = (242,206,234)
                    pygame.draw.rect(screen, color, rect)

                x_offset += self.squareSize

            x_offset = 0
            y_offset += self.squareSize


    def readBit(self, row, col, pos): #positionFrom
        # pos = self.board[row][col][1]
        if pos >= 0:
            byte = self.board[row][col][0]
            mask = 1 << (pos)
            result = int.from_bytes(byte, byteorder="big") & mask
            return result > 0
        else:
            return None


    def writeBits(self, row, col, bits, numOfBits, overwrite): #dodati poziciju sa koje se pomera
        
        if(overwrite):
            #upisuje od pos- numOfBits
            pos = self.board[row][col][1] - numOfBits
        else:
            pos = self.board[row][col][1]
        
        #writtenByte ovde dekl
        writtenByteFinal = bytes([0])

        i=0
        for i in range(numOfBits):
            
            byte = self.board[row][col][0]

            mask = 1 << pos
            negatedMask = bitwise_not_bytes(bytes([mask]))
            maskedByte = bitwise_and_bytes(byte, negatedMask)

            writtenByte = bitwise_or_bytes(maskedByte, bytes([bits[i] << pos]))
            #brise se writtenbyte izmedju iteracija nesto tako
            writtenByteFinal = bitwise_or_bytes(writtenByteFinal, writtenByte)

            pos += 1

        if(overwrite):
            pos = self.board[row][col][1] - numOfBits

        self.board[row][col] = (writtenByte, pos)



    def move(self, movement, positionFrom):  #obrisati screen 
        
        x1, y1 = self.get_field_start(movement[0], movement[1])
        x2, y2 = self.get_field_start(movement[2], movement[3])

        row1 = int(y1 / self.squareSize)
        col1 = int(x1 / self.squareSize)
        row2 = int(y2 / self.squareSize)
        col2 = int(x2 / self.squareSize)

        isValid = self.valid_move(row1, col1, row2, col2)
        if( isValid == None):
            return

        #prvo procita bitove sa pozicije sa koje se pomera i cuva ih u nizu
        bits = []

        #brise sa pozicije sa koje se pomera
        numOfBits = self.board[row1][col1][1]
        for i in range(positionFrom, numOfBits):
            #cita bitove sa pozicije
            bits.append(self.readBit(row1, col1, i)) #obrisano +1
            
        #brisanje
        self.writeBits(row1, col1, [0 for _ in range(numOfBits)], numOfBits, True) #da li +1

        #upis
        self.writeBits(row2, col2, bits, numOfBits, False)

        self.currentPlayer = 0 if self.currentPlayer == 1 else 1
        
        #provera da li je neki stek popunjen
        self.updateScore(row2, col2)

        #provera da li je gotova igra
        #if(self.isOver):
            #prikazi poruku i resetuj

        
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

       #provera sa user.color 
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

    def updateScore(self, row, col):
        #cita da li ima 8b, ako ima onda dodaje poen
        if(self.board[row][col][1] == 8):
            #cita poslednji dodati bit i dodaje odgovarajucem
            resColor = self.readBit(row, col, 7)
            for u in self.users:
                if(u.color == resColor):
                    u.score += 1

    def isOver(self):
        if(self.users[self.currentPlayer].score >= self.maxStacks/2):
            return True
        return False

    def get_field_start(self, x, y):
        return [x-self.rectStart[0], y-self.rectStart[1]]