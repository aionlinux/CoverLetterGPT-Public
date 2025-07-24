# Makefile for Cover Letter GPT - Ultra-Fine-Tuned System
# ========================================================
# 
# Comprehensive build and test automation for the advanced Cover Letter GPT system,
# demonstrating production-ready development practices and CI/CD workflows.
#
# Purpose: Ultra-fine-tuned development workflow for public GitHub showcase

.PHONY: help install install-dev test test-unit test-integration test-performance test-coverage lint format type-check security-scan clean build package deploy docs serve-docs benchmark profile setup-env validate-env run demo

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
COVERAGE := coverage
FLAKE8 := flake8
BLACK := black
MYPY := mypy
BANDIT := bandit
PACKAGE_NAME := cover_letter_generator
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs
REPORTS_DIR := reports
VENV_DIR := venv

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

help: ## Show this help message
	@echo "$(CYAN)Cover Letter GPT - Ultra-Fine-Tuned Development Workflow$(RESET)"
	@echo "$(BLUE)========================================================$(RESET)"
	@echo ""
	@echo "$(GREEN)Available targets:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(PURPLE)Examples:$(RESET)"
	@echo "  make install-dev    # Install development dependencies"
	@echo "  make test           # Run complete test suite"
	@echo "  make lint           # Run code quality checks"
	@echo "  make benchmark      # Run performance benchmarks"
	@echo "  make demo           # Run interactive demo"

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Production dependencies installed$(RESET)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-test.txt
	$(PIP) install flake8 black mypy bandit isort pre-commit
	@echo "$(GREEN)✓ Development dependencies installed$(RESET)"

setup-env: ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(YELLOW)Please activate the virtual environment:$(RESET)"
	@echo "  source $(VENV_DIR)/bin/activate  # Linux/Mac"
	@echo "  $(VENV_DIR)\\Scripts\\activate     # Windows"
	@echo "$(YELLOW)Then run: make install-dev$(RESET)"

validate-env: ## Validate development environment
	@echo "$(BLUE)Validating environment...$(RESET)"
	@$(PYTHON) --version
	@$(PIP) --version
	@$(PYTEST) --version
	@echo "$(GREEN)✓ Environment validated$(RESET)"

test: ## Run complete test suite
	@echo "$(BLUE)Running complete test suite...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	$(PYTEST) $(TEST_DIR) -v
	@echo "$(GREEN)✓ All tests completed$(RESET)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	$(PYTEST) $(TEST_DIR) -v -m "unit or not (integration or performance)"
	@echo "$(GREEN)✓ Unit tests completed$(RESET)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	$(PYTEST) $(TEST_DIR) -v -m "integration"
	@echo "$(GREEN)✓ Integration tests completed$(RESET)"

test-performance: ## Run performance tests only
	@echo "$(BLUE)Running performance tests...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	$(PYTEST) $(TEST_DIR) -v -m "performance" --benchmark-only
	@echo "$(GREEN)✓ Performance tests completed$(RESET)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage analysis...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	$(COVERAGE) run -m pytest $(TEST_DIR)
	$(COVERAGE) report
	$(COVERAGE) html
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(RESET)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	$(PYTEST) $(TEST_DIR) -f --tb=short

lint: ## Run code quality checks
	@echo "$(BLUE)Running code quality checks...$(RESET)"
	@echo "$(YELLOW)Running flake8...$(RESET)"
	$(FLAKE8) $(SRC_DIR) --max-line-length=100 --extend-ignore=E203,W503
	@echo "$(YELLOW)Running import sorting check...$(RESET)"
	isort --check-only --diff $(SRC_DIR)
	@echo "$(GREEN)✓ Code quality checks passed$(RESET)"

format: ## Format code using black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(BLACK) $(SRC_DIR) --line-length=100
	isort $(SRC_DIR)
	@echo "$(GREEN)✓ Code formatted$(RESET)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checking...$(RESET)"
	$(MYPY) $(SRC_DIR) --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking completed$(RESET)"

security-scan: ## Run security scanning with bandit
	@echo "$(BLUE)Running security scan...$(RESET)"
	$(BANDIT) -r $(SRC_DIR) -f json -o $(REPORTS_DIR)/security_report.json
	$(BANDIT) -r $(SRC_DIR)
	@echo "$(GREEN)✓ Security scan completed$(RESET)"

quality-check: lint type-check security-scan ## Run all code quality checks
	@echo "$(GREEN)✓ All quality checks completed$(RESET)"

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	$(PYTEST) $(TEST_DIR) -v -m "performance" --benchmark-only --benchmark-json=$(REPORTS_DIR)/benchmark.json
	@echo "$(GREEN)✓ Benchmarks completed - results in $(REPORTS_DIR)/benchmark.json$(RESET)"

profile: ## Run performance profiling
	@echo "$(BLUE)Running performance profiling...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	$(PYTHON) -m cProfile -o $(REPORTS_DIR)/profile.stats run.py
	@echo "$(GREEN)✓ Profiling completed - results in $(REPORTS_DIR)/profile.stats$(RESET)"

clean: ## Clean temporary files and cache
	@echo "$(BLUE)Cleaning temporary files...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf $(REPORTS_DIR)/*.json
	rm -rf $(REPORTS_DIR)/*.html
	rm -rf $(REPORTS_DIR)/*.xml
	@echo "$(GREEN)✓ Cleanup completed$(RESET)"

build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(RESET)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)✓ Distribution packages built$(RESET)"

package: quality-check test build ## Create production package
	@echo "$(BLUE)Creating production package...$(RESET)"
	@echo "$(GREEN)✓ Production package ready$(RESET)"

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(RESET)"
	@mkdir -p $(DOCS_DIR)/api
	$(PYTHON) -m pydoc -w $(SRC_DIR)/$(PACKAGE_NAME)
	mv $(PACKAGE_NAME).html $(DOCS_DIR)/api/
	@echo "$(GREEN)✓ Documentation generated in $(DOCS_DIR)/$(RESET)"

serve-docs: docs ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(RESET)"
	cd $(DOCS_DIR) && $(PYTHON) -m http.server 8000

run: ## Run the application
	@echo "$(BLUE)Starting Cover Letter GPT...$(RESET)"
	$(PYTHON) run.py

demo: ## Run interactive demo
	@echo "$(BLUE)Starting interactive demo...$(RESET)"
	COVER_LETTER_ENV=demo $(PYTHON) run.py

dev-setup: setup-env install-dev ## Complete development setup
	@echo "$(GREEN)✓ Development environment ready$(RESET)"
	@echo "$(YELLOW)Don't forget to activate your virtual environment!$(RESET)"

ci-test: ## Run CI/CD test pipeline
	@echo "$(BLUE)Running CI/CD test pipeline...$(RESET)"
	@make lint
	@make type-check
	@make security-scan
	@make test-coverage
	@make benchmark
	@echo "$(GREEN)✓ CI/CD pipeline completed successfully$(RESET)"

pre-commit: ## Run pre-commit checks
	@echo "$(BLUE)Running pre-commit checks...$(RESET)"
	@make format
	@make lint
	@make type-check
	@make test-unit
	@echo "$(GREEN)✓ Pre-commit checks completed$(RESET)"

release-check: ## Check if ready for release
	@echo "$(BLUE)Checking release readiness...$(RESET)"
	@make quality-check
	@make test
	@make benchmark
	@make security-scan
	@echo "$(GREEN)✓ Release readiness check completed$(RESET)"

# Advanced targets for ultra-fine-tuning showcase

analytics-report: ## Generate comprehensive analytics report
	@echo "$(BLUE)Generating analytics report...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	$(PYTHON) -c "
from src.cover_letter_generator.memory_analytics import get_global_memory_analytics
from src.cover_letter_generator.memory_core import MemoryCore
import json

memory = MemoryCore()
analytics = get_global_memory_analytics()
report = analytics.generate_comprehensive_report(memory.get_memory_data())

with open('$(REPORTS_DIR)/analytics_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

print('Analytics report generated: $(REPORTS_DIR)/analytics_report.json')
"
	@echo "$(GREEN)✓ Analytics report generated$(RESET)"

performance-report: ## Generate performance monitoring report
	@echo "$(BLUE)Generating performance report...$(RESET)"
	@mkdir -p $(REPORTS_DIR)
	$(PYTHON) -c "
from src.cover_letter_generator.performance_monitor import get_global_performance_monitor
import json

monitor = get_global_performance_monitor()
report = monitor.generate_performance_report()

with open('$(REPORTS_DIR)/performance_report.json', 'w') as f:
    json.dump(report, f, indent=2, default=str)

print('Performance report generated: $(REPORTS_DIR)/performance_report.json')
"
	@echo "$(GREEN)✓ Performance report generated$(RESET)"

system-health: ## Check overall system health
	@echo "$(BLUE)Checking system health...$(RESET)"
	@make analytics-report
	@make performance-report
	@echo "$(GREEN)✓ System health check completed$(RESET)"

showcase: ## Generate complete showcase reports
	@echo "$(BLUE)Generating showcase reports...$(RESET)"
	@make clean
	@make ci-test
	@make analytics-report
	@make performance-report
	@make docs
	@echo "$(GREEN)✓ Showcase reports generated$(RESET)"
	@echo "$(CYAN)Ultra-fine-tuned system ready for public showcase!$(RESET)"

# Docker targets (if needed)
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t cover-letter-gpt:latest .
	@echo "$(GREEN)✓ Docker image built$(RESET)"

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(RESET)"
	docker run -it --rm cover-letter-gpt:latest
	@echo "$(GREEN)✓ Docker container started$(RESET)"

# Status and information targets
status: ## Show project status
	@echo "$(CYAN)Cover Letter GPT - Project Status$(RESET)"
	@echo "$(BLUE)================================$(RESET)"
	@echo "$(YELLOW)Environment:$(RESET)       $$($(PYTHON) --version)"
	@echo "$(YELLOW)Source files:$(RESET)     $$(find $(SRC_DIR) -name '*.py' | wc -l) Python files"
	@echo "$(YELLOW)Test files:$(RESET)       $$(find $(TEST_DIR) -name '*.py' | wc -l) test files"
	@echo "$(YELLOW)Lines of code:$(RESET)    $$(find $(SRC_DIR) -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $$1}') lines"
	@echo "$(YELLOW)Documentation:$(RESET)    $$(find $(DOCS_DIR) -name '*.md' | wc -l) documentation files"

info: ## Show detailed project information
	@echo "$(CYAN)Cover Letter GPT - Ultra-Fine-Tuned AI System$(RESET)"
	@echo "$(BLUE)==============================================$(RESET)"
	@echo "$(GREEN)Author:$(RESET)           Claude AI (Anthropic)"
	@echo "$(GREEN)Purpose:$(RESET)          Public GitHub showcase of advanced AI development"
	@echo "$(GREEN)Features:$(RESET)         Ultra-intelligent relevance engine, advanced memory analytics,"
	@echo "                      enterprise-grade error handling, real-time performance monitoring"
	@echo "$(GREEN)Architecture:$(RESET)     Production-ready, scalable, extensively tested"
	@echo "$(GREEN)Quality:$(RESET)          Comprehensive test coverage, type safety, security scanning"
	@echo ""
	@make status
