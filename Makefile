# Makefile for Project_1_GenAI Trader

# --- Variables ---
# Use python3 by default, adjust if necessary
PYTHON = python3
PIP = pip3
# Find all Python source files in the current directory
SRC_FILES = $(wildcard *.py)
# Generated data directory
DATA_DIR = Data
# Get a list of Git-tracked files in the data directory
GIT_TRACKED_FILES := $(shell git ls-tree --full-tree -r HEAD:$(DATA_DIR) | awk '{print $$4}')

# --- Tool Commands (Optional but recommended) ---
# Install flake8 and black via pip if you want to use lint/format targets
LINTER = flake8
FORMATTER = black

# --- Targets ---

# Phony targets are rules that don't produce an output file with the same name
.PHONY: all install run clean lint format help

# Default target: Show help message
all: help

# Install dependencies from requirements.txt
install: requirements.txt
	@echo ">>> Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo ">>> Dependencies installed."

# Run the bot application script
run:
	@echo ">>> Running the main application (bot.py)..."
	@echo "--- Make sure ALPACA_API_KEY, ALPACA_API_SECRET, and GEMINI_API_KEY environment variables are set, or be ready to input them ---"
	$(PYTHON) bot.py

# Clean up generated files and directories (excluding Git-tracked files in Data)
clean:
	@echo ">>> Cleaning up generated files..."
	@# Remove Python bytecode cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	@# Clean Data directory (excluding Git tracked files)
	@echo ">>> Cleaning $(DATA_DIR) (excluding Git tracked files)..."
	@if [ -d "$(DATA_DIR)" ]; then \
		for file in $$(ls -A $(DATA_DIR)); do \
			if [ -f "$(DATA_DIR)/$$file" ] && ! echo "$(DATA_DIR)/$$file" | grep -q -F -e "$$(echo $(GIT_TRACKED_FILES) | sed 's/ /\\n/g')"; then \
				rm -f "$(DATA_DIR)/$$file"; \
			fi; \
		done; \
		echo ">>> $(DATA_DIR) cleaned (excluding Git tracked files)."; \
	else \
		echo ">>> $(DATA_DIR) directory not found, nothing to remove."; \
	fi
	@echo ">>> Cleanup complete."

# Lint the Python code using flake8 (requires flake8 to be installed)
lint:
	@echo ">>> Linting Python files using $(LINTER)..."
	$(LINTER) $(SRC_FILES)

# Format the Python code using black (requires black to be installed)
format:
	@echo ">>> Formatting Python files using $(FORMATTER)..."
	$(FORMATTER) $(SRC_FILES)

# Show help message
help:
	@echo "Available commands:"
	@echo "  make install    Install required Python packages from requirements.txt"
	@echo "  make run        Run the main trading application (main.py)"
	@echo "  make clean      Remove generated files (__pycache__, *.pyc, Data/ excluding Git tracked files)"
	@echo "  make lint       Check code style using flake8 (requires flake8)"
	@echo "  make format     Format code using black (requires black)"
	@echo "  make help       Show this help message"