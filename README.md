# flask-api-tutorial

## Description
This repository is based on the telcado course, https://teclado.com/rest-apis-flask-python/.
There have been some changes to improve the codebase which includes, but is not limited to:
- type hints
- poetry
- shell scripts to simplify management of docker and poetry

## Dependencies

### Using `poetry`
- `poetry install` from the root dirtectory

### Using `venv` (virtual environment)
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`

## Starting server

### Using `poetry`
- `poetry run flask run`

### Using `venv`
While inside the virtual environment,
- `flask run`
