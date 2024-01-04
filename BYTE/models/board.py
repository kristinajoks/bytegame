from collections import deque
import math
import pygame
from helpers.binary_helper import * 
from models.user import User

class Board:
    def __init__(self, dim, rectSize, rectStart, computer):
        self.dim = dim
        self.board=[[(bytes([0]), 0) for _ in range(dim)] for _ in range(dim)]
        self.bit = (dim-2)*dim/2
        self.byte = self.bit/8
        self.squareSize = rectSize / dim
        self.bitHeight = 10
        self.rectStart = rectStart
        self.currentPlayer = 1
        self.fillMatrix()
        self.maxStacks = ((self.dim-2) * self.dim)/16
        self.users = [User(0), User(1)] #sluzi samo za dodavanje poena
        self.computer = computer
        

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


    def play(self, movement):        

        if(self.computer != self.currentPlayer): # korisnik

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
    
            if(not self.board[row1][col1][1]):
                return None
            
            if(clicked_bit > self.board[row1][col1][1]):
                positionFrom = self.board[row1][col1][1] - 1
            else:
                positionFrom = int(clicked_bit)

            self.move(row1, col1, row2, col2, positionFrom)

        else:
            best_move = [0, 0, 0, 0, 0] 
            #pitanje da li treba da se salje row i col to i kako da se inicijaizuje pokret
            self.minimax(0, self.NEG_INFINITY, self.POS_INFINITY, True, 1, 1, 0, 0, 0, best_move) 

            self.move(best_move[0], best_move[1], best_move[2], best_move[3], best_move[4]) #bice parametar move


    def move(self, row1, col1, row2, col2, positionFrom): 
        
        validFields = self.calculate_all_possible_moves() 
        #vrati dozvoljene za sve pozicije nevezano za to da li postoji bolji
        #ili ne malo sam zbunjena

        if(validFields is None or len(validFields) == 0): #ako nema dozvoljenih poteza prepusta se
            self.currentPlayer = 0 if self.currentPlayer == 1 else 1 
            return False

        if((row1, col1, row2, col2, positionFrom) not in validFields):
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
        
    
    NEG_INFINITY = float('-inf')
    POS_INFINITY = float('inf')
 
    def minimax(self, depth, alpha, beta, is_max_player, row_from, col_from, row_to, col_to, pos_from, best_move):
        if self.terminal(row_from, col_from, row_to, col_to, pos_from):
            return self.state_value(row_from, col_from)

        if depth == math.log(self.dim, 2):
            return self.evaluate(row_from, col_from, row_to, col_to, pos_from)

        if is_max_player:
            max_eval = self.NEG_INFINITY
            for move in self.calculate_all_possible_moves():
                eval_score = self.minimax(depth + 1, alpha, beta, False, move[0], move[1], move[2], move[3], move[4], best_move)
                if eval_score > max_eval:
                    max_eval = eval_score
                    if depth == 0:
                        best_move[0], best_move[1], best_move[2], best_move[3], best_move[4] = move[0], move[1], move[2], move[3], move[4]
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = self.POS_INFINITY
            for move in self.calculate_all_possible_moves():
                eval_score = self.minimax(depth + 1, alpha, beta, True, move[0], move[1], move[2], move[3], move[4], best_move)
                if eval_score < min_eval:
                    min_eval = eval_score
                    if depth == 0:
                        best_move[0], best_move[1], best_move[2], best_move[3], best_move[4] = move[0], move[1], move[2], move[3], move[4]
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval
      
    #TODO
    #implementirati funkciju koja prevodi stanje u niz cinjenica
    #formulisati skup pravila 
    #nad nizom cinjenica izvesti procenu na osnovu formiranog skupa pravila masinom zakljucivanja

    def evaluate(self, row_from, col_from, row_to, col_to, pos_from): 
        return self.board[row_to][col_to][1] #random vrednost, samo da bi se videlo da li radi minimax


    def terminal(self, row_from, col_from, row_to, col_to, pos_from):
        if(self.users[0].score + self.users[1].score < self.maxStacks - 1): #u sustini != ali ne bi trebalo da sme >
            return False
        if(self.board[row_from][col_from][1] - pos_from + self.board[row_to][col_to][1] < 8): #isto !=
            return False
        
        #ovde znaci da je poslednji potez
        return True


    #ako je terminal, poziva se ova funkcija da odredi pobednika
    def stateValue(self, row_from, col_from):
        if(self.readBit(row_from, col_from, 7) == 1 and self.users[1].score > self.users[0].score):
            return 10
        elif(self.readBit(row_from, col_from, 7) == 0 and self.users[0].score > self.users[1].score):
            return -10
        else:
            return 0
            

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
        
        nearest_nonzero = dict()
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
                nearest_nonzero = self.find_nearest_nonzero(row1, col1)
                
                print(nearest_nonzero)

                if nearest_nonzero: 
                    return nearest_nonzero      
                else:
                    return False
                
            return False
        
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
        allowed_elements = dict()
        my_dict = {(start_row, start_col): lista}
        counter = 0
        while queue:

            if len(lista) == 0:
                if len(my_dict) >= 1:
                    allowed_elements = {k: v for k, v in allowed_elements.items() if k is not None}
                    return allowed_elements
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
                                allowed_elements[(current_row,current_col)] = distance
                            else:
                                allowed_elements[self.return_position((new_row, new_col), (start_row, start_col), my_dict)] = distance

                    if (0 <= new_row < self.dim and 0 <= new_col < self.dim and not visited[new_row][new_col]
                        and (new_row != start_row or new_col != start_col)):
                        queue.append((new_row, new_col))

                    counter += 1
        return allowed_elements


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

            self.writeBits(row, col, [0 for _ in range(8)], 8, True)


    def isOver(self):
        if(self.users[0].score >= self.maxStacks/2 or self.users[1].score >= self.maxStacks/2):
            return True
        return False


    def get_field_start(self, x, y):
        return [x-self.rectStart[0], y-self.rectStart[1]]
    

    def calculate_all_possible_moves(self): 
        possible_moves_best = []
        possible_moves_empty_diagonals = []
        possible_moves = []
        for row in range(self.dim):
            for col in range(self.dim): #mogu da napisem row +1 i range 7 jer nikad ne ide u prvu i poslednjucvrstu

                # za svaki bit, ali dovoljno je da jednom bude True, ako ima vise belih u steku ispitivace za svakog a ne mora
                for bit_position in range(self.board[row][col][1] - 1, -1, -1):
                    bit = self.readBit(row, col, bit_position)
                    if bit == self.currentPlayer:  # da li odgovara trenutnom igracu
                        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                            new_row, new_col = row + dr, col + dc
                            if 0 <= new_row < self.dim and 0 <= new_col < self.dim:
                                # validnost
                                if self.valid_move(row, col, new_row, new_col, bit):   
                                    keys_from_stack_rules = self.stackRules(row, col, new_row, new_col, bit_position)
                                    if isinstance(keys_from_stack_rules, dict):
                                        new_moves = [(row, col, k[0], k[1], v, bit_position) for k, v in keys_from_stack_rules.items()]
                                        for move in new_moves:
                                            if move not in possible_moves_empty_diagonals:
                                                possible_moves_empty_diagonals.append(move)
                                                print(possible_moves_empty_diagonals)
                                                print(new_moves)
                                                print(move)
                                                print("Tu sam")
                                    if keys_from_stack_rules is True: #ovde bi bio najbolji potez
                                        possible_moves_best.append((row, col, new_row, new_col, bit_position))

        if len(possible_moves_best) == 0:
            min_v = min(item[2] for item in possible_moves_empty_diagonals)
            possible_moves_empty_diagonals = [(elem[0], elem[1], elem[2], elem[3], elem[5]) for elem in possible_moves_empty_diagonals if elem[4] == min_v]
            print(possible_moves_empty_diagonals)
            return possible_moves_empty_diagonals
                                    
        return possible_moves_best