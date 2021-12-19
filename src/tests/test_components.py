from ..components import Color, Piece, Column, Board, Pawn, Castle


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
        assert (Column.A, 3) in p1.get_possible_moves_position(b)
        assert (Column.B, 3) in p1.get_possible_moves_position(b)
        assert (Column.C, 3) in p1.get_possible_moves_position(b)
        assert (Column.B, 4) in p1.get_possible_moves_position(b)
        assert 4 == len(p1.get_possible_moves_position(b))


class TestCastle:
    def test_castle_surrounded_same_color(self):
        c1 = Castle(Column.B, 2, Color.BLACK)
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
        c1 = Castle(Column.B, 2, Color.BLACK)
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
        c1 = Castle(Column.B, 2, Color.BLACK)
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
        c1 = Castle(Column.B, 2, Color.BLACK)
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
        c1 = Castle(Column.D, 4, Color.BLACK)
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
