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
