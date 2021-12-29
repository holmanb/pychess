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
CASTLE = DEFAULT_START + addln(
    [
        "position startpos moves e2e3 h7h5 g2g4 h5g4 "
        "g1f3 h8h2 f3h2 g4g3 f2g3 e7e6 h2f3 d8h4 g3h4",
        "isready",
        "go wtime 300000 btime 300000 movestogo 40",
    ]
)


class TestUCI:
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
        try:
            main()
        except StopIteration:
            pass

    @patch("builtins.input", side_effect=CASTLE)
    def test_main(self, _input):
        try:
            main()
        except StopIteration:
            pass
