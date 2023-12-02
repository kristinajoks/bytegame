import pygame
from models.board import Board
from helpers.drop_down import Dropdown

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1200,650))
name = pygame.display.set_caption("Byte Game")
running = True

movement = list(range(4))

board = Board(8, 560, [500, 50])
# board.fillMatrix()


white_black_options = ["White", "Black"]
board_size_options = ["8x8", "10x10", "16x16"]
white_black_dropdown = Dropdown(screen, white_black_options, (50, 50))
board_size_dropdown = Dropdown(screen, board_size_options, (50, 200))

while running:
    background = screen.fill((245, 243, 240))
    board.drawMatrix(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        white_black_dropdown.handle_event(event)
        board_size_dropdown.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            movement[0], movement[1] = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONUP:
            movement[2], movement[3] = pygame.mouse.get_pos()
            print(movement)
            board.move(screen, movement, 0)

    white_black_option = white_black_dropdown.selected_option
    board_size_option = board_size_dropdown.selected_option

    if board_size_option is not None:
        if board_size_option == "8x8":
            board = Board(8, 560, [500, 50])
        elif board_size_option == "10x10":
            board = Board(10, 560, [500, 50])
        elif board_size_option == "16x16":
            board = Board(16, 560, [500, 50])

    white_black_dropdown.draw()
    board_size_dropdown.draw()
    
    board.drawMatrix(screen)

    pygame.display.flip()
    clock.tick(5)

