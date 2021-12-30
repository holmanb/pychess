#!/usr/bin/env python3.10 -m cProfile
from uci import main

try:
    main()
except StopIteration:
    pass
except EOFError:
    pass
except KeyboardInterrupt:
    pass
