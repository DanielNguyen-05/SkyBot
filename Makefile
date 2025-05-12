# Makefile for Project_1_GenAI Trader

# --- Variables ---
# Use python3 by default, adjust if necessary
PYTHON = python3
PIP = pip3
# Find all Python source files in the current directory
SRC_FILES = $(wildcard *.py)
# Generated data directory
DATA_DIR = Data

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

# Run the main application script
run:
	@echo ">>> Running the main application (main.py)..."
	@echo "--- Make sure ALPACA_API_KEY, ALPACA_API_SECRET, and GEMINI_API_KEY environment variables are set, or be ready to input them ---"
	$(PYTHON) main.py

# Clean up generated files and directories
clean:
	@echo ">>> Cleaning up generated files..."
	@# Remove Python bytecode cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	@# Remove generated data directory (Use with caution!)
	@if [ -d "$(DATA_DIR)" ]; then \
		echo ">>> Removing $(DATA_DIR) directory..."; \
		rm -rf $(DATA_DIR); \
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
	@echo "  make clean      Remove generated files (__pycache__, *.pyc, Data/)"
	@echo "  make lint       Check code style using flake8 (requires flake8)"
	@echo "  make format     Format code using black (requires black)"
	@echo "  make help       Show this help message"