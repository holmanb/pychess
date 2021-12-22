#!/usr/bin/env python3.10

# ref: https://github.com/nomemory/uci-protocol-specification/

import fileinput
import os
import logging as log
from pathlib import Path
from typing import Tuple, List

ENGINE_NAME = "pychess"
THIS = Path(__file__).parent
LOG_DIR = THIS / "logs"
LOG_FILE = LOG_DIR / "uci.log"



def uci(cmd):
    log.debug(f"sending command: {cmd}")
    print(f"{cmd}\n", flush=True)


def bestmove(position: dict):
    """This is where the magic will happen, for now it only sends e5 as a
    possible move, assuming black, plus an info string
    """
    moves = ["e7e5", "e5e4", "e4e3", "a7a5", "b7b5", "c7c5", "d7d5"]
    uci("info depth 1 seldepth 0")
    uci("info string wow pychess is so strong no way you'll win after THAT opening")
    uci("bestmove {}".format(moves[bestmove.i]))
    bestmove.i += 1


def position_valid_or_raise(pos: str):
    if 4 != len(pos):
        raise ValueError("Invalid position, expected 4 characters in string")
    for i, char in enumerate(pos):
        match char:
            case ('a'|'b'|'c'|'d'|'e'|'f'|'g'|'h'):
                # odd
                if i % 2:
                    raise ValueError(f"Invalid value, {char}, did not match "
                        "expected characters")
            case ('1'|'2'|'3'|'4'|'5'|'6'|'7'|'8'):
                # even
                if not i % 2:
                    raise ValueError(f"Invalid value, {char}, did not match "
                        "expected characters")

            case _:
                raise ValueError("Invalid value, {char} did not match expected"
                    " characters in position {i}")


def parse_command(cmd, state: dict) -> Tuple[bool, List[dict]]:
    """Parse command, return true if bestmove is required
    """
    log.debug(f"uci command: {cmd}")

    # Since every go commmand requires a bestmove response, use the existence
    # of a "go: command as a sentinal to run bestmove
    match cmd.split():
        case ["uci"]:
            uci(f"id name {ENGINE_NAME}")
            uci("uciok")

        # for synchronizing after long running commands
        case ["isready"]:
            uci("readyok")

        # default start position
        case ["position", "startpos"]:
            pass

        # default start position plus moves
        case ["position", "startpos", "moves", *moves]:
            move_list = []
            for move in moves:
                position_valid_or_raise(move)
                move_list.append({
                    'move': {
                        'start': {
                            'file': move[0],
                            'rank': move[1],
                        },
                        'end':{
                            'file': move[2],
                            'rank': move[3],
                        },
                    },
            })
            return (False, move_list)

        case ["go", *args]:
            moves = iter(args)
            state["ponderhit"] = False
            try:
                while True:
                    token = next(moves)

                    # Boolean tokens
                    if "ponder" == token or "infinite" == token:
                        state[token] = True
                    # The rest are k/v pairs
                    else:
                        state[token] = next(moves)

            except StopIteration:
                pass

            # If ponder, do not send bestmove, wait for ponderhit
            return (not state["ponder"], None)

        # custom start position
        case ["position", "fen", pos]:
            pass

        # default start position plus moves
        case ["position", "fen", pos, "moves", moves]:
            pass

        case ["ucinewgame"]:
            # todo: clear internal board, don't depend - not all guis support
            pass

        # Search for move using the last position sent by "go ponder"
        case ["ponderhit"]:
            # use
            return (True, None)

        case ["quit"]:
            os._exit(0)

        case _:
            log.warning(f"no matching command found for \"{cmd}\"")
    return (False, None)


def main():
    bestmove.i = 0
    if not LOG_DIR.is_dir():
        LOG_DIR.mkdir()
    log.basicConfig(filename=LOG_FILE, encoding='utf-8', level=log.DEBUG)
    state = {
        "position": "",
        "wtime": 0,
        "btime": 0,
        "winc": 0,
        "binc": 0,
        "movestogo": 0,
        "depth": 0,
        "nodes": 0,
        "movetime": 0,
        "ponder": False,
        "infinite": False,
    }
    ppid = os.getppid()
    log.info("==================================================")
    log.info(f"| Starting {ENGINE_NAME}                                    |")
    log.info("==================================================")
    log.info(f"started by parent process: [{ppid}]\n")
    last_position = None
    for line in fileinput.input():

        (get_move, position) = parse_command(line.strip(), state)
        if position:
            last_position = position
        if get_move:
            bestmove(last_position)
            last_position = None


if "__main__" == __name__:
    try:
        main()
    except KeyboardInterrupt:
        log.debug(f"received keyboard interrupt")
