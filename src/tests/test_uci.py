import pytest
from unittest.mock import patch
from typing import List
from ..uci import position_valid_or_raise, parse_command, main


def addln(str_list: List[str]):
    return list(map(lambda x: f"{x}\n", str_list))


DEFAULT_START = addln(
    [
        "uci",
        "isready",
        "ucinewgame",
        "position startpos",
        "position startpos moves e2e4",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

MOVE_TWO = DEFAULT_START + addln(
    [
        "position startpos moves e2e4 a7a5 b2b3",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)
CASTLE_1 = DEFAULT_START + addln(
    [
        "position startpos moves e2e3 h7h5 g2g4 h5g4 "
        "g1f3 h8h2 f3h2 g4g3 f2g3 e7e6 h2f3 d8h4 g3h4",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

CASTLE_2 = DEFAULT_START + addln(
    [
        "position startpos moves e2e4 g8f6 g1f3 f6e4 d2d3 e4f2 e1f2 "
        "c7c5 c2c4 f7f5 f3e5 b8c6 e5c6 e7e6 c6d8 f8d6 d8f7",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_1 = DEFAULT_START + addln(
    [
        "position startpos moves e2e3 h7h5 g1f3 f7f5 f3h4 "
        "g7g5 h4f5 d7d6 f1d3 c8f5 d3f5",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_2 = DEFAULT_START + addln(
    [
        "position startpos moves e2e3 e7e5 d2d4",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_3 = DEFAULT_START + addln(
    [
        "position startpos moves b2b3 d7d5 b1c3 d5d4 c1a3 d4c3 a3e7 d8d2 d1d2",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_4 = DEFAULT_START + addln(
    [
        "position startpos moves b1c3 d7d5 c3e4 d5e4 d2d3 d8d3 c1d2 h7h6 "
        "b2b4 b7b5 d2c3 d3d4 d1d2 d4e3",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_5 = DEFAULT_START + addln(
    [
        "position startpos moves e2e4 a7a6 d2d4 b7b6 c1f4 c8b7 b1c3 b7d5 c3b5 c7c6",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_6 = DEFAULT_START + addln(
    [
        "position startpos moves g2g3 g8f6 e2e4",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_7 = DEFAULT_START + addln(
    [
        "position startpos moves e2e4 d7d6 d1g4 c8g4 f1e2 g4f3 e2b5 c7c6 g1f3"
        " d8a5 b5c4 a5a2 c4a2 d6d5 e4d5 c6c5 f3e5 f7f6 e5d7 e7e6 d5e6 c5c4 "
        "a2c4 f8a3 a1a3 b7b5 c4b5 b8c6 b5c6 e8d8 c6a8 g8e7 a3a7 h7h5 a7c7 "
        "e7c8 d7b6 c8e7 c7c8 e7c8 b6c8 h5h4 c8d6 g7g6 d2d4 d8e7 c1h6 h8b8 "
        "a8d5 b8d8 b1c3 g6g5 h6g5 e7f8 g5f6 h4h3 f6d8",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_8 = DEFAULT_START + addln(
    [
        "position startpos moves e2e3 a7a5 d2d4 a8a6 d1d3 f7f5 d3e4 f5e4 g1e2 "
        "e7e5 e2f4 e5f4 f1d3 e4d3 c2d3 f4f3 g2f3 f8a3 c1d2 a3b2 b1c3 b2a1 "
        "e3e4 d7d5 c3d5 d8d5 e4d5 a1d4 d2e3 d4a7 h1g1 a7e3 f2e3 a6e6 e3e4 "
        "e6e4 f3e4 h7h6 g1g4 c8g4 h2h3 g4c8 h3h4 c8f5 e1e2 f5e4 d3e4 g8e7 "
        "e2e3 e7d5 e4d5 h6h5 e3e4 e8g8 e4e5 f8f4 e5f4 b7b6 f4f5 c7c5 d5d6 "
        "g8h8 f5e6 g7g5 d6d7 b8d7 e6d7 g5h4 d7c6 c5c4 c6b6 a5a4 b6a5 c4c3 "
        "a5a4 h4h3 a4b3 h5h4 b3c3 h3h2 a2a3 h8g8 a3a4",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_9 = DEFAULT_START + addln(
    [
        "position startpos moves e2e3 e7e6 d2d4 g8e7 e3e4 h8g8 f2f4 g7g6 f4f5 "
        "b7b5 c2c4 c7c6 b1c3 f8g7 c3d5 g7d4 c1e3 d8c7 e3d4 c6d5 c4d5 c7c1 "
        "d1c1 e7f5 g1f3 f5d4 f3d4 e6d5 e4d5 a7a5 c1e3 e8d8 e3e6 f7e6 d4c6 "
        "d7c6 d5c6 b8c6 f1c4 c6a7 a1d1",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)

RANDO_CRASH_10 = DEFAULT_START + addln(
    [
        "position startpos moves e2e3 b8a6 d2d4 g7g6 g1f3 g8h6 f3e5 h6g4 e5g4 "
        "e7e5 d4e5 d8f6 e5f6 e8d8 g4e5 d7d5 e5f7 d8d7 f7h8 f8e7 f6e7",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)


class TestUCI:
    def _main(self):
        try:
            main()
        except StopIteration:
            pass

    def test_position_valid_or_raise(self):
        with pytest.raises(ValueError):
            position_valid_or_raise("e2e4e6")
        with pytest.raises(ValueError):
            assert position_valid_or_raise("i2")
        with pytest.raises(ValueError):
            assert position_valid_or_raise("a9")
        with pytest.raises(ValueError):
            assert position_valid_or_raise("a0")
        with pytest.raises(ValueError):
            assert position_valid_or_raise("10")
        # Promote
        position_valid_or_raise("b7a8r")

        # Normal move
        position_valid_or_raise("e2e4")

    def test_parse_command(self, capsys, *_args):
        try:
            for line in DEFAULT_START:
                parse_command(line.strip(), {"ponder": None, "last": None})
        except StopIteration:
            pass
        captured = capsys.readouterr()
        assert "readyok" in captured.out

    @patch("builtins.input", side_effect=DEFAULT_START)
    def test_main(self, _input):
        self._main()

    @patch("builtins.input", side_effect=CASTLE_1)
    def test_main_castle1(self, _input):
        self._main()

    @patch("builtins.input", side_effect=CASTLE_2)
    def test_main_castle2(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_1)
    def test_main_crash_1(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_2)
    def test_main_crash_2(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_3)
    def test_main_crash_3(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_4)
    def test_main_crash_4(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_5)
    def test_main_crash_5(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_6)
    def test_main_crash_6(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_7)
    def test_main_crash_7(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_8)
    def test_main_crash_8(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_9)
    def test_main_crash_9(self, _input):
        self._main()

    @patch("builtins.input", side_effect=RANDO_CRASH_10)
    def test_main_crash_10(self, _input):
        self._main()

SACK_QUEEN = addln(
    [
        "uci",
        "isready",
        "ucinewgame",
        "position startpos",
        "position startpos moves e2e4 b8a6 d1g4 c7c6 g4g6",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)


class TestMiniMax:
    def _main(self):
        try:
            main()
        except StopIteration:
            pass

    @patch("builtins.input", side_effect=SACK_QUEEN)
    def test_mini_max_queen_sack(self, _input):
        self._main()
