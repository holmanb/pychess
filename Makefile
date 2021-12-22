all:
	+make -C src $(MAKECMDGOALS)

$(MAKECMDGOALS):
	+make -C src $(MAKECMDGOALS)
