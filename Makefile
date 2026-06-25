lint:
	ruff check .
	mypy .
	black --check .

test:
	pytest

check:
	ruff check .
	mypy .
	pytest

