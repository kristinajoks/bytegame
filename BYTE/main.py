import pygame
from models.board import Board
from helpers.drop_down import Dropdown
from helpers.button import Button

pygame.init()

screenWelcome = pygame.display.set_mode((300,500))
nameWelcome = pygame.display.set_caption("Welcome!")

starting = True
running = False

start_button = Button(screenWelcome, (0,0,0), 50, 320, 200, 50, "START", (255,255,255))

white_black_options = ["White", "Black"]
board_size_options = ["8x8", "10x10", "16x16"]


white_black_dropdown = Dropdown(screenWelcome, white_black_options, (50, 50))
board_size_dropdown = Dropdown(screenWelcome, board_size_options, (50, 150))

selected_white_black = None
selected_board_size = None

while starting:
    background = screenWelcome.fill((245, 243, 240))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            starting = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if start_button.is_clicked(mouse_pos):  
                if selected_board_size is not None and selected_white_black is not None:
                    starting = False
                    running = True 


        selected_white_black = white_black_dropdown.get_selected()
        selected_board_size = board_size_dropdown.get_selected()

        white_black_dropdown.handle_event(event)
        board_size_dropdown.handle_event(event)

        if selected_board_size is not None:
            if selected_board_size == "8x8":
                board = Board(8, 560, [50, 50])
            elif selected_board_size == "10x10":
                board = Board(10, 560, [50, 50])
            elif selected_board_size == "16x16":
                board = Board(16, 560, [50, 50])

    white_black_dropdown.draw()
    board_size_dropdown.draw()

    start_button.draw()

    pygame.display.flip()

movement = list(range(4))
screenGame = pygame.display.set_mode((650,650))
nameGame = pygame.display.set_caption("Byte Game")

while running:
    background = screenGame.fill((245, 243, 240))
    board.drawMatrix(screenGame)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            movement[0], movement[1] = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONUP:
            movement[2], movement[3] = pygame.mouse.get_pos()
            board.move(screenGame, movement, 0)

    board.drawMatrix(screenGame)

    pygame.display.flip()
   

pygame.quit()

