import pygame
from models.board import Board

pygame.init()

screen = pygame.display.set_mode((800,650))
name = pygame.display.set_caption("Byte Game")
running = True

while running:
    board = Board(8)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    background = screen.fill((245,243,240))
    board.drawInitial(screen)

    pygame.display.flip()

