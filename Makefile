all:run

run:src/main.py
	@echo "executing main.py..."
	@python3 src/main.py

config:.pre-commit-config.yaml
	@echo "installing precommit hooks..."
	pip install pre-commit
	pre-commit install
	pre-commit run --all-files
	@echo "precommit hooks have been installed!"