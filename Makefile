.PHONY: setup-dev test

# Install runtime and development dependencies
setup-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	python -m spacy download en_core_web_sm

# Run the test suite using pytest
# Assumes dependencies have been installed


test:
	pytest
