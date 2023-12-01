import pygame
from models.board import Board

pygame.init()

screen = pygame.display.set_mode((1200,650))
name = pygame.display.set_caption("Byte Game")
running = True

movement = list(range(4))

while running:
    board = Board(8)

    background = screen.fill((245,243,240))
    board.drawInitial(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            movement[0], movement[1] = pygame.mouse.get_pos()            
        elif event.type == pygame.MOUSEBUTTONUP:
            movement[2], movement[3] = pygame.mouse.get_pos()
            print(board.move(movement))
            


    pygame.display.flip()
