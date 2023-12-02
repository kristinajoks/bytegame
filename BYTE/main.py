import pygame
from models.board import Board

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1200,650))
name = pygame.display.set_caption("Byte Game")
running = True

movement = list(range(4))

board = Board(8, 560, [500, 50])
board.fillMatrix()

while running:

    background = screen.fill((245,243,240))
    board.drawMatrix(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            movement[0], movement[1] = pygame.mouse.get_pos()      
            rectStart = board.get_field_start(movement[0], movement[1])
        if event.type == pygame.MOUSEBUTTONUP:
            movement[2], movement[3] = pygame.mouse.get_pos()
            board.move(screen, movement)

    board.drawMatrix(screen)

    # pygame.display.update()
    pygame.display.flip()
    clock.tick(5)
