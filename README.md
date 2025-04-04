# Git-Anchor
an authomated tool for linking commits and issues

## Quick Run

### install requirements
```bash 
# install rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
. "$HOME/.cargo/env"

# install poetry 
pip install poetry 

# optional: install poetry shell plugin
poetry self add poetry-plugin-shell
```
### setup virtual env
```bash
# using poetry shell (recommended):
poetry shell

# using poetry env 
poetry env use python3.12
. <(poetry env activate)

# virtualenv
pip -m venv venv
source venv/bin/activate
```
### install python dependencies
```bash
# install dependencies
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
