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

##@ Running Services

.PHONY: mcp
mcp: ## Run the MCP server
	@echo "$(COLOR_BLUE)Starting MCP server...$(COLOR_RESET)"
	cd $(dir $(realpath $(firstword $(MAKEFILE_LIST)))) && PYTHONPATH=. $(PYTHON_VENV) mcp_server/main.py

.PHONY: agent-backend
agent-backend: ## Run the agent backend server
	@echo "$(COLOR_BLUE)Starting agent backend...$(COLOR_RESET)"
	PYTHONPATH=. $(PYTHON_VENV) agent/backend/main.py

.PHONY: agent-frontend
agent-frontend: ## Run the agent frontend server
	@echo "$(COLOR_BLUE)Starting agent frontend on port $(PORT_FRONTEND)...$(COLOR_RESET)"
	cd agent/frontend-v2 && npm run dev

.PHONY: agent-frontend-legacy
agent-frontend-legacy: ## Run the agent frontend server
	@echo "$(COLOR_BLUE)Starting agent frontend on port $(PORT_FRONTEND)...$(COLOR_RESET)"
	cd agent/frontend && npm run dev
