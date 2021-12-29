from typing import List

import pytest
from pytest import raises

from ..game import Chess
from ..components import (
    Color,
    Piece,
    Column,
    Board,
    Pawn,
    Rook,
    Bishop,
    Knight,
    Queen,
    King,
    Player,
    Index,
    Position,
    position_to_index,
    index_to_position,
    index_valid_or_raise,
)


class TestHelpers:
    def pos_index(self):
        assert Index(0, 0) == position_to_index(Position(Column.A, 1))
        assert Index(7, 7) == position_to_index(Position(Column.H, 8))

    def index_pos(self):
        assert Position(Column.A, 1) == index_to_position(Index(0, 0))
        assert Position(Column.H, 8) == index_to_position(Index(7, 7))

    def bounds_check(self):
        with raises(ValueError):
            index_valid_or_raise(Index(-1, 0))
            index_valid_or_raise(Index(0, -1))
            index_valid_or_raise(Index(8, 0))
            index_valid_or_raise(Index(0, 8))


class TestPieces:
    def test_piece_move_to(self):
        p = Piece(Column.A, 1, Color.BLACK)
        p.move_to_position(Position(Column.H, 2))
        assert p.get_position() == Index(Column.H, 2)

    def test_piece_get_relative_position(self):
        p1 = Piece(Column.A, 1, Color.BLACK)
        p2 = Piece(Column.A, 2, Color.WHITE)
        b = Board([p1, p2])
        assert p2 == p1.get_relative_index(b, 0, 1)
        assert p1 == p2.get_relative_index(b, 0, -1)

    def test_piece_get_relative_position_color(self):
        p1 = Piece(Column.A, 1, Color.BLACK)
        p2 = Piece(Column.A, 2, Color.WHITE)
        b = Board([p1, p2])
        assert Color.WHITE == p1.get_relative_index_color(b, 0, 1)
        assert Color.BLACK == p2.get_relative_index_color(b, 0, -1)


class TestPawn:
    def test_pawn_get_possible_moves_no_blocks(self):
        p1 = Pawn(Column.B, 2, Color.WHITE)
        b = Board([p1])
        assert (Column.B, 3) in p1.get_possible_moves_position(b)
        assert (Column.B, 4) in p1.get_possible_moves_position(b)

    def test_pawn_get_possible_moves_blocked(self):
        p1 = Pawn(Column.B, 2, Color.WHITE)
        p2 = Pawn(Column.B, 3, Color.WHITE)
        b = Board([p1, p2])
        assert [] == p1.get_possible_moves_position(b)

    def test_pawn_get_possible_moves_blocked_attack(self):
        p1 = Pawn(Column.B, 2, Color.WHITE)
        p2 = Pawn(Column.B, 3, Color.WHITE)
        p3 = Pawn(Column.A, 3, Color.BLACK)
        b = Board([p1, p2, p3])
        assert [(Column.A, 3)] == p1.get_possible_moves_position(b)

    def test_pawn_get_possible_moves_blocked_attack_two(self):
        p1 = Pawn(Column.B, 2, Color.WHITE)
        p2 = Pawn(Column.B, 3, Color.WHITE)
        p3 = Pawn(Column.A, 3, Color.WHITE)
        p4 = Pawn(Column.C, 3, Color.BLACK)
        b = Board([p1, p2, p3, p4])
        assert [(Column.C, 3)] == p1.get_possible_moves_position(b)

    def test_pawn_get_possible_moves_four(self):
        p1 = Pawn(Column.B, 2, Color.WHITE)
        p2 = Pawn(Column.A, 3, Color.BLACK)
        p3 = Pawn(Column.C, 3, Color.BLACK)
        b = Board([p1, p2, p3])
        moves = p1.get_possible_moves_position(b)
        assert (Column.A, 3) in moves
        assert (Column.B, 3) in moves
        assert (Column.C, 3) in moves
        assert (Column.B, 4) in moves
        assert 4 == len(moves)

    def test_pawn_get_attacking_moves(self):
        p1 = Pawn(Column.B, 2, Color.WHITE)
        p2 = Pawn(Column.A, 3, Color.BLACK)
        p3 = Pawn(Column.C, 3, Color.BLACK)
        b = Board([p1, p2, p3])
        moves = p1.get_attacking_moves_position(b)
        assert (Column.A, 3) in moves
        assert (Column.C, 3) in moves
        assert 2 == len(moves)

    def test_pawn_do_not_attack_same_color(self):
        p1 = Pawn(Column.B, 2, Color.WHITE)
        p2 = Pawn(Column.A, 3, Color.WHITE)
        p3 = Pawn(Column.C, 3, Color.WHITE)
        b = Board([p1, p2, p3])
        moves = p1.get_attacking_moves_position(b)
        assert (Column.A, 3) not in moves
        assert (Column.C, 3) not in moves

    def test_pawn_get_defended_moves(self):
        p = Pawn(Column.E, 2, Color.BLACK)
        b = Board([p])
        indices = p.get_defended_moves_index(b)
        for move in [Position(Column.D, 1), Position(Column.F, 1)]:
            assert position_to_index(move) in indices


class TestRook:
    def test_rook_surrounded_same_color(self):
        c1 = Rook(Column.B, 2, Color.BLACK)
        board = [
            c1,
            Pawn(Column.A, 2, Color.BLACK),
            Pawn(Column.C, 2, Color.BLACK),
            Pawn(Column.B, 1, Color.BLACK),
            Pawn(Column.B, 3, Color.BLACK),
        ]
        b = Board(board)
        assert not c1.get_possible_moves_position(b)

    def test_rook_up_down(self):
        c1 = Rook(Column.B, 2, Color.BLACK)
        board = [
            c1,
            Pawn(Column.A, 2, Color.BLACK),
            Pawn(Column.C, 2, Color.BLACK),
        ]
        b = Board(board)
        moves = c1.get_possible_moves_position(b)
        assert (Column.B, 1) in moves
        assert (Column.B, 3) in moves
        assert (Column.B, 4) in moves
        assert (Column.B, 5) in moves
        assert (Column.B, 6) in moves
        assert (Column.B, 7) in moves
        assert (Column.B, 8) in moves
        assert 7 == len(moves)

    def test_rook_left_right(self):
        c1 = Rook(Column.B, 2, Color.BLACK)
        board = [
            c1,
            Pawn(Column.B, 1, Color.BLACK),
            Pawn(Column.B, 3, Color.BLACK),
        ]
        b = Board(board)
        moves = c1.get_possible_moves_position(b)
        assert (Column.A, 2) in moves
        assert (Column.C, 2) in moves
        assert (Column.D, 2) in moves
        assert (Column.E, 2) in moves
        assert (Column.F, 2) in moves
        assert (Column.G, 2) in moves
        assert (Column.H, 2) in moves
        assert 7 == len(moves)

    def test_rook_surrounded_opposite_color(self):
        c1 = Rook(Column.B, 2, Color.BLACK)
        board = [
            c1,
            Pawn(Column.A, 2, Color.WHITE),
            Pawn(Column.C, 2, Color.WHITE),
            Pawn(Column.B, 1, Color.WHITE),
            Pawn(Column.B, 3, Color.WHITE),
        ]
        b = Board(board)
        moves = c1.get_possible_moves_position(b)
        assert (Column.A, 2) in moves
        assert (Column.C, 2) in moves
        assert (Column.B, 1) in moves
        assert (Column.B, 3) in moves
        assert 4 == len(moves)

    def test_rook_partially_blocked(self):
        c1 = Rook(Column.D, 4, Color.BLACK)
        board = [
            c1,
            Pawn(Column.D, 6, Color.BLACK),
            Pawn(Column.D, 2, Color.BLACK),
            Pawn(Column.B, 4, Color.BLACK),
            Pawn(Column.F, 4, Color.BLACK),
        ]
        b = Board(board)
        moves = c1.get_possible_moves_position(b)
        assert (Column.D, 3) in moves
        assert (Column.D, 5) in moves
        assert (Column.C, 4) in moves
        assert (Column.E, 4) in moves
        assert 4 == len(moves)

    def test_rook_get_defended_moves(self):
        r1 = Rook(Column.D, 6, Color.BLACK)
        pieces = [
            r1,
            Rook(Column.D, 7, Color.BLACK),
            Rook(Column.D, 5, Color.BLACK),
            Rook(Column.C, 6, Color.BLACK),
            Rook(Column.E, 6, Color.BLACK),
        ]
        b = Board(pieces)
        indices = r1.get_defended_moves_index(b)
        for move in [
            Position(Column.D, 7),
            Position(Column.D, 5),
            Position(Column.C, 6),
            Position(Column.E, 6),
        ]:
            assert position_to_index(move) in indices
        assert 4 == len(indices)


class TestBishop:
    def test_bishop_surrounded_same_color(self):
        b1 = Bishop(Column.D, 4, Color.BLACK)
        board = [
            b1,
            Pawn(Column.C, 5, Color.BLACK),
            Pawn(Column.C, 3, Color.BLACK),
            Pawn(Column.E, 5, Color.BLACK),
            Pawn(Column.E, 3, Color.BLACK),
        ]
        b = Board(board)
        assert not b1.get_possible_moves_position(b)

    def test_bishop_surrounded_diff_color(self):
        b1 = Bishop(Column.D, 4, Color.BLACK)
        board = [
            b1,
            Pawn(Column.C, 5, Color.WHITE),
            Pawn(Column.C, 3, Color.WHITE),
            Pawn(Column.E, 5, Color.WHITE),
            Pawn(Column.E, 3, Color.WHITE),
        ]
        b = Board(board)
        moves = b1.get_possible_moves_position(b)
        assert (Column.C, 5) in moves
        assert (Column.C, 3) in moves
        assert (Column.E, 3) in moves
        assert (Column.E, 5) in moves
        assert 4 == len(moves)

    def bishop_unhindered(self):
        b1 = Bishop(Column.D, 4, Color.BLACK)
        board = [
            b1,
        ]
        b = Board(board)
        moves = b1.get_possible_moves_position(b)
        assert (Column.E, 5) in moves
        assert (Column.D, 6) in moves
        assert (Column.F, 7) in moves
        assert (Column.G, 8) in moves

        assert (Column.C, 5) in moves
        assert (Column.B, 6) in moves
        assert (Column.A, 7) in moves

        assert (Column.C, 3) in moves
        assert (Column.B, 2) in moves
        assert (Column.A, 1) in moves

        assert (Column.E, 3) in moves
        assert (Column.F, 2) in moves
        assert (Column.G, 1) in moves

        assert 13 == len(moves)

    def test_bishop_get_defended_moves(self):
        r1 = Bishop(Column.D, 6, Color.BLACK)
        pieces = [
            r1,
            Bishop(Column.E, 7, Color.BLACK),
            Bishop(Column.E, 5, Color.BLACK),
            Bishop(Column.C, 7, Color.BLACK),
            Bishop(Column.C, 5, Color.BLACK),
        ]
        b = Board(pieces)
        indices = r1.get_defended_moves_index(b)
        for move in [
            Position(Column.E, 7),
            Position(Column.E, 5),
            Position(Column.C, 7),
            Position(Column.C, 5),
        ]:
            assert position_to_index(move) in indices
        assert 4 == len(indices)

    def test_bishop_defend_king(self):
        """Bishop must invoke is_check() before returning moves
        Also, if king is in check, should not be able to move bishop unless
        it blocks check
        """
        r1 = Rook(Column.D, 7, Color.WHITE)
        wk = King(Column.A, 2, Color.WHITE)
        b1 = Bishop(Column.D, 6, Color.BLACK)
        bk = King(Column.D, 5, Color.BLACK)
        black = Player(Color.BLACK, [b1, bk])
        white = Player(Color.WHITE, [r1, wk])
        pieces = [
            r1,
            b1,
            wk,
            bk,
        ]
        b = Board(pieces)
        moves = white.get_possible_moves_position(b, black)
        for src_move, _ in moves:
            assert (Column.D, 6) not in src_move

        # Assert the bishop doesn't have possible moves
        for moves in white.get_possible_moves_index(b, black):
            assert b1.index is not moves[0]

    def test_bishop_move_to_defend_king(self):
        """Bishop must invoke is_check() before returning moves
        If king is in check, should not be able to move bishop unless
        it blocks check
        """
        r1 = Rook(Column.D, 7, Color.WHITE)
        wk = King(Column.H, 2, Color.WHITE)
        b1 = Bishop(Column.E, 7, Color.BLACK)
        bk = King(Column.D, 5, Color.BLACK)
        pieces = [
            r1,
            b1,
            wk,
            bk,
        ]
        b = Board(pieces)
        print(b.prettify())
        black = Player(Color.BLACK, [b1, bk])
        white = Player(Color.WHITE, [r1, wk])
        moves = black.get_possible_moves_position(b, white)
        assert ((Column.E, 7), (Column.D, 6)) in moves
        assert ((Column.D, 5), (Column.E, 6)) in moves
        assert ((Column.D, 5), (Column.E, 5)) in moves
        assert ((Column.D, 5), (Column.E, 4)) in moves
        assert ((Column.D, 5), (Column.C, 6)) in moves
        assert ((Column.D, 5), (Column.C, 5)) in moves
        assert ((Column.D, 5), (Column.C, 4)) in moves
        assert 7 == len(moves)


class TestKnight:
    def test_knight_get_defended_moves(self):
        k1 = Knight(Column.E, 4, Color.BLACK)
        pieces = [
            k1,
            Knight(Column.D, 6, Color.BLACK),
            Knight(Column.D, 2, Color.BLACK),
            Knight(Column.F, 6, Color.BLACK),
            Knight(Column.F, 2, Color.BLACK),
            Knight(Column.C, 5, Color.BLACK),
            Knight(Column.C, 3, Color.BLACK),
            Knight(Column.G, 5, Color.BLACK),
            Knight(Column.G, 3, Color.BLACK),
        ]
        b = Board(pieces)
        indices = k1.get_defended_moves_index(b)
        for move in [
            Position(Column.D, 6),
            Position(Column.D, 2),
            Position(Column.F, 6),
            Position(Column.F, 2),
            Position(Column.C, 5),
            Position(Column.C, 3),
            Position(Column.G, 5),
            Position(Column.G, 3),
        ]:
            assert position_to_index(move) in indices
        assert 8 == len(indices)

    def test_knight_get_attacking_moves(self):
        k1 = Knight(Column.E, 4, Color.WHITE)
        pieces = [
            k1,
            Knight(Column.D, 6, Color.BLACK),
            Knight(Column.D, 2, Color.BLACK),
            Knight(Column.F, 6, Color.BLACK),
            Knight(Column.F, 2, Color.BLACK),
            Knight(Column.C, 5, Color.BLACK),
            Knight(Column.C, 3, Color.BLACK),
            Knight(Column.G, 5, Color.BLACK),
            Knight(Column.G, 3, Color.BLACK),
        ]
        b = Board(pieces)
        indices = k1.get_defended_moves_index(b)
        for move in [
            Position(Column.D, 6),
            Position(Column.D, 2),
            Position(Column.F, 6),
            Position(Column.F, 2),
            Position(Column.C, 5),
            Position(Column.C, 3),
            Position(Column.G, 5),
            Position(Column.G, 3),
        ]:
            assert position_to_index(move) in indices
        assert 8 == len(indices)

    def test_knight_get_possible_moves(self):
        k1 = Knight(Column.E, 4, Color.BLACK)
        pieces = [
            k1,
            Knight(Column.D, 6, Color.BLACK),
            Knight(Column.D, 2, Color.BLACK),
            Knight(Column.F, 6, Color.BLACK),
            Knight(Column.F, 2, Color.BLACK),
            Knight(Column.C, 5, Color.BLACK),
            Knight(Column.C, 3, Color.BLACK),
            Knight(Column.G, 5, Color.BLACK),
            Knight(Column.G, 3, Color.BLACK),
        ]
        b = Board(pieces)
        indices = k1.get_possible_moves_position(b)
        assert not indices


class TestQueen:
    def test_queen_surrounded_same_color(self):
        q1 = Queen(Column.D, 4, Color.BLACK)
        board = [
            q1,
            Pawn(Column.C, 5, Color.BLACK),
            Pawn(Column.C, 3, Color.BLACK),
            Pawn(Column.E, 5, Color.BLACK),
            Pawn(Column.E, 3, Color.BLACK),
            Pawn(Column.D, 5, Color.BLACK),
            Pawn(Column.D, 3, Color.BLACK),
            Pawn(Column.E, 4, Color.BLACK),
            Pawn(Column.C, 4, Color.BLACK),
        ]
        b = Board(board)
        assert not q1.get_possible_moves_position(b)

    def test_queen_surrounded_diff_color(self):
        q1 = Queen(Column.D, 4, Color.BLACK)
        board = [
            q1,
            Pawn(Column.C, 5, Color.WHITE),
            Pawn(Column.C, 3, Color.WHITE),
            Pawn(Column.E, 5, Color.WHITE),
            Pawn(Column.E, 3, Color.WHITE),
            Pawn(Column.D, 5, Color.WHITE),
            Pawn(Column.D, 3, Color.WHITE),
            Pawn(Column.E, 4, Color.WHITE),
            Pawn(Column.C, 4, Color.WHITE),
        ]
        b = Board(board)
        moves = q1.get_possible_moves_position(b)

        assert (Column.C, 5) in moves
        assert (Column.C, 4) in moves
        assert (Column.C, 3) in moves

        assert (Column.D, 5) in moves
        assert (Column.D, 3) in moves

        assert (Column.E, 5) in moves
        assert (Column.E, 4) in moves
        assert (Column.E, 3) in moves

        assert 8 == len(moves)

    def test_queen_get_defended_moves(self):
        q1 = Queen(Column.D, 6, Color.BLACK)
        pieces = [
            q1,
            Queen(Column.E, 7, Color.BLACK),
            Queen(Column.E, 6, Color.BLACK),
            Queen(Column.E, 5, Color.BLACK),
            Queen(Column.C, 7, Color.BLACK),
            Queen(Column.C, 6, Color.BLACK),
            Queen(Column.C, 5, Color.BLACK),
            Queen(Column.D, 7, Color.BLACK),
            Queen(Column.D, 5, Color.BLACK),
        ]
        b = Board(pieces)
        indices = q1.get_defended_moves_index(b)
        for move in [
            Position(Column.E, 7),
            Position(Column.E, 6),
            Position(Column.E, 5),
            Position(Column.C, 7),
            Position(Column.C, 6),
            Position(Column.C, 5),
            Position(Column.D, 7),
            Position(Column.D, 5),
        ]:
            assert position_to_index(move) in indices
        assert 8 == len(indices)


class TestKing:
    def test_king_surrounded_same_color(self):
        k1 = King(Column.D, 4, Color.BLACK)
        board = [
            k1,
            Pawn(Column.C, 5, Color.BLACK),
            Pawn(Column.C, 3, Color.BLACK),
            Pawn(Column.E, 5, Color.BLACK),
            Pawn(Column.E, 3, Color.BLACK),
            Pawn(Column.D, 5, Color.BLACK),
            Pawn(Column.D, 3, Color.BLACK),
            Pawn(Column.E, 4, Color.BLACK),
            Pawn(Column.C, 4, Color.BLACK),
        ]
        b = Board(board)
        white = Player(Color.WHITE, [])
        black = Player(Color.BLACK, board)
        assert not k1.get_possible_moves_position(b, black, white)

    def test_king_castle(self):
        bk = King(Column.E, 8, Color.BLACK)
        wk = King(Column.E, 1, Color.WHITE)
        white_pieces = [
            wk,
            Rook(Column.A, 1, Color.WHITE),
            Rook(Column.H, 1, Color.WHITE),
        ]
        black_pieces = [
            bk,
            Rook(Column.A, 8, Color.BLACK),
            Rook(Column.H, 8, Color.BLACK),
        ]
        board = [*white_pieces, *black_pieces]
        b = Board(board)
        white = Player(Color.WHITE, white_pieces)
        black = Player(Color.BLACK, black_pieces)

        print(black.color)
        print(wk.color)
        assert Position(Column.G, 1) in wk.get_possible_moves_position(
            b, white, black
        )
        assert Position(Column.C, 1) in wk.get_possible_moves_position(
            b, white, black
        )
        assert Position(Column.G, 8) in bk.get_possible_moves_position(
            b, black, white
        )
        assert Position(Column.C, 8) in bk.get_possible_moves_position(
            b, black, white
        )

    @pytest.mark.parametrize(
        "rank,color", [(1, Color.WHITE), (8, Color.BLACK)]
    )
    @pytest.mark.parametrize(
        "cmd_start,cmd_end,file",
        [
            ("e", "g", Column.G),
            ("e", "c", Column.C),
        ],
    )
    def test_king_castle_position(self, rank, color, cmd_start, cmd_end, file):
        other_color = Color.WHITE if color == Color.BLACK else Color.BLACK
        wk = King(Column.E, rank, color)
        white_pieces = [
            wk,
            Rook(Column.A, rank, color),
            Rook(Column.H, rank, color),
        ]
        b = Board(white_pieces)
        black = Player(other_color, [])
        white = Player(color, white_pieces)
        white.do_move(
            {
                "start": {
                    "file": cmd_start,
                    "rank": rank,
                },
                "end": {
                    "file": cmd_end,
                    "rank": rank,
                },
                "promote": None,
            },
            b,
            black,
        )
        assert Position(file, rank) == index_to_position(white.king_index)

    def test_king_no_castle(self):
        bk = King(Column.E, 8, Color.BLACK)
        wk = King(Column.E, 1, Color.WHITE)
        white_pieces = [
            wk,
            Rook(Column.A, 1, Color.WHITE),
            Rook(Column.H, 1, Color.WHITE),
            Bishop(Column.E, 7, Color.WHITE),
        ]
        black_pieces = [
            bk,
            Rook(Column.A, 8, Color.BLACK),
            Rook(Column.H, 8, Color.BLACK),
            Bishop(Column.E, 2, Color.BLACK),
        ]
        board = [*white_pieces, *black_pieces]
        b = Board(board)
        white = Player(Color.WHITE, white_pieces)
        black = Player(Color.BLACK, black_pieces)

        assert Position(Column.G, 1) not in wk.get_possible_moves_position(
            b, white, black
        )
        assert Position(Column.C, 1) not in wk.get_possible_moves_position(
            b, white, black
        )
        assert Position(Column.G, 8) not in bk.get_possible_moves_position(
            b, black, white
        )
        assert Position(Column.C, 8) not in bk.get_possible_moves_position(
            b, black, white
        )

    def test_king_surrounded_diff_color(self):
        k1 = King(Column.D, 4, Color.BLACK)
        player: List[Piece] = [
            Pawn(Column.C, 5, Color.WHITE),
            Pawn(Column.C, 3, Color.WHITE),
            Pawn(Column.E, 5, Color.WHITE),
            Pawn(Column.E, 3, Color.WHITE),
            Pawn(Column.D, 5, Color.WHITE),
            Pawn(Column.D, 3, Color.WHITE),
            Pawn(Column.E, 4, Color.WHITE),
            Pawn(Column.C, 4, Color.WHITE),
        ]
        white = Player(Color.WHITE, player)
        black = Player(Color.BLACK, [])
        player.append(k1)
        b = Board(player)

        moves = k1.get_possible_moves_position(b, black, white)
        print("king moves: {}".format(moves))

        white_defended = white.get_defended_positions(b, black)
        print("defended: {}".format(white_defended))
        print(b.prettify())
        white.print_defended_positions(b, black)
        for move in white_defended:
            assert move not in moves
        assert (Column.C, 5) in moves

        # defended by D3
        assert (Column.C, 4) not in moves
        assert (Column.C, 3) in moves

        # defended by C4 and E4
        assert (Column.D, 5) not in moves
        assert (Column.D, 3) in moves

        assert (Column.E, 5) in moves

        # defended by D3
        assert (Column.E, 4) not in moves
        assert (Column.E, 3) in moves

        assert 5 == len(moves)

    def test_king_get_defended_moves(self):
        k1 = King(Column.D, 6, Color.BLACK)
        pieces = [
            k1,
            King(Column.E, 7, Color.BLACK),
            King(Column.E, 6, Color.BLACK),
            King(Column.E, 5, Color.BLACK),
            King(Column.C, 7, Color.BLACK),
            King(Column.C, 6, Color.BLACK),
            King(Column.C, 5, Color.BLACK),
            King(Column.D, 7, Color.BLACK),
            King(Column.D, 5, Color.BLACK),
        ]
        b = Board(pieces)
        p = Player(Color.WHITE, [])
        indices = k1.get_defended_moves_index(b, p)
        for move in [
            Position(Column.E, 7),
            Position(Column.E, 6),
            Position(Column.E, 5),
            Position(Column.C, 7),
            Position(Column.C, 6),
            Position(Column.C, 5),
            Position(Column.D, 7),
            Position(Column.D, 5),
        ]:
            assert position_to_index(move) in indices
        assert 8 == len(indices)


class TestPlayer:
    def test_player_is_defending_one_pawn(self):
        board = [
            Pawn(Column.C, 5, Color.WHITE),
        ]
        b = Board(board)
        player = Player(Color.WHITE, board)
        other_player = Player(Color.BLACK, [])
        defended_positions = player.get_defended_positions(b, other_player)
        assert (Column.B, 6) in defended_positions
        assert (Column.D, 6) in defended_positions
        assert player.is_defending_position(
            b, Position(Column.B, 6), other_player
        )
        assert player.is_defending_position(
            b, Position(Column.D, 6), other_player
        )
        assert 2 == len(defended_positions)

    def test_player_is_defending_pawn_line(self):
        board = [
            Pawn(Column.A, 2, Color.WHITE),
            Pawn(Column.B, 2, Color.WHITE),
            Pawn(Column.C, 2, Color.WHITE),
            Pawn(Column.D, 2, Color.WHITE),
            Pawn(Column.E, 2, Color.WHITE),
            Pawn(Column.F, 2, Color.WHITE),
            Pawn(Column.G, 2, Color.WHITE),
        ]
        b = Board(board)
        player = Player(Color.WHITE, board)
        other_player = Player(Color.BLACK, [])
        defended_positions = player.get_defended_positions(b, other_player)
        player.print_defended_positions(b, other_player)
        assert (Column.A, 3) in defended_positions
        assert (Column.B, 3) in defended_positions
        assert (Column.C, 3) in defended_positions
        assert (Column.D, 3) in defended_positions
        assert (Column.E, 3) in defended_positions
        assert (Column.F, 3) in defended_positions
        assert (Column.G, 3) in defended_positions

        assert 8 == len(defended_positions)

    def test_chess_defended_positions_beginning(self):
        chess = Chess()
        defended_positions = chess.white.get_defended_positions(
            chess.board, chess.black
        )
        assert (Column.A, 3) in defended_positions
        assert (Column.B, 3) in defended_positions
        assert (Column.C, 3) in defended_positions
        assert (Column.D, 3) in defended_positions
        assert (Column.E, 3) in defended_positions
        assert (Column.F, 3) in defended_positions
        assert (Column.G, 3) in defended_positions

        defended_positions = chess.black.get_defended_positions(
            chess.board, chess.white
        )
        assert (Column.A, 6) in defended_positions
        assert (Column.B, 6) in defended_positions
        assert (Column.C, 6) in defended_positions
        assert (Column.D, 6) in defended_positions
        assert (Column.E, 6) in defended_positions
        assert (Column.F, 6) in defended_positions
        assert (Column.G, 6) in defended_positions

    def test_chess_possible_positions_beginning(self):
        chess = Chess()
        defended_positions = chess.white.get_possible_moves_position(
            chess.board, chess.black
        )
        pieces = [
            Piece(end.x, end.y, Color.WHITE) for _, end in defended_positions
        ]

        b = Board(pieces)
        legal_positions = [
            # Pawn Move 1
            ((Column.A, 2), (Column.A, 3)),
            ((Column.B, 2), (Column.B, 3)),
            ((Column.C, 2), (Column.C, 3)),
            ((Column.D, 2), (Column.D, 3)),
            ((Column.E, 2), (Column.E, 3)),
            ((Column.F, 2), (Column.F, 3)),
            ((Column.G, 2), (Column.G, 3)),
            ((Column.H, 2), (Column.H, 3)),
            # Pawn Move 2
            ((Column.A, 2), (Column.A, 4)),
            ((Column.B, 2), (Column.B, 4)),
            ((Column.C, 2), (Column.C, 4)),
            ((Column.D, 2), (Column.D, 4)),
            ((Column.E, 2), (Column.E, 4)),
            ((Column.F, 2), (Column.F, 4)),
            ((Column.G, 2), (Column.G, 4)),
            ((Column.H, 2), (Column.H, 4)),
            # Knight
            ((Column.B, 1), (Column.A, 3)),
            ((Column.B, 1), (Column.C, 3)),
            ((Column.G, 1), (Column.F, 3)),
            ((Column.G, 1), (Column.H, 3)),
        ]
        for position in legal_positions:
            assert position in defended_positions
        assert len(legal_positions) == len(defended_positions)

        defended_positions = chess.black.get_possible_moves_position(
            chess.board, chess.white
        )
        legal_positions = [
            # Pawn Move 1
            ((Column.A, 7), (Column.A, 6)),
            ((Column.B, 7), (Column.B, 6)),
            ((Column.C, 7), (Column.C, 6)),
            ((Column.D, 7), (Column.D, 6)),
            ((Column.E, 7), (Column.E, 6)),
            ((Column.F, 7), (Column.F, 6)),
            ((Column.G, 7), (Column.G, 6)),
            ((Column.H, 7), (Column.H, 6)),
            # Pawn Move 2
            ((Column.A, 7), (Column.A, 5)),
            ((Column.B, 7), (Column.B, 5)),
            ((Column.C, 7), (Column.C, 5)),
            ((Column.D, 7), (Column.D, 5)),
            ((Column.E, 7), (Column.E, 5)),
            ((Column.F, 7), (Column.F, 5)),
            ((Column.G, 7), (Column.G, 5)),
            ((Column.H, 7), (Column.H, 5)),
            # Knight
            ((Column.B, 8), (Column.A, 6)),
            ((Column.B, 8), (Column.C, 6)),
            ((Column.G, 8), (Column.F, 6)),
            ((Column.G, 8), (Column.H, 6)),
        ]
        for position in legal_positions:
            assert position in defended_positions
        assert len(legal_positions) == len(defended_positions)
