#!/usr/bin/env python3

from components import (
    Color,
    Column,
    Board,
    Rook,
    Rook,
    Bishop,
    King,
    Queen,
    Pawn,
)

DEFAULT_BOARD = [
    Rook(Column.A, 1, Color.WHITE),
    Rook(Column.B, 1, Color.WHITE),
    Bishop(Column.C, 1, Color.WHITE),
    Queen(Column.D, 1, Color.WHITE),
    King(Column.E, 1, Color.WHITE),
    Bishop(Column.F, 1, Color.WHITE),
    Rook(Column.G, 1, Color.WHITE),
    Rook(Column.H, 1, Color.WHITE),
    Pawn(Column.A, 2, Color.WHITE),
    Pawn(Column.B, 2, Color.WHITE),
    Pawn(Column.C, 2, Color.WHITE),
    Pawn(Column.D, 2, Color.WHITE),
    Pawn(Column.E, 2, Color.WHITE),
    Pawn(Column.F, 2, Color.WHITE),
    Pawn(Column.G, 2, Color.WHITE),
    Pawn(Column.H, 2, Color.WHITE),
    Rook(Column.A, 8, Color.BLACK),
    Rook(Column.B, 8, Color.BLACK),
    Bishop(Column.C, 8, Color.BLACK),
    Queen(Column.D, 8, Color.BLACK),
    King(Column.E, 8, Color.BLACK),
    Bishop(Column.F, 8, Color.BLACK),
    Rook(Column.G, 8, Color.BLACK),
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


def get_user_input():
    pass


def evaluate_user_input():
    pass


def print_board():
    pass


if __name__ == "__main__":
    print(Board(DEFAULT_BOARD).prettify())
