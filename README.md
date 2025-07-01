# Git-Anchor
an authomated tool for linking commits and issues

## Quick Run

### install requirements
```bash 
# install rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
. "$HOME/.cargo/env"

# (optional) install uv
pip install uv

```
### setup virtual env
```bash
# using uv venv 
uv venv
venv=$(uv venv --allow-existing  2>&1 | grep source | awk '{print$4}')
source $venv

# virtualenv
pip -m venv venv
source venv/bin/activate
```
### install python dependencies
```bash
# install dependencies
uv pip install -r pyproject.toml
```
### install git-wrapper and code-wrapper development use:
```bash
(cd src/git-wrapper && maturin develop)
(cd src/code-wrapper && maturin develop)
```
### Run
```bash 
export OPENAI_API_KEY=<YOUR_OPEN_API_KEY>

# default mode
uv run -m src.main --git <GIT_REPO_URL> --issue <ISSUE_URL>

# interactive mode
uv run -m src.main --git <GIT_REPO_URL> --issue <ISSUE_URL> --interactive

# debug logs enabled
uv run -m src.main --git <GIT_REPO_URL> --issue <ISSUE_URL> --debug
```
