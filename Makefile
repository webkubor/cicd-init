.PHONY: install dev build docker test clean

# Install in local venv
install:
	python3 -m venv .venv
	.venv/bin/python -m pip install -e .

# Install with dev dependencies
dev: install

# Build Docker image
docker:
	docker build -t cicd-init:latest .

# Run via Docker (usage: make docker-run DIR=/path/to/project)
docker-run:
	docker run --rm -v $(DIR):/src cicd-init:latest init -d /src

# Test with dry-run on a sample project
test:
	@echo "Creating temp project for testing..."
	@mkdir -p /tmp/cicd-init-test
	@echo '{"name":"test","scripts":{"build":"echo ok","lint":"echo ok","test":"echo ok"}}' > /tmp/cicd-init-test/package.json
	@cd /tmp/cicd-init-test && git init && git remote add origin https://github.com/example/test.git 2>/dev/null || true
	.venv/bin/cicd-init init -d /tmp/cicd-init-test --all --dry-run
	@rm -rf /tmp/cicd-init-test

# Clean build artifacts
clean:
	rm -rf .venv *.egg-info dist build __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
