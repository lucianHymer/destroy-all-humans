# Color codes
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
RESET := \033[0m
INFO := @echo "$(GREEN)INFO:$(RESET)"
WARN := @echo "$(YELLOW)WARN:$(RESET)"

# Executable script paths
CMD_PATH := ./bin/generate_embedding
EXEC_PATHS := $(CMD_PATH)
# Output paths include executable paths and any other generated files
OUTPUT_PATHS := $(EXEC_PATHS)

.PHONY: install setup clean check-poetry

# Default target
all: install setup
	$(INFO) Setup complete! Try running: ./generate_embedding --help

# Verify Poetry is installed
check-poetry:
	@command -v poetry >/dev/null 2>&1 || { echo "$(RED)ERROR: Poetry is not installed. Please install it first: https://python-poetry.org/docs/#installation$(RESET)"; exit 1; }

# Install dependencies using Poetry
install: check-poetry
	$(INFO) Installing Python dependencies...
	@poetry install
	$(INFO) Dependencies installed successfully!

# Create and configure the executable script
setup: check-poetry
	$(INFO) Creating executable script...
	@echo '#!/bin/bash\n\npoetry run python ../src/main.py "$$@"' > $(CMD_PATH)
	@chmod u+x $(EXEC_PATHS)
	$(INFO) Created executable: $(CMD_PATH)
	$(WARN) Make sure src/main.py exists before running the script!

# Clean up generated files
clean:
	$(INFO) Cleaning up generated files...
	rm -f $(OUTPUT_PATHS)
	$(INFO) Cleanup complete!
