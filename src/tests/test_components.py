from typing import List

from pytest import raises

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
        print(b.prettify())
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
    def test_castle_surrounded_same_color(self):
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

    def test_castle_up_down(self):
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

    def test_castle_left_right(self):
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

    def test_castle_surrounded_opposite_color(self):
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

    def test_castle_partially_blocked(self):
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
        b1 = Bishop(Column.D, 6, Color.BLACK)
        k1 = King(Column.D, 5, Color.BLACK)
        pieces = [
            r1,
            b1,
            k1,
        ]
        b = Board(pieces)
        indices = r1.get_possible_moves_index(b)
        assert not indices

    def test_bishop_move_to_defend_king(self):
        """Bishop must invoke is_check() before returning moves
        If king is in check, should not be able to move bishop unless
        it blocks check
        """
        r1 = Rook(Column.D, 7, Color.WHITE)
        b1 = Bishop(Column.E, 7, Color.BLACK)
        k1 = King(Column.D, 5, Color.BLACK)
        pieces = [
            r1,
            b1,
            k1,
        ]
        b = Board(pieces)
        indices = r1.get_possible_moves_index(b)
        assert (Column.D, 6) in indices
        assert 1 == len(indices)


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
        assert Position(Column.F, 1) in wk.get_possible_moves_position(
            b, white, black
        )
        assert Position(Column.C, 1) in wk.get_possible_moves_position(
            b, white, black
        )
        assert Position(Column.F, 8) in bk.get_possible_moves_position(
            b, black, white
        )
        assert Position(Column.C, 8) in bk.get_possible_moves_position(
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
        assert (Column.A, 3) in defended_positions
        assert (Column.B, 3) in defended_positions
        assert (Column.C, 3) in defended_positions
        assert (Column.D, 3) in defended_positions
        assert (Column.E, 3) in defended_positions
        assert (Column.F, 3) in defended_positions
        assert (Column.G, 3) in defended_positions

        assert 8 == len(defended_positions)
        print(b.prettify())
        player.print_defended_positions(b, other_player)
