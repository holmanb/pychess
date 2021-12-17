#!/usr/bin/env python3

import pieces
import board

DEFAULT_BOARD = [
    pieces.Castle(board.Column.A, 1, pieces.Color.WHITE),
    pieces.Rook(board.Column.B, 1, pieces.Color.WHITE),
    pieces.Bishop(board.Column.C, 1, pieces.Color.WHITE),
    pieces.Queen(board.Column.D, 1, pieces.Color.WHITE),
    pieces.King(board.Column.E, 1, pieces.Color.WHITE),
    pieces.Bishop(board.Column.F, 1, pieces.Color.WHITE),
    pieces.Rook(board.Column.G, 1, pieces.Color.WHITE),
    pieces.Castle(board.Column.H, 1, pieces.Color.WHITE),
    pieces.Pawn(board.Column.A, 2, pieces.Color.WHITE),
    pieces.Pawn(board.Column.B, 2, pieces.Color.WHITE),
    pieces.Pawn(board.Column.C, 2, pieces.Color.WHITE),
    pieces.Pawn(board.Column.D, 2, pieces.Color.WHITE),
    pieces.Pawn(board.Column.E, 2, pieces.Color.WHITE),
    pieces.Pawn(board.Column.F, 2, pieces.Color.WHITE),
    pieces.Pawn(board.Column.G, 2, pieces.Color.WHITE),
    pieces.Pawn(board.Column.H, 2, pieces.Color.WHITE),
    pieces.Castle(board.Column.A, 8, pieces.Color.BLACK),
    pieces.Rook(board.Column.B, 8, pieces.Color.BLACK),
    pieces.Bishop(board.Column.C, 8, pieces.Color.BLACK),
    pieces.Queen(board.Column.D, 8, pieces.Color.BLACK),
    pieces.King(board.Column.E, 8, pieces.Color.BLACK),
    pieces.Bishop(board.Column.F, 8, pieces.Color.BLACK),
    pieces.Rook(board.Column.G, 8, pieces.Color.BLACK),
    pieces.Castle(board.Column.H, 8, pieces.Color.BLACK),
    pieces.Pawn(board.Column.A, 7, pieces.Color.BLACK),
    pieces.Pawn(board.Column.B, 7, pieces.Color.BLACK),
    pieces.Pawn(board.Column.C, 7, pieces.Color.BLACK),
    pieces.Pawn(board.Column.D, 7, pieces.Color.BLACK),
    pieces.Pawn(board.Column.E, 7, pieces.Color.BLACK),
    pieces.Pawn(board.Column.F, 7, pieces.Color.BLACK),
    pieces.Pawn(board.Column.G, 7, pieces.Color.BLACK),
    pieces.Pawn(board.Column.H, 7, pieces.Color.BLACK),
]


def get_user_input():
    pass


def evaluate_user_input():
    pass


def print_board():
    pass


if __name__ == "__main__":
    print(board.Board(DEFAULT_BOARD).prettify())
