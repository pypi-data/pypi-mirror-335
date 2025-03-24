test: ## Execute test suite
	uv run pytest

init: ## Initialize development environment
	@echo "🚀 Initializing project..."
	@if [ -d ".venv" ]; then rm -rf .venv; fi
	uv venv
	uv pip install --upgrade pip
	uv pip install -r pyproject.toml --all-extras
	uv sync

install-dev: ## Install development dependencies
	@echo "🔧 Installing development dependencies..."
	uv pip install -e ".[dev]"
	@echo "✅ Development dependencies installed successfully"

run: ## Run the application
	@echo "🚀 Starting application..."
	uv run train.py

check: ## Run code quality checks
	@echo "🔍 Running code analysis..."
	uvx ruff check

format: ## Format source code
	@echo "🔧 Formatting code..."
	ruff format .
	ruff check --fix

upgrade: ## Update project dependencies
	@echo "📡 Upgrading dependencies..."
	uv lock --upgrade
	uv sync
	uv pip freeze > requirements.txt
	@echo "✅ Dependencies updated successfully"

pre-commit: ## Run pre-commit checks
	pre-commit run --all-files

build: ## Build the project
	@echo "🔨 Building project..."
	uv build
	@echo "✅ Build completed successfully"

publish: ## Publish the project
	@echo "📦 Publishing project..."
	uv publish
	@echo "✅ Project published successfully"

coverage: ## Run tests with coverage
	@echo "📊 Running tests with coverage..."
	uv run pytest -v --cov=src/logfire_callback --cov-report=html
	@echo "✅ Coverage report generated successfully"
