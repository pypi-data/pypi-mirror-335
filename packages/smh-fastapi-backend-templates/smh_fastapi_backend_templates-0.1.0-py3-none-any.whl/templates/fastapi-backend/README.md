# FastAPI Backend

FastAPI Backend API helps you do awesome stuff. 🚀

## Features

- Built with **FastAPI** for high-performance web APIs
- Uses **Poetry** for dependency management
- Supports **orjson** for fast JSON serialization
- Includes **CORS middleware** for cross-origin requests
- Structured logging configuration
- Database support with **SQLAlchemy**, **asyncpg**, and **psycopg2**
- **Alembic** for database migrations
- **Motor** for MongoDB interaction
- **pyspark** and **sentence-transformers** for data processing and NLP
- **Pre-commit hooks** configured for linting and formatting
- Type checking with **mypy**
- Linting with **ruff**
- Build support with **Nuitka**

## Requirements

- Python >= 3.12
- Poetry (Install it if not available: `curl -sSL https://install.python-poetry.org | python3 -`)
- (Optional) Make (for running predefined commands)

## Installation

Ensure you have **Poetry** installed. Then run:

```sh
poetry install
```

If you have `make` installed, you can use:

```sh
make install
```

## Running the Application

To start the application, run:

```sh
poetry run python main.py
```

Or if `make` is available:

```sh
make start
```

## Updating Dependencies

```sh
poetry update
```

Or with `make`:

```sh
make update
```

## Code Formatting & Linting

To format the code:

```sh
poetry run ruff format
```

To lint the code:

```sh
poetry run ruff check
```

To check types with **mypy**:

```sh
poetry run mypy .
```

Or run all checks at once using `make`:

```sh
make check
```

## Pre-commit Hooks

To install pre-commit hooks:

```sh
poetry run pre-commit install
```

Or with `make`:

```sh
make pc-install
```

## Logging Configuration

Logging is configured using `LOGGING_CONFIG` from `app.config.logging_config`. Ensure your logs are being saved as required.

## License

This project is licensed under the **Apache 2.0** license. See [LICENSE](https://www.apache.org/licenses/LICENSE-2.0.html) for details.

## Contact

For support, contact **FastAPI Backend** team:
- Email: [email@gmail.com](mailto:email@gmail.com)
- Website: [FastAPI Backend Contact](http://x-force.example.com/contact/)

