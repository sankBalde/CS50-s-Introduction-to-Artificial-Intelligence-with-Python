"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def count(board, p):
    c = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == p:
                c += 1
    return c

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    nbr_X = count(board, X)
    nbr_O = count(board, O)
    if nbr_X == nbr_O:
        return X
    elif nbr_X > nbr_O:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    tab_of_actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                tab_of_actions.add((i, j))
    if len(tab_of_actions) == 0:
        return None
    else:
        return tab_of_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Not a valid action")
    else:
        # deep copy of the board
        new_board = [row[:] for row in board]
        new_board[action[0]][action[1]] = player(board)
        return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check if there is a winner in the rows
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != EMPTY:
            return board[i][0]
    # check if there is a winner in the columns
    for j in range(3):
        if board[0][j] == board[1][j] == board[2][j] and board[0][j] != EMPTY:
            return board[0][j]
    # check if there is a winner in the diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    if board[2][0] == board[1][1] == board[0][2] and board[2][0] != EMPTY:
        return board[2][0]
    # otherwise return None
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    elif actions(board) is None:
        return True
    else:
        return False

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    else:
        if player(board) == X:
            option = (0, 0)
            max_ = -math.inf
            for action in actions(board):
                if min_value(result(board, action)) > max_:
                    max_ = min_value(result(board, action))
                    option = action
            return option
        elif player(board) == O:
            option = (0, 0)
            min_ = math.inf
            for action in actions(board):
                if max_value(result(board, action)) < min_:
                    min_ = max_value(result(board, action))
                    option = action
            return option

def max_value(board):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v
