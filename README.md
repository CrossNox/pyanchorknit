# PyAnchorKnit

# Dev install
## Poetry
### Install pipx
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx completions
```

### Install poetry
```bash
pipx install poetry
```

### Install the project
```bash
poetry install
```

## Install [pre-commit](https://pre-commit.com) hooks
```bash
poetry run pre-commit install
poetry run pre-commit install -t pre-push
```
