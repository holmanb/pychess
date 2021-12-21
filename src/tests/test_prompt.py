import pytest

from ..prompt import parse, is_notation_valid

rank = [
    "1",
    "5",
    "8",
]

file = [
    "a",
    "e",
    "h",
]


class TestPrompt:
    def test_valid_prompt_no_dups(self):
        assert not is_notation_valid(parse("a2 a2"))

    @pytest.mark.parametrize(
            "piece",
            [
                "K",
                "P",
                "",
            ]
    )
    @pytest.mark.parametrize("capture", ["x", " ", "#" "+"])
    @pytest.mark.parametrize("rank1", rank)
    @pytest.mark.parametrize("rank2", rank)
    @pytest.mark.parametrize("file1", file)
    @pytest.mark.parametrize("file2", file)
    def test_valid_prompt(self, capture, piece, rank1, rank2, file1, file2):
        arg = f"{piece} {file1}{rank1} {file2}{rank2}"
        print(arg)
        if not (rank1 == rank2 and file1 == file2):
            assert is_notation_valid(parse(arg))
        else:
            assert not is_notation_valid(parse(arg))
