#!/usr/bin/env python3.10

# ref: https://github.com/nomemory/uci-protocol-specification/

import fileinput
import traceback
import os
import logging as log
from pathlib import Path
from typing import Tuple, List, Union

from game import Chess

ENGINE_NAME = "pychess"
THIS = Path(__file__).parent
LOG_DIR = THIS / "logs"
LOG_FILE = LOG_DIR / "uci.log"

# the GUI I'm using sends "isready" after an invalid move. Detect.
GAME_STARTED = False


def uci(cmd):
    log.debug(f"sending command: {cmd}")
    print(f"{cmd}\n", flush=True)


def bestmove(position: str):
    """This is where the magic will happen, for now it only sends e5 as a
    possible move, assuming black, plus an info string
    """
    uci(f"bestmove {position}")
    # moves = ["e7e5", "e5e4", "e4e3", "a7a5", "b7b5", "c7c5", "d7d5"]
    # uci("info string wow pychess is so strong no way you'll win after THAT opening")
    # uci("bestmove {}".format(moves[bestmove.i]))
    # bestmove.i += 1


def position_valid_or_raise(pos: str):

    # Promote
    if 5 == len(pos):
        move = pos[:4]
        promote = pos[4]
        if promote not in ["q", "r", "b", "n"]:
            raise ValueError(f"Invalid promote {promote}")
    else:
        move = pos

    if 4 != len(move):
        raise ValueError(
            "Invalid position: "
            f'expected 4 characters in move string, received "{move}"'
        )
    for i, char in enumerate(move):
        match char:
            case ("a" | "b" | "c" | "d" | "e" | "f" | "g" | "h"):
                # odd
                if i % 2:
                    raise ValueError(
                        f"Invalid value, {char}, did not match "
                        "expected characters"
                    )
            case ("1" | "2" | "3" | "4" | "5" | "6" | "7" | "8"):
                # even
                if not i % 2:
                    raise ValueError(
                        f"Invalid value, {char}, did not match "
                        "expected characters"
                    )

            case _:
                raise ValueError(
                    "Invalid value, {char} did not match expected"
                    " characters in position {i}"
                )


def parse_command(cmd, state: dict) -> Tuple[bool, Union[List[dict], bool]]:
    """Parse command, return true if bestmove is required"""
    log.debug(f"uci command: {cmd}")

    # Since every go commmand requires a bestmove response, use the existence
    # of a "go: command as a sentinal to run bestmove
    match cmd.split():
        case ["uci"]:
            state["last"] = "uci"
            uci(f"id name {ENGINE_NAME}")
            uci("uciok")

        # for synchronizing after long running commands
        case ["isready"]:
            if "go" == state["last"]:
                log.warning("Checkmate or invalid move")
            uci("readyok")

        # default start position
        case ["position", "startpos"]:
            state["last"] = "position"
            pass

        # default start position plus moves
        case ["position", "startpos", "moves", *moves]:
            move_list = []
            for move in moves:
                promote = move[4] if 5 == len(move) else None
                position_valid_or_raise(move)
                move_list.append(
                    {
                        "move": {
                            "start": {
                                "file": move[0],
                                "rank": move[1],
                            },
                            "end": {
                                "file": move[2],
                                "rank": move[3],
                            },
                            "promote": promote,
                        },
                    }
                )
            return (False, move_list)

        case ["go", *args]:
            state["last"] = "go"
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
            return (not state["ponder"], False)

        # custom start position
        case ["position", "fen", pos]:
            raise NotImplemented()

        case ["ucinewgame"]:
            parse_command.started = False

        # Search for move using the last position sent by "go ponder"
        case ["ponderhit"]:
            state["last"] = "ponderhit"
            return (True, False)

        case ["quit"]:
            os._exit(0)

        case _:
            log.warning(f'no matching command found for "{cmd}"')
    return (False, False)


def main():
    bestmove.i = 0
    if not LOG_DIR.is_dir():
        LOG_DIR.mkdir()
    log.basicConfig(filename=LOG_FILE, encoding="utf-8", level=log.DEBUG)
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
        "last": None,
    }
    ppid = os.getppid()
    log.info("==================================================")
    log.info(f"| Starting {ENGINE_NAME}                                 |")
    log.info("==================================================")
    log.info(f"started by parent process: [{ppid}]\n")
    last_position = None
    while True:
        line = input()

        (get_move, position) = parse_command(line.strip(), state)
        if position:
            last_position = position
        if get_move:
            if not isinstance(last_position, list):
                raise TypeError(f"{last_position}")
            bestmove(Chess().get_best_move(last_position))
            last_position = None


if "__main__" == __name__:
    try:
        main()
    except KeyboardInterrupt:
        log.debug(f"received keyboard interrupt")
    except Exception as e:
        print(traceback.format_exc())
        log.error(e, exc_info=True)
        raise e
