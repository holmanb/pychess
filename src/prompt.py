#!/usr/bin/env python3.10


def parse(in_string: str, command: dict = {}) -> dict:
    """
    UCI doesn't use piece symbol in notation, but my cli prompt game does (to
    simplify implemenation by avoiding ambiguity)
    Not sure if UCI requires the GUI to verify move legality, but the two
    that I have tested (cutechess and banksia) both do, and the UCI spec
    doesn't seem to have any error handling, so I think that chess engine
    GUIs are expected to pass only legal moves, which simplifies implementation
    details, but requires a slight change in handling code. See the "strict"
    option in is_notation_valid().

    The following is the expected notation[1] for CLI use:
    <piece moves> ::= <Piece symbol><from square><Capture symbol><to square>
    <pawn moves>  ::= <from square>['-'|'x']<to square>[<promoted to>]
    <Piece symbol> ::= 'N' | 'B' | 'R' | 'Q' | 'K' | ['P']
    <Capture symbol> ::= '+'|'#'|'x'
    <from square> :: = <File><Rank>
    <File> ::= 'a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h'
    <Rank> ::= '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8'

    [1] based on https://www.chessprogramming.org/Algebraic_Chess_Notation#\
            Long_Algebraic_Notation_.28LAN.29
    """
    result = {
        "move": {
            "capture": None,
            "piece": None,
            "start": {
                "file": None,
                "rank": None,
            },
            "end": {
                "file": None,
                "rank": None,
            },
        },
        "QCastle": None,
        "KCastle": None,
    }
    if command:
        result = command
    string = in_string.replace(" ", "")

    if string:
        match [string[0], result["move"]]:
            case [("+" | "#" | "x"), _] as capture:
                result["move"]["capture"] = capture[0]
            case [("K" | "Q" | "N" | "B" | "R" | "P"), _] as piece:
                result["move"]["piece"] = piece[0]
            case [
                ("1" | "2" | "3" | "4" | "5" | "6" | "7" | "8"),
                {"start": {"rank": None}, **_kwargs},
            ] as rank:
                result["move"]["start"]["rank"] = rank[0]
            case [
                ("1" | "2" | "3" | "4" | "5" | "6" | "7" | "8"),
                {"end": {"rank": None}, **_kwargs},
            ] as rank:
                result["move"]["end"]["rank"] = rank[0]
            case [
                ("a" | "b" | "c" | "d" | "e" | "f" | "g" | "h"),
                {"start": {"file": None}, **_kwargs},
            ] as file:
                result["move"]["start"]["file"] = file[0]
            case [
                ("a" | "b" | "c" | "d" | "e" | "f" | "g" | "h"),
                {"end": {"file": None}, **_kwargs},
            ] as file:
                result["move"]["end"]["file"] = file[0]
            case ["0-0-0", _]:
                result["KCastle"] = True
                return result
            case ["0-0", _]:
                result["QCastle"] = True
                return result
            case _:
                raise ValueError()
        return parse(string[1:], result)
    else:
        # Default to pawn
        piece = result["move"]["piece"]
        if not piece:
            result["move"]["piece"] = "P"
        return result


def is_notation_valid(command: dict, strict: bool = True) -> bool:
    """Assert that notation is valid"""
    move = command["move"]
    if strict and not move["piece"]:
        return False

    return (
        command.get("QCastle")
        or command.get("KCastle")
        or (
            move["start"]["file"]
            and move["end"]["file"]
            and move["start"]["rank"]
            and move["end"]["rank"]
        )
        and
        # Same input and output
        bool(set(move["start"].values()) ^ set(move["end"].values()))
    )


def read_move() -> dict:
    """Parse input for commands. Supports Long algebraic notation. Stores but
    ignores indicators, capture "x", en passant "e.p.", check "+", and
    checkmate "#"
    """
    while True:
        try:
            orig = input("> ")
            out = parse(orig)
            if not is_notation_valid(out):
                raise ValueError()
            return out
        except ValueError:
            print(f'Invalid input: "{orig}"')


if "__main__" == __name__:
    try:
        read_move()
    except KeyboardInterrupt:
        print()
