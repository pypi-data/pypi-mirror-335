# Development

`Geneva` requires Python 3.10+.

Run test

```sh
uv run pytest
```

Run formatter and linter

```sh
uv run ruff format
uv run ruff check
```

Build docs

```sh
cd docs
uv sync --extra docs
uv run mkdocs serve
```