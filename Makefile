VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

.PHONY: all install run_keylogger run_app lint clean

all: install run_keylogger run_app

install:
	@echo "Setting up virtual environment and installing dependencies..."
	python3 -m venv $(VENV_DIR)
	$(PIP) install -r requirements.txt
	@echo "Installation complete."

run_keylogger:
	@echo "Starting Keylogger Max... (Press Ctrl+C to stop)"
	$(PYTHON) keyloggermax.py

run_app:
	@echo "Starting Flask web application..."
	$(PYTHON) app.py

lint:
	@echo "Running ruff linter..."
	$(PYTHON) -m ruff check keyloggermax.py app.py

clean:
	@echo "Cleaning up generated files and virtual environment..."
	rm -rf $(VENV_DIR)
	rm -rf output/*.csv
	rm -rf output/screenshots/*.png
	@echo "Cleanup complete."
