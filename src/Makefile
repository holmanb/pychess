.PHONY all:
	./game.py

.PHONY clean:
clean:
	find -name __pycache__ -type d -exec rm -rf {} +
	rm -rf logs
	rm -rf .pytest_cache/

.PHONY fmt:
fmt:
	black --line-length 79 .

.PHONY pytest:
test:
	python3.10 -m pytest tests
