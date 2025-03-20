#!/usr/bin/env bash

set -exu -o pipefail

if [[ -z "${GITHUB_ACTIONS+x}" ]]; then
  echo "GITHUB_ACTIONS environment variable is not set.Use local mode."
  uv sync --all-extras --dev
  uv run ruff format src
  uv run ruff format tests
  uv run ruff check src --fix
  uv run mypy src --strict
  uv run pytest tests --durations=5 --cov=. --cov-report term
else
  echo "GITHUB_ACTIONS environment variable is set.Use CI mode."
  uv sync --all-extras --dev
  uv run ruff check src
  uv run mypy src --strict
  uv run pytest tests --durations=5 --cov=. --cov-report term
fi
