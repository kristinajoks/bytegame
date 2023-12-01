import pygame

class Board:
    def __init__(self, dim):
        self.dim = dim
        self.board=[[(bytes([0]), 0) for _ in range(dim)] for _ in range(dim)]
        self.bit = (dim-2)*dim/2
        self.byte = self.bit/8
        self.squareSize = 560 / dim
        self.rectStart = [500, 50]

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


            #razmislicemo
            for(i) in range( int(16/self.dim) - 1):
                bit_image = pygame.transform.scale2x(bit_image)
                
            #bit_image = pygame.transform.scale(bit_image, (self.dim /4 * bit_image.get_width(), self.dim /4 * bit_image.get_height()))
            pygame.Surface.blit(screen, bit_image, (rect[0] + self.squareSize / 4, rect[1] + self.squareSize / 4))


    def writeBit(self, row, col, bit):
        pos = self.board[row][col][1]
        
        if(bit == 1):
            byte = self.board[row][col][0]
            mask = 1 << pos
            print(bin(mask))
            #ovde nesto ne valja
            byte &= ~mask
            byte |= 1 << pos
            pos += 1

            self.board[row][col] = (byte, pos)
        else:
            self.board[row][col] = (self.board[row][col][0], pos + 1)

    def move(self, movement):
        #Potez se sastoji od pozicije polja, mesta figure na steku i smer pomeranja (GL, GD, DL, DD)
        
        x1 = movement[0] - self.rectStart[0]
        y1 = movement[1] - self.rectStart[1]
        x2 = movement[2] - self.rectStart[0]
        y2 = movement[3] - self.rectStart[1]

        row1 = int(y1 / self.squareSize)
        col1 = int(x1 / self.squareSize)
        row2 = int(x2 / self.squareSize)
        col2 = int(y2 / self.squareSize)

        print(row1, col1, row2, col2)

        #valid move function
        isValid = self.valid_move(row1, col1, row2, col2)
        if( isValid == None):
            return
        else:
            return isValid    
        
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
            #gore levo
            return "GL"
        elif(row2 == row1-1 and col2 == col1+1):
            #gore desno
            return "GD"
        elif(row2 == row1+1 and col2 == col1-1):
            #dole levo
            return "DL"
        elif(row2 == row1+1 and col2 == col1+1):
            #dole desno
            return "DD"
