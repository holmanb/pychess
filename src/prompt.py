#!/usr/bin/env python3.10
import pprint

def parse(in_string: str, command: dict = None):
    result = {
            'move': {
                'capture': None,
                'piece': None,
                'start': {
                    'file': None,
                    'rank': None,
                },
                'end':{
                    'file': None,
                    'rank': None,
                },
            },
            'QCastle': None,
            'KCastle': None,
    }
    if command:
        result = command
    string = in_string.replace(" ", "")

    if string:
        match [string[0], result['move']]:
            case [('+'|'#'|'x'), _] as capture:
                result['move']['capture'] = capture[0]
            case [('K'|'Q'|'N'|'B'|'R'|'P'), _] as piece:
                result['move']['piece'] = piece[0]
            case [('1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'), {'start': {'rank': None}, **_kwargs}] as rank:
                result['move']['start']['rank'] = rank[0]
            case [('1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'), {'end': {'rank': None}, **_kwargs}] as rank:
                result['move']['end']['rank'] = rank[0]
            case [('a'|'b'|'c'|'d'|'e'|'f'|'g'), {'start': {'file': None}, **_kwargs}] as file:
                result['move']['start']['file'] = file[0]
            case [('a'|'b'|'c'|'d'|'e'|'f'|'g'), {'end': {'file': None}, **_kwargs}] as file:
                result['move']['end']['file'] = file[0]
            case ['0-0-0', _]:
                result['KCastle'] = True
                return result
            case ['0-0', _]:
                result['QCastle'] = True
                return result
            case _:
                raise ValueError()
        return parse(string[1:], result)
    else:
        # Default to pawn
        piece = result['move']['piece']
        if not piece:
            result['move']['piece'] = 'P'
        return result

def is_notation_valid(command: dict) -> bool:
    """Assert that notation declares either castling,
    """
    move = command['move']
    return (
            command['QCastle'] or
            command['KCastle'] or
            (
                move['piece'] and
                move['start']['file'] and
                move['end']['file'] and
                move['start']['rank'] and
                move['end']['rank']) and

                # Same input and output
                bool(set(move['start'].values()) ^ set(move['end'].values()))
            )

def read_move():
    """Parse input for commands. Supports Long algebraic notation. Stores but
    ignores indicators, capture "x", en passant "e.p.", check "+", and
    checkmate "#"
    """
    try:
        while True:
            try:
                orig = input("> ")
                out = parse(orig)
                pprint.pprint(out)
                if not is_notation_valid(out):
                    raise ValueError()
                pprint.pprint(out)
            except ValueError:
                print(f"Invalid input: \"{orig}\"")
    except KeyboardInterrupt:
        print()

if "__main__" == __name__:
    read_move()
