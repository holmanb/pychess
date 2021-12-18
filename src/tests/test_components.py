from ..components import Color, Piece, Column, Board, Pawn


class TestPieces:

    def test_piece_move_to(self):
        p = Piece(Column.A, 1, Color.BLACK)
        p.move_to_position(Column.H, 2)
        assert p.x == Column.H
        assert p.y == 1

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
        p1 = Pawn(Column.B, 2, Color.BLACK)
        b = Board([p1])
        assert [(Column.B, 3)] == p1.get_possible_moves_position(b)

    def test_pawn_get_possible_moves_blocked(self):
        p1 = Pawn(Column.B, 2, Color.BLACK)
        p2 = Pawn(Column.B, 3, Color.BLACK)
        b = Board([p1, p2])
        assert [] == p1.get_possible_moves_position(b)

    def test_pawn_get_possible_moves_blocked_attack(self):
        p1 = Pawn(Column.B, 2, Color.BLACK)
        p2 = Pawn(Column.B, 3, Color.BLACK)
        p3 = Pawn(Column.A, 3, Color.WHITE)
        b = Board([p1, p2, p3])
        assert [(Column.A, 3)] == p1.get_possible_moves_position(b)

    def test_pawn_get_possible_moves_blocked_attack_two(self):
        p1 = Pawn(Column.B, 2, Color.BLACK)
        p2 = Pawn(Column.B, 3, Color.BLACK)
        p3 = Pawn(Column.A, 3, Color.BLACK)
        p4 = Pawn(Column.C, 3, Color.WHITE)
        b = Board([p1, p2, p3, p4])
        assert [(Column.C, 3)] == p1.get_possible_moves_position(b)

    def test_pawn_get_possible_moves_three(self):
        p1 = Pawn(Column.B, 2, Color.BLACK)
        p2 = Pawn(Column.A, 3, Color.WHITE)
        p3 = Pawn(Column.C, 3, Color.WHITE)
        b = Board([p1, p2, p3])
        assert (Column.A, 3) in p1.get_possible_moves_position(b)
        assert (Column.B, 3) in p1.get_possible_moves_position(b)
        assert (Column.C, 3) in p1.get_possible_moves_position(b)
