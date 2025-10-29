# DocsFlow Makefile
# Automation commands for development and deployment

.PHONY: help install build serve clean lint validate test docker-build docker-run deploy

# Default target
help: ## Show this help message
	@echo "DocsFlow - Documentation Pipeline Automation"
	@echo "============================================"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development setup
install: ## Install Python dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully"

install-dev: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt
	pip install pre-commit black flake8 mypy
	pre-commit install
	@echo "✅ Development environment setup complete"

# Documentation build
build: ## Build documentation site
	@echo "🏗️  Building documentation..."
	.venv/Scripts/python.exe -m mkdocs build --clean --strict
	@echo "✅ Documentation built successfully"

serve: ## Serve documentation locally
	@echo "🚀 Starting development server..."
	.venv/Scripts/python.exe -m mkdocs serve --dev-addr localhost:8000

# Quality checks
lint: ## Run documentation linting
	@echo "🔍 Running documentation linting..."
	python scripts/lint_docs.py

validate: ## Validate YAML configuration files
	@echo "📋 Validating YAML files..."
	python scripts/validate_yaml.py

test: lint validate ## Run all tests and validation
	@echo "🧪 Running comprehensive tests..."
	@echo "✅ All tests passed"

# Docker operations
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t docsflow:latest .
	@echo "✅ Docker image built successfully"

docker-run: ## Run documentation server in Docker
	@echo "🐳 Starting Docker container..."
	docker run --rm -p 8000:8000 -v ${PWD}:/app docsflow:latest

docker-compose-up: ## Start all services with docker-compose
	@echo "🐳 Starting Docker Compose services..."
	docker-compose up -d docsflow

docker-compose-build: ## Build and start with docker-compose
	@echo "🐳 Building and starting Docker Compose services..."
	docker-compose up --build -d

# Deployment
deploy-local: build ## Deploy to local environment
	@echo "🚀 Deploying locally..."
	python scripts/upload_to_fluidtopics.py

deploy: ## Deploy to production (requires environment variables)
	@echo "🚀 Deploying to production..."
	@if [ -z "$(FLUID_URL)" ] || [ -z "$(FLUID_USER)" ] || [ -z "$(FLUID_PASS)" ]; then \
		echo "❌ Missing required environment variables: FLUID_URL, FLUID_USER, FLUID_PASS"; \
		exit 1; \
	fi
	$(MAKE) build
	python scripts/upload_to_fluidtopics.py

# Maintenance
clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf site/
	rm -f docs_package.zip
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete"

clean-docker: ## Clean Docker images and containers
	@echo "🧹 Cleaning Docker resources..."
	docker system prune -f
	docker image prune -f
	@echo "✅ Docker cleanup complete"

# Git operations
git-setup: ## Setup git hooks and configuration
	@echo "🔧 Setting up git configuration..."
	git config --local core.autocrlf input
	git config --local pull.rebase true
	@echo "✅ Git configuration complete"

# CI/CD simulation
ci-local: ## Run full CI pipeline locally
	@echo "🔄 Running local CI pipeline..."
	$(MAKE) clean
	$(MAKE) lint
	$(MAKE) validate
	$(MAKE) build
	$(MAKE) docker-build
	@echo "✅ Local CI pipeline completed successfully"

# Quick development workflows
dev: ## Quick development setup (install + serve)
	$(MAKE) install
	$(MAKE) serve

quick-check: ## Quick quality check (lint + validate)
	$(MAKE) lint
	$(MAKE) validate

# Release management
release-check: ## Check if ready for release
	@echo "🔍 Checking release readiness..."
	$(MAKE) clean
	$(MAKE) test
	$(MAKE) build
	@echo "✅ Ready for release"

# Information
info: ## Show project information
	@echo "DocsFlow Project Information"
	@echo "==========================="
	@echo "Python version: $$(.venv/Scripts/python.exe --version 2>/dev/null || python --version)"
	@echo "MkDocs version: $$(.venv/Scripts/python.exe -m mkdocs --version 2>/dev/null || echo 'MkDocs not installed')"
	@echo "Docker version: $$(docker --version 2>/dev/null || echo 'Docker not installed')"
	@echo "Current branch: $$(git branch --show-current 2>/dev/null || echo 'Not a git repository')"
	@echo "Last commit: $$(git log -1 --oneline 2>/dev/null || echo 'No commits')"

# Environment setup
env-setup: ## Setup environment variables from template
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp .env.example .env; \
		echo "✅ .env file created. Please update with your values."; \
	else \
		echo "⚠️  .env file already exists"; \
	fi