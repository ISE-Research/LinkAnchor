# Git-Anchor
an authomated tool for linking commits and issues

## Quick Run

### setup virtual env
```bash
# using poetry
poetry shell
poetry install

# using virtualenv
python3 -m venv venv
source venv/bin/activate
pip install .
```
### building python package for development use:
```bash
cd src/git-wrapper
maturin develop
```
### Run
```bash 
export OPENAI_API_KEY=<YOUR_OPEN_API_KEY>
python3 src/main.py
```
