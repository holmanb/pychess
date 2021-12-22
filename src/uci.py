#!/usr/bin/env python3.10

# ref: https://github.com/nomemory/uci-protocol-specification/

from pathlib import Path
import fileinput
import os
import logging as log

ENGINE_NAME = "pychess"
THIS = Path(__file__).parent
LOG_DIR = THIS / "logs"
LOG_FILE = LOG_DIR / "uci.log"



def uci(cmd):
    log.debug(f"sending command: {cmd}")
    print(f"{cmd}\n", flush=True)

def bestmove():
    """This is where the magic will happen, for now it only sends e5 as a
    possible move, assuming black, plus an info string
    """
    uci("info depth 1 seldepth 0")
    uci("info string wow pychess is so strong no way you'll win after THAT opening")
    uci("bestmove e7e5")

def parse_command(cmd, state: dict) -> bool:
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
            pass

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
            return not state["ponder"]

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
            return True

        case ["quit"]:
            os._exit(0)

        case _:
            log.warning(f"no matching command found for \"{cmd}\"")
    return False


def main():
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
    log.info(f"| Starting {ENGINE_NAME}                         |")
    log.info("==================================================")
    log.info(f"started by parent process: [{ppid}]\n")

    for line in fileinput.input():
        if parse_command(line.strip(), state):
            bestmove()


if "__main__" == __name__:
    try:
        main()
    except KeyboardInterrupt:
        log.debug(f"received keyboard interrupt")
