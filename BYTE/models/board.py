from collections import deque
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
        self.bitHeight = 10;
        self.rectStart = rectStart
        self.currentPlayer = 1
        self.fillMatrix()
        self.maxStacks = ((self.dim-2) * self.dim)/16
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
                            
                            outline_image = pygame.image.load('BYTE\\assets\\outline.gif')
                            outline_image = pygame.transform.scale(outline_image, (self.squareSize/2, self.squareSize/2))
                            pygame.Surface.blit(screen, outline_image, (rect[0] + self.squareSize / 4, rect[1] + self.squareSize / 2 + stack_offset))
                            
                            stack_offset -= self.bitHeight; 


                else:
                    color = (242,206,234)
                    pygame.draw.rect(screen, color, rect)

                x_offset += self.squareSize

            x_offset = 0
            y_offset += self.squareSize


    def readBit(self, row, col, pos): #positionFrom
        if pos >= 0:
            byte = self.board[row][col][0]
            mask = 1 << (pos)
            result = int.from_bytes(byte, byteorder="big") & mask
            return result > 0
        else:
            return None


    def writeBits(self, row, col, bits, numOfBits, overwrite): #dodati poziciju sa koje se pomera
        
        if(overwrite):
            #upisuje od pos - numOfBits
            pos = self.board[row][col][1] - numOfBits
        else:
            pos = self.board[row][col][1]
        
        byte = self.board[row][col][0]

        i=0
        for i in range(numOfBits):

            mask = 1 << pos
            negatedMask = bitwise_not_bytes(bytes([mask]))
            maskedByte = bitwise_and_bytes(byte, negatedMask)

            writtenByte = bitwise_or_bytes(maskedByte, bytes([bits[i] << pos]))

            byte = writtenByte

            pos += 1

        if(overwrite):
            pos = self.board[row][col][1] - numOfBits

        self.board[row][col] = (byte, pos)



    def move(self, movement, positionFrom): 
        
        x1, y1 = self.get_field_start(movement[0], movement[1])
        x2, y2 = self.get_field_start(movement[2], movement[3])

        row1 = int(y1 / self.squareSize)
        col1 = int(x1 / self.squareSize)
        row2 = int(y2 / self.squareSize)
        col2 = int(x2 / self.squareSize)


        isValid = self.valid_move(row1, col1, row2, col2, positionFrom)
        if( isValid == None):
            return

        #citanje
        bits = []

        numOfBits = self.board[row1][col1][1]
        for i in range(positionFrom, numOfBits):
            bits.append(self.readBit(row1, col1, i)) 
            
        #brisanje
        self.writeBits(row1, col1, [0 for _ in range(numOfBits)], numOfBits, True)

        #upis
        self.writeBits(row2, col2, bits, numOfBits, False)

        self.currentPlayer = 0 if self.currentPlayer == 1 else 1
        
        #provera da li je neki stek popunjen
        self.updateScore(row2, col2)

        #provera da li je gotova igra
        #if(self.isOver):
            #prikazi poruku i resetuj

        
    def valid_move(self, row1, col1, row2, col2, positionFrom):
        if(row1 == row2 or col1 == col2):
            return None
        if(row1 < 0 or row1 >= self.dim or col1 < 0 or col1 >= self.dim):
            return None
        if(row2 < 0 or row2 >= self.dim or col2 < 0 or col2 >= self.dim):
            return None
        if(self.board[row1][col1][1] == 0):
            return None
        if(self.board[row2][col2][1] == 8):
            return None

       #provera sa user.color 
        if(self.currentPlayer == 1 and row1 % 2 != 0 or self.currentPlayer == 0 and row1 % 2 != 1):
            return None
        
        #dodati uslovi za valjanost poteza
        #pozicija sa koje se pomera je u rangu
        if(positionFrom < 0 or positionFrom >= self.board[row1][col1][1]):
            return None
        
        self.stackRules(row1, col1, row2, col2, positionFrom)

        #ovaj uslov izmeniti da se ipak dozvoljava prazno polje, 
        # ali samo ukoliko su sva okolna prazna i 
        # odabrano polje je u pravcu nekog postojeceg steka
        if(self.board[row2][col2][1] == 0):
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


    #Realizovati funkcije koje proveravaju da li su susedna polja prazna
    def areDiagonalEmpty(self, row, col):
        #samo za proveru su stampanja
        ll = self.board[row-1][col-1][1]
        lr = self.board[row-1][col+1][1]
        ul = self.board[row+1][col-1][1]
        ur = self.board[row+1][col+1][1]

        print(ll == 0)
        print(lr == 0)
        print(ul == 0)
        print(ur == 0)


        if(self.board[row-1][col-1][1] == 0 and self.board[row-1][col+1][1] == 0 
           and self.board[row+1][col-1][1] == 0 and self.board[row+1][col+1][1] == 0):
            return True
        return False


    #-Realizovati funkcije koje na osnovu konkretnog poteza i stanje igre proveravaju 
    #da li se potez može odigrati prema pravilima pomeranja definisanim za stekove
    def stackRules(self, row1, col1, row2, col2, positionFrom):
        #broj ukupnih bitova na novom steku je manji od 8
        if(self.board[row2][col2][1] + self.board[row1][col1][1] - positionFrom > 8):
            return None
        
        #bitovi se pomeraju na visu ili jednaku poziciju
        if(positionFrom > self.board[row1][col1][1] - 1):
            return None
        
        if(self.areDiagonalEmpty(row1, col1)):
            #naci najblizi stek i proveriti da li je u pravcu
            #ako jeste, onda je dozvoljeno

            nzrow, nzcol = self.find_nearest_nonzero(row1, col1)
            print(nzrow, nzcol)


    def find_nearest_nonzero(self, start_row, start_col):
        #DL, DD, GL, GD
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        visited = [[False for _ in range(len(self.board[0]))] for _ in range(len(self.board))]

        # queue = deque([(start_row, start_col)])
        queue = deque([(start_row + dr, start_col + dc) for dr, dc in directions])


        while queue:
            current_row, current_col = queue.popleft()
            visited[current_row][current_col] = True

            #opet ovaj uslov vec postoji
            if self.board[current_row][current_col][1] != 0:
                print(self.board[current_row][current_col])
                return current_row, current_col

            #iterativno obilazi susede, jer python nekad brzo ogranicava rekurziju
            for dr, dc in directions:
                new_row, new_col = current_row + dr, current_col + dc

                #u granicama matrice i nije posecen, ali mozda mogu i da se izbace uslovi za granicu
                if (new_row != start_row and new_col != start_col and 
                    0 <= new_row < len(self.board) and 0 <= new_col < len(self.board[0]) 
                    and not visited[new_row][new_col]):
                    queue.append((new_row, new_col))

        return None, None


    def updateScore(self, row, col):
        if(self.board[row][col][1] == 8):
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