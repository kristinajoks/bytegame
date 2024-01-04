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


        selected_white_black = 1 if white_black_dropdown.get_selected() == "White" else 0
        selected_board_size = 8 if board_size_dropdown.get_selected() == "8x8" else 10 if board_size_dropdown.get_selected() == "10x10" else 16

        white_black_dropdown.handle_event(event)
        board_size_dropdown.handle_event(event)

        board = Board(selected_board_size, 560, [50, 50], not selected_white_black)

    white_black_dropdown.draw()
    board_size_dropdown.draw()

    start_button.draw()

    pygame.display.flip()

pygame.quit()

pygame.init()
movement = list(range(4))
screenGame = pygame.display.set_mode((650,650))
nameGame = pygame.display.set_caption("Byte Game")

gameOver = False
pygame.font.init()
font = pygame.font.Font(None, 36)

computerPlayed = False
computer_move_start_time = 0
computer_move_delay = 2000 

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
            if(not gameOver and board.computer != board.currentPlayer):
                gameOver = board.play(movement)
                computerPlayed = False                
                computer_move_start_time = pygame.time.get_ticks()  
                

    current_player = board.currentPlayer
    if current_player:
        current_player_text = font.render("White's Turn", True, (0, 0, 0))
        screenGame.blit(current_player_text, (450, 615))
    else:
        current_player_text = font.render("Black's Turn", True, (0, 0, 0))
        screenGame.blit(current_player_text, (60, 20))
    #TODO
    #da se napravi da tekst ide gore levo ili dole desno u zavisnosti i od toga ko je izabran na pocetku
        #i da pise your turn za izabranu boju

    if(not gameOver and board.computer == board.currentPlayer and not computerPlayed):
        current_time = pygame.time.get_ticks()
        if current_time - computer_move_start_time >= computer_move_delay:
            board.play(None)
            computerPlayed = True


    if gameOver == True:
        game_over_text = font.render("Game Over!", True, (0, 0, 0))
        screenGame.blit(game_over_text, (250, 20))

    score_text = font.render(f"(B) {board.users[0].score} : {board.users[1].score} (W)", True, (0, 0, 0))
    screenGame.blit(score_text, (220, 615))

    pygame.display.flip()
   

pygame.quit()