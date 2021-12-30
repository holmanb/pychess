#!/usr/bin/sh
python3.10 -m cProfile -o bench/profile.prof ./bench/bench.py << EOF
uci
isready
ucinewgame
position startpos
position startpos moves e2e4
go wtime 300000 btime 300000 movestogo 40
EOF
python3.10 -c "import pstats; pstats.Stats('bench/profile.prof').strip_dirs().sort_stats('tottime').print_stats(50)"
python3.10 -c "import pstats; pstats.Stats('bench/profile.prof').strip_dirs().sort_stats('cumtime').print_stats(50)"
