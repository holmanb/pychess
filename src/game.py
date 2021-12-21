#!/usr/bin/env python3.10

from prompt import read_move
from components import (
    Color,
    Column,
    Board,
    Player,
    Rook,
    Bishop,
    Knight,
    King,
    Queen,
    Pawn,
)

DEFAULT_WHITE = [
    Rook(Column.A, 1, Color.WHITE),
    Knight(Column.B, 1, Color.WHITE),
    Bishop(Column.C, 1, Color.WHITE),
    Queen(Column.D, 1, Color.WHITE),
    King(Column.E, 1, Color.WHITE),
    Bishop(Column.F, 1, Color.WHITE),
    Knight(Column.G, 1, Color.WHITE),
    Rook(Column.H, 1, Color.WHITE),

    Pawn(Column.A, 2, Color.WHITE),
    Pawn(Column.B, 2, Color.WHITE),
    Pawn(Column.C, 2, Color.WHITE),
    Pawn(Column.D, 2, Color.WHITE),
    Pawn(Column.E, 2, Color.WHITE),
    Pawn(Column.F, 2, Color.WHITE),
    Pawn(Column.G, 2, Color.WHITE),
    Pawn(Column.H, 2, Color.WHITE),
]

DEFAULT_BLACK = [
    Rook(Column.A, 8, Color.BLACK),
    Knight(Column.B, 8, Color.BLACK),
    Bishop(Column.C, 8, Color.BLACK),
    Queen(Column.D, 8, Color.BLACK),
    King(Column.E, 8, Color.BLACK),
    Bishop(Column.F, 8, Color.BLACK),
    Knight(Column.G, 8, Color.BLACK),
    Rook(Column.H, 8, Color.BLACK),

    Pawn(Column.A, 7, Color.BLACK),
    Pawn(Column.B, 7, Color.BLACK),
    Pawn(Column.C, 7, Color.BLACK),
    Pawn(Column.D, 7, Color.BLACK),
    Pawn(Column.E, 7, Color.BLACK),
    Pawn(Column.F, 7, Color.BLACK),
    Pawn(Column.G, 7, Color.BLACK),
    Pawn(Column.H, 7, Color.BLACK),
]

DEFAULT_BOARD = DEFAULT_BLACK + DEFAULT_WHITE


def get_user_input() -> dict:
    return read_move()


def evaluate_user_input():
    pass


def print_board():
    pass


def game_loop(board: Board, white: Player, black: Player):
    """For now, single keyboard input drives both players (for testing)
    """
    try:
        turn = Color.WHITE
        err_msg = ""
        while True:
            try:
                print("{}'s Turn\tMaterial: {}/{}".format(
                    "White" if turn == Color.WHITE else "Black",
                    white.get_material(board), black.get_material(board)))
                print(board.prettify())
                print(err_msg)
                err_msg = ""
                user_in = get_user_input()

                if turn == Color.WHITE:
                    white.move(user_in, board, black)
                if turn == Color.BLACK:
                    black.move(user_in, board, white)

                # Switch turns
                turn = Color.BLACK if turn == Color.WHITE else Color.WHITE
            except ValueError as e:
                err_msg = e
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    board = Board(DEFAULT_BOARD)
    white = Player(Color.WHITE, DEFAULT_WHITE)
    black = Player(Color.BLACK, DEFAULT_BLACK)
    game_loop(board, white, black)
