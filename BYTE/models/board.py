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


    def move(self, movement): 
        
        x1, y1 = self.get_field_start(movement[0], movement[1])
        x2, y2 = self.get_field_start(movement[2], movement[3])

        row1 = int(y1 / self.squareSize)
        col1 = int(x1 / self.squareSize)
        row2 = int(y2 / self.squareSize)
        col2 = int(x2 / self.squareSize)

        clicked_bit = int(((row1 + 1) * self.squareSize) - y1 ) / self.bitHeight

        positionFrom = 0
        if(clicked_bit < 0):
            return None
 
        ###
        
        if(not self.board[row1][col1][1]):
            return None
        
        if(clicked_bit > self.board[row1][col1][1]):
            positionFrom = self.board[row1][col1][1] - 1
        else:
            positionFrom = int(clicked_bit)


        validFields = self.calculate_all_possible_moves()

        if(validFields is None or len(validFields) == 0): #ako nema dozvoljenih poteza prepusta se
            self.currentPlayer = 0 if self.currentPlayer == 1 else 1 
            return False

        if((row1, col1, row2, col2) not in validFields):
            return None 
       
        #citanje
        bits = []

        numOfBits = self.board[row1][col1][1] - positionFrom
        for i in range(numOfBits):
            bits.append(self.readBit(row1, col1, positionFrom + i))

        #brisanje
        self.writeBits(row1, col1, [0 for _ in range(numOfBits)], numOfBits, True)

        #upis
        self.writeBits(row2, col2, bits, numOfBits, False)

        self.currentPlayer = 0 if self.currentPlayer == 1 else 1
        
        self.updateScore(row2, col2)

        if(self.isOver()):
            return True
        
    def valid_move(self, row1, col1, row2, col2, bit):
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
        if(self.currentPlayer == 1 and bit == 0 or self.currentPlayer == 0 and bit == 1):
            return None
        
        # Provera da li je potez dijagonalan
        diag = self.diagonal(row1, col1, row2, col2)
        return diag if diag is not None else None

        
    def diagonal(self, row1, col1, row2, col2):
        if(row2 == row1-1 and col2 == col1-1):
            return "GL"
        elif(row2 == row1-1 and col2 == col1+1):
            return "GD"
        elif(row2 == row1+1 and col2 == col1-1):
            return "DL"
        elif(row2 == row1+1 and col2 == col1+1):
            return "DD"


    def is_in_direction(self, start_row, start_col, target_row, target_col, stack_pos):
        # vektori
        direction_to_target = (target_row - start_row, target_col - start_col)
        direction_to_stack = (stack_pos[0] - start_row, stack_pos[1] - start_col)

        # da li su u istom pravcu
        cross_product = direction_to_target[0] * direction_to_stack[1] - direction_to_target[1] * direction_to_stack[0]

        return cross_product == 0
    

    def areDiagonalEmpty(self, row, col):
        # DL
        ll = 0
        if (row - 1 >= 0 and col - 1 >= 0 and row - 1 < len(self.board) and col - 1 < len(self.board[0])):
            ll = self.board[row - 1][col - 1][1]

        # DD
        lr = 0
        if (row - 1 >= 0 and col + 1 >= 0 and row - 1 < len(self.board) and col + 1 < len(self.board[0])):
            lr = self.board[row - 1][col + 1][1]

        # GL
        ul = 0
        if (row + 1 >= 0 and col - 1 >= 0 and row + 1 < len(self.board) and col - 1 < len(self.board[0])):
            ul = self.board[row + 1][col - 1][1]

        # GD
        ur = 0
        if (row + 1 >= 0 and col + 1 >= 0 and row + 1 < len(self.board) and col + 1 < len(self.board[0])):
            ur = self.board[row + 1][col + 1][1]

        # Provera da li su sva dijagonalna polja prazna
        if ll == 0 and lr == 0 and ul == 0 and ur == 0:
            return True
        
        return False


    def stackRules(self, row1, col1, row2, col2, positionFrom):
        #pozicija sa koje se pomera je u rangu
        if(positionFrom < 0 or positionFrom >= self.board[row1][col1][1]):
            return None
        
        lista = list()
        #broj ukupnih bitova na novom steku je manji od 8
        if(self.board[row2][col2][1] + self.board[row1][col1][1] - positionFrom > 8):
            return False

        #bitovi se pomeraju na visu ili jednaku poziciju
        #to ne vazi kad su sva polja okolo prazna 
        if(positionFrom > self.board[row2][col2][1]):
            return False

        if(positionFrom == self.board[row2][col2][1]): 
            if(self.areDiagonalEmpty(row1, col1)):
                #naci najblizi stek i proveriti da li je u pravcu
                #ako jeste, onda je dozvoljeno
                lista.extend(self.find_nearest_nonzero(row1, col1))
                lista = list(set(lista)) 

                if(lista is None or len(lista) == 0):
                    return False

<<<<<<< HEAD
                return True             
            
=======
                # print(lista) #ovde sada vraca listu dozvoljenog kretanja za bit koji sam pomerila!!!
                # return True 
                return lista            
               
                #treba prvo da se vidi da li je neki bit bolji za pomeranje pa da se zove za njega
                #fja dozvoljenih svih poteza ->ona moja da se proveri
                # if nzrow is not None and self.is_in_direction(row1, col1, nzrow, nzcol, (row2, col2)):
                #     return True
>>>>>>> 2fb12464ce5efdb0064c8709deefee3ef19a6117
                
            return False #ne sme da se pomeri na istu poziciju ako nisu prazne sve dijagonale
        
        return True


    def find_nearest_nonzero(self, start_row, start_col):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        visited = [[False for _ in range(self.dim)] for _ in range(self.dim)]
        queue = deque([(start_row + dr, start_col + dc)
            for dr, dc in directions
            if 0 < start_row + dr < len(self.board) and 0 < start_col + dc < len(self.board[0])
            ])

        lista = list(queue)
        lista2 = list()
        allowed_list = list()
        my_dict = {(start_row, start_col): lista}
        counter = 0
        while queue:

            if len(lista) == 0:
                if len(my_dict) >= 1:
                    allowed_list = [x for x in allowed_list if x is not None]
                    return allowed_list
                else: #naredna distanca, da znam zbog vracanja unazad
                    for _ in range(counter):
                        if queue:
                            lista.append(queue.popleft())
                        else:
                            break
            else:
                current_row, current_col= queue.popleft()
                lista2.clear()
                lista.remove((current_row,current_col))
                visited[current_row][current_col] = True
                
               
                for dr, dc in directions:
                    new_row, new_col = current_row + dr, current_col + dc
                    distance = self.calculate_distance(start_row, new_row, start_col, new_col)
                    #value
                    lista2.append((new_row,new_col))
                    my_dict = {(current_row, current_col): lista2}

                    if(new_row > 0 and new_row < self.dim and new_col > 0 and new_col < self.dim): #dodata provera
                        if self.board[new_row][new_col][1] > 0:
                            if(distance == 2):
                                allowed_list.append((current_row, current_col))
                            else:
                                allowed_list.append(self.return_position((new_row, new_col), (start_row, start_col), my_dict))

                    if (0 <= new_row < self.dim and 0 <= new_col < self.dim and not visited[new_row][new_col]
                        and (new_row != start_row or new_col != start_col)):
                        queue.append((new_row, new_col))

                    counter += 1
        return allowed_list


    def return_position(self, start, target, my_dict):
        visited = set()
        queue = [(start, [start])]

        while queue:
            current, path = queue.pop(0)
            if current == target:
                #da li je startna pozicija u putanji
                if start in path:
                    # prva pre ciljne
                    for i in range(len(path) - 1, 0, -1):
                        if path[i] == target and i > 1:  # element pre ciljne
                            return path[i - 1]
                else:
                    
                    return path
            
            if current not in visited:
                visited.add(current)
                for key, value in my_dict.items():
                    neighbors = value 
                    if current in neighbors:
                        queue.append((key, path + [key]))

        return None


    def calculate_distance(self, start_row, current_row, start_col, current_col):
        if(start_row == current_row): 
            return abs(start_col - current_col)
        
        return abs(start_row - current_row)
        
    
    def updateScore(self, row, col):
        if(self.board[row][col][1] == 8):
            resColor = self.readBit(row, col, 7)
            for u in self.users:
                if(u.color == resColor):
                    u.score += 1


    def isOver(self):
        if(self.users[0].score >= self.maxStacks/2 or self.users[1].score >= self.maxStacks/2):
            return True
        return False


    def get_field_start(self, x, y):
        return [x-self.rectStart[0], y-self.rectStart[1]]
    

    def calculate_all_possible_moves(self): 
        possible_moves = []
        empty_moves = []
        for row in range(self.dim):
            for col in range(self.dim):
<<<<<<< HEAD
                # Proverava svaki bit počevši od najvišeg
                for bit_position in range(self.board[row][col][1] - 1, -1, -1):
                    bit = self.readBit(row, col, bit_position)
                    if bit == self.currentPlayer:  # Proverava da li bit odgovara trenutnom igraču
                        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                            new_row, new_col = row + dr, col + dc
                            if 0 <= new_row < self.dim and 0 <= new_col < self.dim:
                                # Provera validnosti poteza za bit na trenutnoj poziciji i sve iznad njega
                                if self.valid_move(row, col, new_row, new_col, bit): 
                                    if self.stackRules(row, col, new_row, new_col, bit_position):
                                        possible_moves.append((row, col, new_row, new_col)) 
        return possible_moves
=======
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    new_row, new_col = row + dr, col + dc
                    
                    if 0 <= new_row < self.dim and 0 <= new_col < self.dim:
                        #za dato polje, treba proveriti za svaki bit

                        for i in range(self.board[row][col][1]):
                            bit = self.readBit(row, col, i)
                            
                            if self.valid_move(row, col, new_row, new_col, bit): 
                                tmp = self.stackRules(row, col, new_row, new_col, i)
                                
                                # if(type(tmp) is list and len(tmp) > 0):
                                #     empty_moves.append((row, col, tmp[0][0], tmp[0][1], i))
                                #     empty_moves = list(set(empty_moves))

                                if(tmp):
                                    possible_moves.append((row, col, new_row, new_col, i)) 

        if(len(possible_moves) == 0):
            return empty_moves
        
        return possible_moves
>>>>>>> 2fb12464ce5efdb0064c8709deefee3ef19a6117
