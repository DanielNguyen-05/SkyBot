# Makefile for Project_1_GenAI Trader

# --- Variables ---
PYTHON = python3
PIP = pip3
SRC_FILES = $(wildcard *.py)
DATA_DIR = Data

# --- Tool Commands (Optional but recommended) ---
LINTER = flake8
FORMATTER = black

# --- Targets ---

.PHONY: all install run clean lint format help

all: help

install: requirements.txt
	@echo ">>> Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo ">>> Dependencies installed."

run:
	@echo ">>> Running the main application (bot.py)..."
	@echo "--- Make sure ALPACA_API_KEY, ALPACA_API_SECRET, and GEMINI_API_KEY environment variables are set, or be ready to input them ---"
	$(PYTHON) bot.py

clean:
	@echo ">>> Cleaning up generated files..."
	@# Remove Python bytecode cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	@# Remove all files and directories in $(DATA_DIR)
	@echo ">>> Removing all files in $(DATA_DIR)..."
	@if [ -d "$(DATA_DIR)" ]; then \
		rm -rf $(DATA_DIR)/*; \
		echo ">>> $(DATA_DIR) cleaned."; \
	else \
		echo ">>> $(DATA_DIR) directory not found, nothing to remove."; \
	fi
	@echo ">>> Cleanup complete."

lint:
	@echo ">>> Linting Python files using $(LINTER)..."
	$(LINTER) $(SRC_FILES)

format:
	@echo ">>> Formatting Python files using $(FORMATTER)..."
	$(FORMATTER) $(SRC_FILES)

help:
	@echo "Available commands:"
	@echo "  make install    Install required Python packages from requirements.txt"
	@echo "  make run        Run the main trading application (bot.py)"
	@echo "  make clean      Remove generated files (__pycache__, *.pyc, Data/)"
	@echo "  make lint       Check code style using flake8 (requires flake8)"
	@echo "  make format     Format code using black (requires black)"
	@echo "  make help       Show this help message"
