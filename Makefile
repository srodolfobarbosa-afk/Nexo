.PHONY: install test run lint

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

test:
	PYTHONPATH=. pytest -q

run:
	python3 -m gunicorn src.ws_server:app --bind 0.0.0.0:8000 --workers 1

lint:
	python -m pip install ruff
	ruff check .

init:
	chmod +x init_workspace.sh && ./init_workspace.sh --install
