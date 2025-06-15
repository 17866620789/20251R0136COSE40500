import random
import time
import threading

def create_board(size=19):
    return [["." for _ in range(size)] for _ in range(size)]

def print_board_with_labels(board):
    size = len(board)
    print("  ", end="")
    for col in range(1, size + 1):
        print(f"{col:2}", end=" ")
    print("\n", end="")
    for row in range(size):
        print(f"{row + 1:2}", end=" ")
        for col in range(size):
            print(f"{board[row][col]:2}", end=" ")
        print()
    print("\n")

def check_win(board, player):
    """Check if the current player has won the game."""
    size = len(board)
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Horizontal, Vertical, Diagonal, Anti-Diagonal
    
    for x in range(size):
        for y in range(size):
            if board[x][y] != player:
                continue
            for dx, dy in directions:
                win = True
                for step in range(1, 5):  # Check next 4 pieces in each direction
                    nx, ny = x + step*dx, y + step*dy
                    if nx < 0 or nx >= size or ny < 0 or ny >= size or board[nx][ny] != player:
                        win = False
                        break
                if win:
                    return True
    return False

def ai_move(board, player):
    size = len(board)
    empty_positions = [(x, y) for x in range(size) for y in range(size) if board[x][y] == "."]
    if empty_positions:
        x, y = random.choice(empty_positions)
        board[x][y] = player

def player_choice():
    choice = input("Do you want to play as X (black) or O (white)? [X/O]: ").upper()
    while choice not in ["X", "O"]:
        print("Invalid choice. Please choose X for black or O for white.")
        choice = input("Do you want to play as X (black) or O (white)? [X/O]: ").upper()
    return choice

def timed_input(prompt, timeout=30):
    print(prompt)
    input_line = ''
    def take_input():
        nonlocal input_line
        input_line = input()
    thread = threading.Thread(target=take_input)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        print("\nTime's up! You have exceeded the 30 seconds limit.")
        return None
    else:
        return input_line

def play_game():
    board = create_board()
    player_symbol = player_choice()
    ai_symbol = "O" if player_symbol == "X" else "X"
    current_player = "X"  # X starts the game
    
    while True:
        print(f"Current turn: {current_player}")
        print_board_with_labels(board)
        
        if current_player == player_symbol:
            input_line = timed_input("Enter row and column (e.g., '3 4'): ", 30)
            if input_line:
                try:
                    row, col = map(int, input_line.split())
                    row -= 1
                    col -= 1
                except ValueError:
                    print("Invalid input. Please enter two numbers separated by a space.")
                    continue
                if 0 <= row < len(board) and 0 <= col < len(board) and board[row][col] == ".":
                    board[row][col] = current_player
                else:
                    print("Invalid move, try again.")
                    continue
            else:
                # Skipping turn due to timeout, already handled in the timed_input function.
                print(f"{current_player}'s turn was skipped due to timeout.")
        else:
            ai_move(board, ai_symbol)
        
        if check_win(board, current_player):
            print_board_with_labels(board)
            print(f"Player {current_player} wins!")
            break
        
        current_player = ai_symbol if current_player == player_symbol else player_symbol

if __name__ == "__main__":
    play_game()
