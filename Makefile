.DEFAULT_GOAL := help

# Variables
PYTHON := python3
VENV := env
VENV_BIN := $(VENV)/bin
PIP := $(VENV_BIN)/pip
PYTHON_VENV := $(VENV_BIN)/python
PORT_FRONTEND := 8080

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[34m

##@ General

.PHONY: help
help: ## Display this help message
	@echo "$(COLOR_BOLD)Available targets:$(COLOR_RESET)"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(COLOR_GREEN)%-20s$(COLOR_RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(COLOR_BOLD)%s$(COLOR_RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.PHONY: install
install: ## Install dependencies and set up virtual environment
	@echo "$(COLOR_BLUE)Creating virtual environment...$(COLOR_RESET)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(COLOR_BLUE)Installing dependencies...$(COLOR_RESET)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(COLOR_GREEN)Setup complete!$(COLOR_RESET)"

.PHONY: clean
clean: ## Remove Python cache files and virtual environment
	@echo "$(COLOR_YELLOW)Cleaning up...$(COLOR_RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(COLOR_GREEN)Cleanup complete!$(COLOR_RESET)"

##@ Running Services

.PHONY: mcp
mcp: ## Run the MCP server
	@echo "$(COLOR_BLUE)Starting MCP server...$(COLOR_RESET)"
	$(PYTHON_VENV) mcp_server/main.py

.PHONY: agent-backend
agent-backend: ## Run the agent backend server
	@echo "$(COLOR_BLUE)Starting agent backend...$(COLOR_RESET)"
	$(PYTHON_VENV) agent/backend/main.py

.PHONY: agent-frontend
agent-frontend: ## Run the agent frontend server
	@echo "$(COLOR_BLUE)Starting agent frontend on port $(PORT_FRONTEND)...$(COLOR_RESET)"
	cd agent/frontend && npm run dev

.PHONY: merchant
merchant: ## Run the merchant service
	@echo "$(COLOR_BLUE)Starting merchant service...$(COLOR_RESET)"
	$(PYTHON_VENV) merchant/main.py

##@ Code Quality

.PHONY: lint
lint: ## Run linting checks (requires pylint or flake8)
	@echo "$(COLOR_BLUE)Running linting checks...$(COLOR_RESET)"
	@if command -v $(VENV_BIN)/pylint >/dev/null 2>&1; then \
		$(VENV_BIN)/pylint mcp_server/ agent/ merchant/ || true; \
	elif command -v $(VENV_BIN)/flake8 >/dev/null 2>&1; then \
		$(VENV_BIN)/flake8 mcp_server/ agent/ merchant/ || true; \
	else \
		echo "$(COLOR_YELLOW)No linter found. Install pylint or flake8.$(COLOR_RESET)"; \
	fi

.PHONY: format
format: ## Format code using black (requires black)
	@echo "$(COLOR_BLUE)Formatting code...$(COLOR_RESET)"
	@if command -v $(VENV_BIN)/black >/dev/null 2>&1; then \
		$(VENV_BIN)/black mcp_server/ agent/ merchant/; \
	else \
		echo "$(COLOR_YELLOW)Black not installed. Run: pip install black$(COLOR_RESET)"; \
	fi

.PHONY: test
test: ## Run tests (requires pytest)
	@echo "$(COLOR_BLUE)Running tests...$(COLOR_RESET)"
	@if command -v $(VENV_BIN)/pytest >/dev/null 2>&1; then \
		$(VENV_BIN)/pytest tests/ -v; \
	else \
		echo "$(COLOR_YELLOW)Pytest not installed. Run: pip install pytest$(COLOR_RESET)"; \
	fi
