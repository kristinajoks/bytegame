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
            self.minimax(0, self.NEG_INFINITY, self.POS_INFINITY, True, 1, 1, 0, 0, 0, best_move) 

            self.move(best_move[0], best_move[1], best_move[2], best_move[3], best_move[4]) 


    def move(self, row1, col1, row2, col2, positionFrom): 
        
        validFields = self.calculate_all_possible_moves() 

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
            return self.stateValueTerminal(row_from, col_from)

        if depth == math.log(self.dim, 2):
            return self.evaluate(is_max_player, row_from, col_from, row_to, col_to, pos_from)
            # return self.state_value(is_max_player)

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


    def state_value(self, is_max_player):
        total_score = 0

        #tezine su u zbiru 10
        piece_count_weight = 3 #koliko ih ima na tabli (+1 svaki put kada se nadju)
        piece_height_weight = 1 #koliko su visoko u stekovima  
        piece_parity_weight = 1 #da li su pozicije parne 
        piece_topping_weight = 1 #+ da li je ispod tudja boja
        sum_of_stack_height = 1 #koliko su visoki stekovi u kojima se nalaze
        top_color_weight = 2 #na vrhu koliko stekova je boja trenutnog igraca
        position_weight = 1 #da li su orijentisane oko centralnog polja

        piece_count = 0
        pieces_height = 0
        pieces_parity = 0
        pieces_topping = 0
        stacks_height = 0
        top_color_weight_num = 0
        position_weight_num = 0

        for row in range(self.dim):
            for col in range(self.dim):
                for i in range(self.board[row][col][1]):
                    if self.readBit(row, col, i) == self.computer:
                        piece_count += 1
                        pieces_height += i

                        if(i % 2 == 0):
                            pieces_parity += 1
                        
                        if(self.readBit(row, col, i-1) != self.computer):
                            pieces_topping += 1
                        
                        stacks_height += self.board[row][col][1]

                        if( i == self.board[row][col][1] - 1):
                            top_color_weight_num += 1
                        
                        if(row > self.dim/2 - self.dim/4 or row < self.dim/2 + self.dim/4 
                           and col > self.dim/2 - self.dim/4 or col < self.dim/2 + self.dim/4):
                            position_weight_num += 1

        total_score = piece_count * piece_count_weight 
        + pieces_height * piece_height_weight
        + pieces_parity * piece_parity_weight
        + pieces_topping * piece_topping_weight
        + stacks_height * sum_of_stack_height
        + top_color_weight_num * top_color_weight
        + position_weight_num * position_weight

        total_score /= 5.6

        if(is_max_player):
                return total_score
        else:
            return -total_score


    def evaluate(self, is_max_player, row_from, col_from, row_to, col_to, pos_from): 
        total_score = 0

        #tezine su u zbiru 10
        piece_count_weight = 1
        piece_number_weight = 1
        sum_of_pieces_weight = 1
        top_color_weight = 1
        new_position_weight = 1
        direction_weight = 4
        stack_division_weight = 1
    
        piece_count_score = self.evaluate_piece_count()
        total_score += piece_count_score * piece_count_weight

        piece_number_score = self.evaluate_piece_number(row_from, col_from)
        total_score += piece_number_score * piece_number_weight

        sum_of_pieces_score = self.evaluate_sum_of_pieces(row_from, col_from, row_to, col_to, pos_from)
        total_score += sum_of_pieces_score * sum_of_pieces_weight

        top_color_score = self.evaluate_top_color(row_from, col_from)
        total_score += top_color_score * top_color_weight

        new_position_score = self.evaluate_new_position(row_from, col_from, row_to, col_to, pos_from)
        total_score += new_position_score * new_position_weight

        direction_score = self.evaluate_direction(row_from, col_from, row_to, col_to)
        total_score += direction_score * direction_weight

        stack_division_score = 0
        if pos_from != 0:
            stack_division_score = self.evaluate_stack_division(row_from, col_from, row_to, col_to, pos_from)
        total_score += stack_division_score * stack_division_weight

        total_score /= 5.6

        if(is_max_player):
            return total_score
        else:
            return -total_score


    def evaluate_stack_division(self, row_from, col_from, row_to, col_to, pos_from):
        if( self.readBit(row_from, col_from, pos_from - 1) == self.computer):
            return 8
        else:
            return 0
        
        
    def evaluate_direction(self, row_from, col_from, row_to, col_to):
        non_empty_elements = 0

        for row in self.board:
            for element in row:
                if(element[1]>0):
                    non_empty_elements += 1
        
        occupancy = non_empty_elements / self.bit
        
        total_score = 0

        if(occupancy > 0.5):
            if(row_from < self.dim/2):
                total_score += row_to - row_from + self.dim/2 - row_from
            else: 
                total_score += row_from - row_to + row_from - self.dim/2

            if(col_from < self.dim/2):
                total_score += col_to - col_from + self.dim/2 - col_from
            else:
                total_score += col_from - col_to + col_from - self.dim/2
        
        return total_score


    def evaluate_new_position(self, row_from, col_from, row_to, col_to, pos_from):
        total_score = 0 
        if(self.readBit(row_to, col_to, self.board[row_to][col_to][1] - 1) != self.computer):
            total_score += 4
        if (self.board[row_to][col_to][1] - 1) % 2 == 0:
            total_score += 4
        return total_score


    def evaluate_top_color(self, row_from, col_from):
        if self.readBit(row_from, col_from, self.board[row_from][col_from][1] - 1) == self.computer:
            return 8
        return 0


    def evaluate_sum_of_pieces(self, row_from, col_from, row_to, col_to, pos_from):
        return self.board[row_to][col_to][1] + self.board[row_from][col_from][1] - pos_from 


    def evaluate_piece_number(self, row, col):
        return 8 - self.board[row][col][1] 


    def evaluate_piece_count(self):
        max_count = 0
        min_count = 0

        for row in range(self.dim):
            for col in range(self.dim):
                for i in range(self.board[row][col][1]):
                    if self.readBit(row, col, i):
                        max_count += 1
                    else:
                        min_count += 1
        
        return max_count - min_count


    def terminal(self, row_from, col_from, row_to, col_to, pos_from):
        if(self.users[0].score + self.users[1].score < self.maxStacks - 1): 
            return False
        if(self.board[row_from][col_from][1] - pos_from + self.board[row_to][col_to][1] < 8):
            return False
        
        return True


    #ako je terminal, ova funkcija odredjuje pobednika
    def stateValueTerminal(self, row_from, col_from):
        if(self.readBit(row_from, col_from, self.board[row_from][col_from][1] - 1) == 1 and self.users[1].score > self.users[0].score):
            return 10
        elif(self.readBit(row_from, col_from, self.board[row_from][col_from][1] - 1) == 0 and self.users[0].score > self.users[1].score):
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
        nearest_nonzero = dict()

        #pozicija sa koje se pomera je u rangu
        if(positionFrom < 0 or positionFrom >= self.board[row1][col1][1]):
            return None
        
        #broj ukupnih bitova na novom steku je manji od 8
        if(self.board[row2][col2][1] + self.board[row1][col1][1] - positionFrom > 8):
            return False

        if(positionFrom > self.board[row2][col2][1]):
            return False

        if(positionFrom == self.board[row2][col2][1]): 
            if(self.areDiagonalEmpty(row1, col1)):
                #naci najblizi stek i proveriti da li je u pravcu
                nearest_nonzero = self.find_nearest_nonzero(row1, col1)
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

        lista = list(queue).copy()
        lista2 = list()
        allowed_elements = dict()
        my_dict = {(start_row, start_col): lista.copy()}
        counter = 0
        while queue:

            if len(lista) == 0:
                if len(my_dict) >= 1:
                    allowed_elements = {k: v for k, v in allowed_elements.items() if k is not None}  
                    if len(allowed_elements) > 0:
                        return allowed_elements
                    else:
                        elements_to_add = list(queue)[:counter]
                        lista.extend(elements_to_add)
                else: #naredna distanca, da znam zbog vracanja unazad
                    elements_to_add = list(queue)[:counter]
                    lista.extend(elements_to_add)

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
                    my_dict[(current_row, current_col)] = lista2.copy()

                    if(new_row >= 0 and new_row < self.dim and new_col >= 0 and new_col < self.dim): #dodata provera
                        if (self.board[new_row][new_col][1] > 0 and distance != 0):
                            if(distance == 2):
                                allowed_elements[(current_row,current_col)] = distance
                            else:
                                allowed_elements[self.return_position((new_row, new_col), (start_row, start_col), my_dict)] = distance

                    if (0 <= new_row < self.dim and 0 <= new_col < self.dim and not visited[new_row][new_col]
                        and (new_row != start_row or new_col != start_col)):
                        queue.append((new_row, new_col))

                    counter += 1

        allowed_elements = {k: v for k, v in allowed_elements.items() if k is not None}             
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
        return max(abs(start_col - current_col), abs(start_row - current_row))
        
    
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

        for row in range(self.dim):
            for col in range(self.dim): 

                # za svaki bit
                for bit_position in range(self.board[row][col][1] - 1, -1, -1):
                    bit = self.readBit(row, col, bit_position)
                    if bit == self.currentPlayer:  # da li odgovara trenutnom igracu
                        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                            new_row, new_col = row + dr, col + dc
                            if 0 <= new_row < self.dim and 0 <= new_col < self.dim: #mogla bi da se unapredi provera da ako je tu crni bit prvi ne proverava dalje takodje jer sigurno ne moze da se pomeri
                                # validnost
                                if self.valid_move(row, col, new_row, new_col, bit):   
                                    keys_from_stack_rules = self.stackRules(row, col, new_row, new_col, bit_position)
                                    if isinstance(keys_from_stack_rules, dict):
                                        new_moves = [(row, col, k[0], k[1], v, bit_position) for k, v in keys_from_stack_rules.items()]
                                        for move in new_moves:
                                            if move not in possible_moves_empty_diagonals:
                                                possible_moves_empty_diagonals.append(move)

                                    if keys_from_stack_rules is True: #ovde bi bio najbolji potez
                                        possible_moves_best.append((row, col, new_row, new_col, bit_position))

        if len(possible_moves_best) == 0:
            min_v = min(item[4] for item in possible_moves_empty_diagonals)
            possible_moves_empty_diagonals = [(elem[0], elem[1], elem[2], elem[3], elem[5]) for elem in possible_moves_empty_diagonals if elem[4] == min_v]

            return possible_moves_empty_diagonals
                                    
        return possible_moves_best