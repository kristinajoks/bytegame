import pygame
from models.board import Board

pygame.init()

screen = pygame.display.set_mode((1200,650))
name = pygame.display.set_caption("Byte Game")
running = True
moving = False

movement = list(range(4))


while running:
    board = Board(8, 560, [500, 50])

    background = screen.fill((245,243,240))
    board.drawInitial(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            movement[0], movement[1] = pygame.mouse.get_pos()      
            rectStart = board.get_field_start(movement[0], movement[1])
            moving = True      
        if event.type == pygame.MOUSEBUTTONUP:
            movement[2], movement[3] = pygame.mouse.get_pos()
            moving = False
            board.move(movement)
        if event.type == pygame.MOUSEMOTION and moving:
            rect = pygame.Rect(rectStart[0], rectStart[1], board.squareSize, board.squareSize)
            #rect.move(movement[0], movement[1])
            print(event.rel)
            bit_image = pygame.image.load('BYTE\\assets\\black.gif')
        #  bit_image.blit(screen, bit_image, (movement[0], movement[1]))
            # bit_image.blit(screen, bit_image, event.rel)
            print(rect)
            # rect.move_ip(event.rel)
            rect.move(event.rel)


    # if(moving):
    #     rect = pygame.Rect(rectStart[0], rectStart[1], board.squareSize, board.squareSize)
    #     rect.move(movement[0], movement[1])



    pygame.display.update()
    pygame.display.flip()
