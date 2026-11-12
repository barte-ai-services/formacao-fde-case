.PHONY: help check test

help:  ## Mostra estes alvos
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-8s %s\n", $$1, $$2}'

check: test ## O gate antes do commit: os testes

test: ## pytest
	uv run pytest -q
