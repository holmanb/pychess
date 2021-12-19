.PHONY all:
	./game.py

.PHONY clean:
clean:
	find -name __pycache__ -type d -exec rm -rf {} +

.PHONY fmt:
fmt:
	black --line-length 79 .

.PHONY pytest:
test:
	pytest-3
