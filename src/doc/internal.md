Overview
========

Files:
------

components.py - class definitions for the board, players, and piece types
doc/
game.py       - simple cli chess game loop composed of the components
Makefile
prompt.py     - parser for user input
tests/
uci.py        - UCI protocol implementation



Class Overview:
---------------

`Piece` subclasses (Knight, Rook, Bishop, etc):

Each piece has member variables describing color and board location, as well as
functions that return legal moves.


`Board`

Has a 2D list that stores the pieces. Pieces are mapped from their chess
grid position to an index in the list. Helper functions `position_to_index()`
and `index_to_position()` exist for converting between chess grid & 2D list
indices.


`Player`

Contains a list of indices to the pieces that player has in the board. This
list is used to iterate over pieces, for example to see if the other player's
King is in check or mated.

