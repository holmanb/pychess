from typing import List

import pytest
from pytest import raises

from ..game import Chess
from ..components import (
    Color,
    Piece,
    Row,
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
    index_valid_or_raise,
)

#    Position,
#    position_to_index,
#    index_to_position,


class TestHelpers:
    #    def pos_index(self):
    #        assert Index(0, 0) == position_to_index(Position(Column.A, 1))
    #        assert Index(7, 7) == position_to_index(Position(Column.H, 8))

    #    def index_pos(self):
    #        assert Position(Column.A, 1) == index_to_position(Index(0, 0))
    #        assert Position(Column.H, 8) == index_to_position(Index(7, 7))

    def bounds_check(self):
        with raises(ValueError):
            index_valid_or_raise(Index(-1, 0))
            index_valid_or_raise(Index(0, -1))
            index_valid_or_raise(Index(8, 0))
            index_valid_or_raise(Index(0, 8))


class TestPieces:
    def test_piece_move_to(self):
        p = Piece(Column.A, Row._1, Color.BLACK)
        p.move_to_index(Index(Column.H, Row._2))
        assert p.index == Index(Column.H, Row._2)

    def test_piece_get_relative_position(self):
        p1 = Piece(Column.A, Row._1, Color.BLACK)
        p2 = Piece(Column.A, Row._2, Color.WHITE)
        b = Board([p1, p2])
        assert p2 == p1.get_relative_index(b, 0, 1)
        assert p1 == p2.get_relative_index(b, 0, -1)

    def test_piece_get_relative_position_color(self):
        p1 = Piece(Column.A, Row._1, Color.BLACK)
        p2 = Piece(Column.A, Row._2, Color.WHITE)
        b = Board([p1, p2])
        assert Color.WHITE == p1.get_relative_index_color(b, 0, 1)
        assert Color.BLACK == p2.get_relative_index_color(b, 0, -1)


class TestPawn:
    def test_pawn_get_possible_moves_no_blocks(self):
        p1 = Pawn(Column.B, Row._2, Color.WHITE)
        b = Board([p1])
        assert (Column.B, Row._3) in p1.get_possible_moves_index(b)
        assert (Column.B, Row._4) in p1.get_possible_moves_index(b)

    def test_pawn_get_possible_moves_blocked(self):
        p1 = Pawn(Column.B, Row._2, Color.WHITE)
        p2 = Pawn(Column.B, Row._3, Color.WHITE)
        b = Board([p1, p2])
        assert [] == p1.get_possible_moves_index(b)

    def test_pawn_get_possible_moves_blocked_attack(self):
        p1 = Pawn(Column.B, Row._2, Color.WHITE)
        p2 = Pawn(Column.B, Row._3, Color.WHITE)
        p3 = Pawn(Column.A, Row._3, Color.BLACK)
        b = Board([p1, p2, p3])
        assert [Index(Column.A, Row._3)] == p1.get_possible_moves_index(b)

    def test_pawn_get_possible_moves_blocked_attack_two(self):
        p1 = Pawn(Column.B, Row._2, Color.WHITE)
        p2 = Pawn(Column.B, Row._3, Color.WHITE)
        p3 = Pawn(Column.A, Row._3, Color.WHITE)
        p4 = Pawn(Column.C, Row._3, Color.BLACK)
        b = Board([p1, p2, p3, p4])
        assert [(Column.C, Row._3)] == p1.get_possible_moves_index(b)

    def test_pawn_get_possible_moves_four(self):
        p1 = Pawn(Column.B, Row._2, Color.WHITE)
        p2 = Pawn(Column.A, Row._3, Color.BLACK)
        p3 = Pawn(Column.C, Row._3, Color.BLACK)
        b = Board([p1, p2, p3])
        moves = p1.get_possible_moves_index(b)
        assert (Column.A, Row._3) in moves
        assert (Column.B, Row._3) in moves
        assert (Column.C, Row._3) in moves
        assert (Column.B, Row._4) in moves
        assert 4 == len(moves)

    def test_pawn_get_attacking_moves(self):
        p1 = Pawn(Column.B, Row._2, Color.WHITE)
        p2 = Pawn(Column.A, Row._3, Color.BLACK)
        p3 = Pawn(Column.C, Row._3, Color.BLACK)
        b = Board([p1, p2, p3])
        moves = p1.get_attacking_moves_index(b)
        assert (Column.A, Row._3) in moves
        assert (Column.C, Row._3) in moves
        assert 2 == len(moves)

    def test_pawn_do_not_attack_same_color(self):
        p1 = Pawn(Column.B, Row._2, Color.WHITE)
        p2 = Pawn(Column.A, Row._3, Color.WHITE)
        p3 = Pawn(Column.C, Row._3, Color.WHITE)
        b = Board([p1, p2, p3])
        moves = p1.get_attacking_moves_index(b)
        assert (Column.A, Row._3) not in moves
        assert (Column.C, Row._3) not in moves

    def test_pawn_get_defended_moves(self):
        p = Pawn(Column.E, Row._2, Color.BLACK)
        b = Board([p])
        indices = p.get_defended_moves_index(b)
        for move in [Index(Column.D, Row._1), Index(Column.F, Row._1)]:
            assert move in indices


class TestRook:
    def test_rook_surrounded_same_color(self):
        c1 = Rook(Column.B, Row._2, Color.BLACK)
        board = [
            c1,
            Pawn(Column.A, Row._2, Color.BLACK),
            Pawn(Column.C, Row._2, Color.BLACK),
            Pawn(Column.B, Row._1, Color.BLACK),
            Pawn(Column.B, Row._3, Color.BLACK),
        ]
        b = Board(board)
        assert not c1.get_possible_moves_index(b)

    def test_rook_up_down(self):
        c1 = Rook(Column.B, Row._2, Color.BLACK)
        board = [
            c1,
            Pawn(Column.A, Row._2, Color.BLACK),
            Pawn(Column.C, Row._2, Color.BLACK),
        ]
        b = Board(board)
        moves = c1.get_possible_moves_index(b)
        assert (Column.B, Row._1) in moves
        assert (Column.B, Row._3) in moves
        assert (Column.B, Row._4) in moves
        assert (Column.B, Row._5) in moves
        assert (Column.B, Row._6) in moves
        assert (Column.B, Row._7) in moves
        assert (Column.B, Row._8) in moves
        assert 7 == len(moves)

    def test_rook_left_right(self):
        c1 = Rook(Column.B, Row._2, Color.BLACK)
        board = [
            c1,
            Pawn(Column.B, Row._1, Color.BLACK),
            Pawn(Column.B, Row._3, Color.BLACK),
        ]
        b = Board(board)
        moves = c1.get_possible_moves_index(b)
        assert (Column.A, Row._2) in moves
        assert (Column.C, Row._2) in moves
        assert (Column.D, Row._2) in moves
        assert (Column.E, Row._2) in moves
        assert (Column.F, Row._2) in moves
        assert (Column.G, Row._2) in moves
        assert (Column.H, Row._2) in moves
        assert 7 == len(moves)

    def test_rook_surrounded_opposite_color(self):
        c1 = Rook(Column.B, Row._2, Color.BLACK)
        board = [
            c1,
            Pawn(Column.A, Row._2, Color.WHITE),
            Pawn(Column.C, Row._2, Color.WHITE),
            Pawn(Column.B, Row._1, Color.WHITE),
            Pawn(Column.B, Row._3, Color.WHITE),
        ]
        b = Board(board)
        moves = c1.get_possible_moves_index(b)
        assert (Column.A, Row._2) in moves
        assert (Column.C, Row._2) in moves
        assert (Column.B, Row._1) in moves
        assert (Column.B, Row._3) in moves
        assert 4 == len(moves)

    def test_rook_partially_blocked(self):
        c1 = Rook(Column.D, Row._4, Color.BLACK)
        board = [
            c1,
            Pawn(Column.D, Row._6, Color.BLACK),
            Pawn(Column.D, Row._2, Color.BLACK),
            Pawn(Column.B, Row._4, Color.BLACK),
            Pawn(Column.F, Row._4, Color.BLACK),
        ]
        b = Board(board)
        moves = c1.get_possible_moves_index(b)
        assert (Column.D, Row._3) in moves
        assert (Column.D, Row._5) in moves
        assert (Column.C, Row._4) in moves
        assert (Column.E, Row._4) in moves
        assert 4 == len(moves)

    def test_rook_get_defended_moves(self):
        r1 = Rook(Column.D, Row._6, Color.BLACK)
        pieces = [
            r1,
            Rook(Column.D, Row._7, Color.BLACK),
            Rook(Column.D, Row._5, Color.BLACK),
            Rook(Column.C, Row._6, Color.BLACK),
            Rook(Column.E, Row._6, Color.BLACK),
        ]
        b = Board(pieces)
        indices = r1.get_defended_moves_index(b)
        for move in [
            Index(Column.D, Row._7),
            Index(Column.D, Row._5),
            Index(Column.C, Row._6),
            Index(Column.E, Row._6),
        ]:
            assert move in indices
        assert 4 == len(indices)


class TestBishop:
    def test_bishop_surrounded_same_color(self):
        b1 = Bishop(Column.D, Row._4, Color.BLACK)
        board = [
            b1,
            Pawn(Column.C, Row._5, Color.BLACK),
            Pawn(Column.C, Row._3, Color.BLACK),
            Pawn(Column.E, Row._5, Color.BLACK),
            Pawn(Column.E, Row._3, Color.BLACK),
        ]
        b = Board(board)
        assert not b1.get_possible_moves_index(b)

    def test_bishop_surrounded_diff_color(self):
        b1 = Bishop(Column.D, Row._4, Color.BLACK)
        board = [
            b1,
            Pawn(Column.C, Row._5, Color.WHITE),
            Pawn(Column.C, Row._3, Color.WHITE),
            Pawn(Column.E, Row._5, Color.WHITE),
            Pawn(Column.E, Row._3, Color.WHITE),
        ]
        b = Board(board)
        moves = b1.get_possible_moves_index(b)
        assert (Column.C, Row._5) in moves
        assert (Column.C, Row._3) in moves
        assert (Column.E, Row._3) in moves
        assert (Column.E, Row._5) in moves
        assert 4 == len(moves)

    def bishop_unhindered(self):
        b1 = Bishop(Column.D, Row._4, Color.BLACK)
        board = [
            b1,
        ]
        b = Board(board)
        moves = b1.get_possible_moves_index(b)
        assert (Column.E, Row._5) in moves
        assert (Column.D, Row._6) in moves
        assert (Column.F, Row._7) in moves
        assert (Column.G, Row._8) in moves

        assert (Column.C, Row._5) in moves
        assert (Column.B, Row._6) in moves
        assert (Column.A, Row._7) in moves

        assert (Column.C, Row._3) in moves
        assert (Column.B, Row._2) in moves
        assert (Column.A, Row._1) in moves

        assert (Column.E, Row._3) in moves
        assert (Column.F, Row._2) in moves
        assert (Column.G, Row._1) in moves

        assert 13 == len(moves)

    def test_bishop_get_defended_moves(self):
        r1 = Bishop(Column.D, Row._6, Color.BLACK)
        pieces = [
            r1,
            Bishop(Column.E, Row._7, Color.BLACK),
            Bishop(Column.E, Row._5, Color.BLACK),
            Bishop(Column.C, Row._7, Color.BLACK),
            Bishop(Column.C, Row._5, Color.BLACK),
        ]
        b = Board(pieces)
        indices = r1.get_defended_moves_index(b)
        for move in [
            Index(Column.E, Row._7),
            Index(Column.E, Row._5),
            Index(Column.C, Row._7),
            Index(Column.C, Row._5),
        ]:
            assert move in indices
        assert 4 == len(indices)

    def test_bishop_defend_king(self):
        """Bishop must invoke is_check() before returning moves
        Also, if king is in check, should not be able to move bishop unless
        it blocks check
        """
        r1 = Rook(Column.D, Row._7, Color.WHITE)
        wk = King(Column.A, Row._2, Color.WHITE)
        b1 = Bishop(Column.D, Row._6, Color.BLACK)
        bk = King(Column.D, Row._5, Color.BLACK)
        black = Player(Color.BLACK, [b1, bk])
        white = Player(Color.WHITE, [r1, wk])
        pieces = [
            r1,
            b1,
            wk,
            bk,
        ]
        b = Board(pieces)
        moves = white.get_possible_moves_index(b, black)
        for src_move, _ in moves:
            assert Index(Column.D, Row._6) not in src_move

        # Assert the bishop doesn't have possible moves
        for moves in white.get_possible_moves_index(b, black):
            assert b1.index is not moves[0]

    def test_bishop_move_to_defend_king(self):
        """Bishop must invoke is_check() before returning moves
        If king is in check, should not be able to move bishop unless
        it blocks check
        """
        r1 = Rook(Column.D, Row._7, Color.WHITE)
        wk = King(Column.H, Row._2, Color.WHITE)
        b1 = Bishop(Column.E, Row._7, Color.BLACK)
        bk = King(Column.D, Row._5, Color.BLACK)
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
        moves = black.get_possible_moves_index(b, white)
        assert (Index(Column.E, Row._7), Index(Column.D, Row._6)) in moves
        assert (Index(Column.D, Row._5), Index(Column.E, Row._6)) in moves
        assert (Index(Column.D, Row._5), Index(Column.E, Row._5)) in moves
        assert (Index(Column.D, Row._5), Index(Column.E, Row._4)) in moves
        assert (Index(Column.D, Row._5), Index(Column.C, Row._6)) in moves
        assert (Index(Column.D, Row._5), Index(Column.C, Row._5)) in moves
        assert (Index(Column.D, Row._5), Index(Column.C, Row._4)) in moves
        assert 7 == len(moves)


class TestKnight:
    def test_knight_get_defended_moves(self):
        k1 = Knight(Column.E, Row._4, Color.BLACK)
        pieces = [
            k1,
            Knight(Column.D, Row._6, Color.BLACK),
            Knight(Column.D, Row._2, Color.BLACK),
            Knight(Column.F, Row._6, Color.BLACK),
            Knight(Column.F, Row._2, Color.BLACK),
            Knight(Column.C, Row._5, Color.BLACK),
            Knight(Column.C, Row._3, Color.BLACK),
            Knight(Column.G, Row._5, Color.BLACK),
            Knight(Column.G, Row._3, Color.BLACK),
        ]
        b = Board(pieces)
        indices = k1.get_defended_moves_index(b)
        for move in [
            Index(Column.D, Row._6),
            Index(Column.D, Row._2),
            Index(Column.F, Row._6),
            Index(Column.F, Row._2),
            Index(Column.C, Row._5),
            Index(Column.C, Row._3),
            Index(Column.G, Row._5),
            Index(Column.G, Row._3),
        ]:
            assert move in indices
        assert 8 == len(indices)

    def test_knight_get_attacking_moves(self):
        k1 = Knight(Column.E, Row._4, Color.WHITE)
        pieces = [
            k1,
            Knight(Column.D, Row._6, Color.BLACK),
            Knight(Column.D, Row._2, Color.BLACK),
            Knight(Column.F, Row._6, Color.BLACK),
            Knight(Column.F, Row._2, Color.BLACK),
            Knight(Column.C, Row._5, Color.BLACK),
            Knight(Column.C, Row._3, Color.BLACK),
            Knight(Column.G, Row._5, Color.BLACK),
            Knight(Column.G, Row._3, Color.BLACK),
        ]
        b = Board(pieces)
        indices = k1.get_defended_moves_index(b)
        for move in [
            Index(Column.D, Row._6),
            Index(Column.D, Row._2),
            Index(Column.F, Row._6),
            Index(Column.F, Row._2),
            Index(Column.C, Row._5),
            Index(Column.C, Row._3),
            Index(Column.G, Row._5),
            Index(Column.G, Row._3),
        ]:
            assert move in indices
        assert 8 == len(indices)

    def test_knight_get_possible_moves(self):
        k1 = Knight(Column.E, Row._4, Color.BLACK)
        pieces = [
            k1,
            Knight(Column.D, Row._6, Color.BLACK),
            Knight(Column.D, Row._2, Color.BLACK),
            Knight(Column.F, Row._6, Color.BLACK),
            Knight(Column.F, Row._2, Color.BLACK),
            Knight(Column.C, Row._5, Color.BLACK),
            Knight(Column.C, Row._3, Color.BLACK),
            Knight(Column.G, Row._5, Color.BLACK),
            Knight(Column.G, Row._3, Color.BLACK),
        ]
        b = Board(pieces)
        indices = k1.get_possible_moves_index(b)
        assert not indices


class TestQueen:
    def test_queen_surrounded_same_color(self):
        q1 = Queen(Column.D, Row._4, Color.BLACK)
        board = [
            q1,
            Pawn(Column.C, Row._5, Color.BLACK),
            Pawn(Column.C, Row._3, Color.BLACK),
            Pawn(Column.E, Row._5, Color.BLACK),
            Pawn(Column.E, Row._3, Color.BLACK),
            Pawn(Column.D, Row._5, Color.BLACK),
            Pawn(Column.D, Row._3, Color.BLACK),
            Pawn(Column.E, Row._4, Color.BLACK),
            Pawn(Column.C, Row._4, Color.BLACK),
        ]
        b = Board(board)
        assert not q1.get_possible_moves_index(b)

    def test_queen_surrounded_diff_color(self):
        q1 = Queen(Column.D, Row._4, Color.BLACK)
        board = [
            q1,
            Pawn(Column.C, Row._5, Color.WHITE),
            Pawn(Column.C, Row._3, Color.WHITE),
            Pawn(Column.E, Row._5, Color.WHITE),
            Pawn(Column.E, Row._3, Color.WHITE),
            Pawn(Column.D, Row._5, Color.WHITE),
            Pawn(Column.D, Row._3, Color.WHITE),
            Pawn(Column.E, Row._4, Color.WHITE),
            Pawn(Column.C, Row._4, Color.WHITE),
        ]
        b = Board(board)
        moves = q1.get_possible_moves_index(b)

        assert (Column.C, Row._5) in moves
        assert (Column.C, Row._4) in moves
        assert (Column.C, Row._3) in moves

        assert (Column.D, Row._5) in moves
        assert (Column.D, Row._3) in moves

        assert (Column.E, Row._5) in moves
        assert (Column.E, Row._4) in moves
        assert (Column.E, Row._3) in moves

        assert 8 == len(moves)

    def test_queen_get_defended_moves(self):
        q1 = Queen(Column.D, Row._6, Color.BLACK)
        pieces = [
            q1,
            Queen(Column.E, Row._7, Color.BLACK),
            Queen(Column.E, Row._6, Color.BLACK),
            Queen(Column.E, Row._5, Color.BLACK),
            Queen(Column.C, Row._7, Color.BLACK),
            Queen(Column.C, Row._6, Color.BLACK),
            Queen(Column.C, Row._5, Color.BLACK),
            Queen(Column.D, Row._7, Color.BLACK),
            Queen(Column.D, Row._5, Color.BLACK),
        ]
        b = Board(pieces)
        indices = q1.get_defended_moves_index(b)
        for move in [
            Index(Column.E, Row._7),
            Index(Column.E, Row._6),
            Index(Column.E, Row._5),
            Index(Column.C, Row._7),
            Index(Column.C, Row._6),
            Index(Column.C, Row._5),
            Index(Column.D, Row._7),
            Index(Column.D, Row._5),
        ]:
            assert move in indices
        assert 8 == len(indices)


class TestKing:
    def test_king_surrounded_same_color(self):
        k1 = King(Column.D, Row._4, Color.BLACK)
        board = [
            k1,
            Pawn(Column.C, Row._5, Color.BLACK),
            Pawn(Column.C, Row._3, Color.BLACK),
            Pawn(Column.E, Row._5, Color.BLACK),
            Pawn(Column.E, Row._3, Color.BLACK),
            Pawn(Column.D, Row._5, Color.BLACK),
            Pawn(Column.D, Row._3, Color.BLACK),
            Pawn(Column.E, Row._4, Color.BLACK),
            Pawn(Column.C, Row._4, Color.BLACK),
        ]
        b = Board(board)
        white = Player(Color.WHITE, [])
        black = Player(Color.BLACK, board)
        assert not k1.get_possible_moves_index(b, black, white)

    def test_king_castle(self):
        bk = King(Column.E, Row._8, Color.BLACK)
        wk = King(Column.E, Row._1, Color.WHITE)
        white_pieces = [
            wk,
            Rook(Column.A, Row._1, Color.WHITE),
            Rook(Column.H, Row._1, Color.WHITE),
        ]
        black_pieces = [
            bk,
            Rook(Column.A, Row._8, Color.BLACK),
            Rook(Column.H, Row._8, Color.BLACK),
        ]
        board = [*white_pieces, *black_pieces]
        b = Board(board)
        white = Player(Color.WHITE, white_pieces)
        black = Player(Color.BLACK, black_pieces)

        print(black.color)
        print(wk.color)
        assert Index(Column.G, Row._1) in wk.get_possible_moves_index(
            b, white, black
        )
        assert Index(Column.C, Row._1) in wk.get_possible_moves_index(
            b, white, black
        )
        assert Index(Column.G, Row._8) in bk.get_possible_moves_index(
            b, black, white
        )
        assert Index(Column.C, Row._8) in bk.get_possible_moves_index(
            b, black, white
        )

    @pytest.mark.parametrize(
        "rank,color,cmd_rank",
        [(Row._1, Color.WHITE, "1"), (Row._8, Color.BLACK, "8")],
    )
    @pytest.mark.parametrize(
        "cmd_start,cmd_end,file",
        [
            ("e", "g", Column.G),
            ("e", "c", Column.C),
        ],
    )
    def test_king_castle_position(
        self, rank, color, cmd_start, cmd_end, file, cmd_rank
    ):
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
                    "rank": cmd_rank,
                },
                "end": {
                    "file": cmd_end,
                    "rank": cmd_rank,
                },
                "promote": None,
            },
            b,
            black,
        )
        assert Index(file, rank) == white.king_index

    def test_king_no_castle(self):
        bk = King(Column.E, Row._8, Color.BLACK)
        wk = King(Column.E, Row._1, Color.WHITE)
        white_pieces = [
            wk,
            Rook(Column.A, Row._1, Color.WHITE),
            Rook(Column.H, Row._1, Color.WHITE),
            Bishop(Column.E, Row._7, Color.WHITE),
        ]
        black_pieces = [
            bk,
            Rook(Column.A, Row._8, Color.BLACK),
            Rook(Column.H, Row._8, Color.BLACK),
            Bishop(Column.E, Row._2, Color.BLACK),
        ]
        board = [*white_pieces, *black_pieces]
        b = Board(board)
        white = Player(Color.WHITE, white_pieces)
        black = Player(Color.BLACK, black_pieces)

        assert Index(Column.G, Row._1) not in wk.get_possible_moves_index(
            b, white, black
        )
        assert Index(Column.C, Row._1) not in wk.get_possible_moves_index(
            b, white, black
        )
        assert Index(Column.G, Row._8) not in bk.get_possible_moves_index(
            b, black, white
        )
        assert Index(Column.C, Row._8) not in bk.get_possible_moves_index(
            b, black, white
        )

    def test_king_surrounded_diff_color(self):
        k1 = King(Column.D, Row._4, Color.BLACK)
        player: List[Piece] = [
            Pawn(Column.C, Row._5, Color.WHITE),
            Pawn(Column.C, Row._3, Color.WHITE),
            Pawn(Column.E, Row._5, Color.WHITE),
            Pawn(Column.E, Row._3, Color.WHITE),
            Pawn(Column.D, Row._5, Color.WHITE),
            Pawn(Column.D, Row._3, Color.WHITE),
            Pawn(Column.E, Row._4, Color.WHITE),
            Pawn(Column.C, Row._4, Color.WHITE),
        ]
        white = Player(Color.WHITE, player)
        black = Player(Color.BLACK, [])
        player.append(k1)
        b = Board(player)

        moves = k1.get_possible_moves_index(b, black, white)
        print("king moves: {}".format(moves))

        white_defended = white.get_defended_indices(b, black)
        print("defended: {}".format(white_defended))
        print(b.prettify())
        white.print_defended_indices(b, black)
        for move in white_defended:
            assert move not in moves
        assert (Column.C, Row._5) in moves

        # defended by D3
        assert (Column.C, Row._4) not in moves
        assert (Column.C, Row._3) in moves

        # defended by C4 and E4
        assert (Column.D, Row._5) not in moves
        assert (Column.D, Row._3) in moves

        assert (Column.E, Row._5) in moves

        # defended by D3
        assert (Column.E, Row._4) not in moves
        assert (Column.E, Row._3) in moves

        assert 5 == len(moves)

    def test_king_get_defended_moves(self):
        k1 = King(Column.D, Row._6, Color.BLACK)
        pieces = [
            k1,
            King(Column.E, Row._7, Color.BLACK),
            King(Column.E, Row._6, Color.BLACK),
            King(Column.E, Row._5, Color.BLACK),
            King(Column.C, Row._7, Color.BLACK),
            King(Column.C, Row._6, Color.BLACK),
            King(Column.C, Row._5, Color.BLACK),
            King(Column.D, Row._7, Color.BLACK),
            King(Column.D, Row._5, Color.BLACK),
        ]
        b = Board(pieces)
        p = Player(Color.WHITE, [])
        indices = k1.get_defended_moves_index(b, p)
        for move in [
            Index(Column.E, Row._7),
            Index(Column.E, Row._6),
            Index(Column.E, Row._5),
            Index(Column.C, Row._7),
            Index(Column.C, Row._6),
            Index(Column.C, Row._5),
            Index(Column.D, Row._7),
            Index(Column.D, Row._5),
        ]:
            assert move in indices
        assert 8 == len(indices)


class TestPlayer:
    def test_player_is_defending_one_pawn(self):
        board = [
            Pawn(Column.C, Row._5, Color.WHITE),
        ]
        b = Board(board)
        player = Player(Color.WHITE, board)
        other_player = Player(Color.BLACK, [])
        defended_positions = player.get_defended_indices(b, other_player)
        assert (Column.B, Row._6) in defended_positions
        assert (Column.D, Row._6) in defended_positions
        assert player.is_defending_index(
            b, Index(Column.B, Row._6), other_player
        )
        assert player.is_defending_index(
            b, Index(Column.D, Row._6), other_player
        )
        assert 2 == len(defended_positions)

    def test_player_is_defending_pawn_line(self):
        board = [
            Pawn(Column.A, Row._2, Color.WHITE),
            Pawn(Column.B, Row._2, Color.WHITE),
            Pawn(Column.C, Row._2, Color.WHITE),
            Pawn(Column.D, Row._2, Color.WHITE),
            Pawn(Column.E, Row._2, Color.WHITE),
            Pawn(Column.F, Row._2, Color.WHITE),
            Pawn(Column.G, Row._2, Color.WHITE),
        ]
        b = Board(board)
        player = Player(Color.WHITE, board)
        other_player = Player(Color.BLACK, [])
        defended_positions = player.get_defended_indices(b, other_player)
        player.print_defended_indices(b, other_player)
        assert (Column.A, Row._3) in defended_positions
        assert (Column.B, Row._3) in defended_positions
        assert (Column.C, Row._3) in defended_positions
        assert (Column.D, Row._3) in defended_positions
        assert (Column.E, Row._3) in defended_positions
        assert (Column.F, Row._3) in defended_positions
        assert (Column.G, Row._3) in defended_positions

        assert 8 == len(defended_positions)

    def test_chess_defended_positions_beginning(self):
        chess = Chess()
        defended_positions = chess.white.get_defended_indices(
            chess.board, chess.black
        )
        assert (Column.A, Row._3) in defended_positions
        assert (Column.B, Row._3) in defended_positions
        assert (Column.C, Row._3) in defended_positions
        assert (Column.D, Row._3) in defended_positions
        assert (Column.E, Row._3) in defended_positions
        assert (Column.F, Row._3) in defended_positions
        assert (Column.G, Row._3) in defended_positions

        defended_positions = chess.black.get_defended_indices(
            chess.board, chess.white
        )
        assert (Column.A, Row._6) in defended_positions
        assert (Column.B, Row._6) in defended_positions
        assert (Column.C, Row._6) in defended_positions
        assert (Column.D, Row._6) in defended_positions
        assert (Column.E, Row._6) in defended_positions
        assert (Column.F, Row._6) in defended_positions
        assert (Column.G, Row._6) in defended_positions

    def test_chess_possible_positions_beginning(self):
        chess = Chess()
        defended_positions = chess.white.get_possible_moves_index(
            chess.board, chess.black
        )

        legal_positions = [
            # Pawn Move 1
            (Index(Column.A, Row._2), (Index(Column.A, Row._3))),
            (Index(Column.B, Row._2), (Index(Column.B, Row._3))),
            (Index(Column.C, Row._2), (Index(Column.C, Row._3))),
            (Index(Column.D, Row._2), (Index(Column.D, Row._3))),
            (Index(Column.E, Row._2), (Index(Column.E, Row._3))),
            (Index(Column.F, Row._2), (Index(Column.F, Row._3))),
            (Index(Column.G, Row._2), (Index(Column.G, Row._3))),
            (Index(Column.H, Row._2), (Index(Column.H, Row._3))),
            # Pawn Move 2
            (Index(Column.A, Row._2), Index(Column.A, Row._4)),
            (Index(Column.B, Row._2), Index(Column.B, Row._4)),
            (Index(Column.C, Row._2), Index(Column.C, Row._4)),
            (Index(Column.D, Row._2), Index(Column.D, Row._4)),
            (Index(Column.E, Row._2), Index(Column.E, Row._4)),
            (Index(Column.F, Row._2), Index(Column.F, Row._4)),
            (Index(Column.G, Row._2), Index(Column.G, Row._4)),
            (Index(Column.H, Row._2), Index(Column.H, Row._4)),
            # Knight
            (Index(Column.B, Row._1), Index(Column.A, Row._3)),
            (Index(Column.B, Row._1), Index(Column.C, Row._3)),
            (Index(Column.G, Row._1), Index(Column.F, Row._3)),
            (Index(Column.G, Row._1), Index(Column.H, Row._3)),
        ]
        for position in legal_positions:
            assert position in defended_positions
        assert len(legal_positions) == len(defended_positions)

        defended_positions = chess.black.get_possible_moves_index(
            chess.board, chess.white
        )
        legal_positions = [
            # Pawn Move 1
            (Index(Column.A, Row._7), Index(Column.A, Row._6)),
            (Index(Column.B, Row._7), Index(Column.B, Row._6)),
            (Index(Column.C, Row._7), Index(Column.C, Row._6)),
            (Index(Column.D, Row._7), Index(Column.D, Row._6)),
            (Index(Column.E, Row._7), Index(Column.E, Row._6)),
            (Index(Column.F, Row._7), Index(Column.F, Row._6)),
            (Index(Column.G, Row._7), Index(Column.G, Row._6)),
            (Index(Column.H, Row._7), Index(Column.H, Row._6)),
            # Pawn Move 2
            (Index(Column.A, Row._7), Index(Column.A, Row._5)),
            (Index(Column.B, Row._7), Index(Column.B, Row._5)),
            (Index(Column.C, Row._7), Index(Column.C, Row._5)),
            (Index(Column.D, Row._7), Index(Column.D, Row._5)),
            (Index(Column.E, Row._7), Index(Column.E, Row._5)),
            (Index(Column.F, Row._7), Index(Column.F, Row._5)),
            (Index(Column.G, Row._7), Index(Column.G, Row._5)),
            (Index(Column.H, Row._7), Index(Column.H, Row._5)),
            # Knight
            (Index(Column.B, Row._8), Index(Column.A, Row._6)),
            (Index(Column.B, Row._8), Index(Column.C, Row._6)),
            (Index(Column.G, Row._8), Index(Column.F, Row._6)),
            (Index(Column.G, Row._8), Index(Column.H, Row._6)),
        ]
        for position in legal_positions:
            assert position in defended_positions
        assert len(legal_positions) == len(defended_positions)
