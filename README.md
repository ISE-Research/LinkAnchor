# Git-Anchor
an authomated tool for linking commits and issues

## Quick Run

### setup virtual env
```bash
# ensure poetry is installed
pip install poetry

# install dependencies
poetry shell
poetry install --no-root
```
### install git-wrapper development use:
```bash
(cd src/git-wrapper && maturin develop)
```
### Run
```bash 
export OPENAI_API_KEY=<YOUR_OPEN_API_KEY>
python3 src/main.py
```
