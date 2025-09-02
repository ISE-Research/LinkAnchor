# Link-Anchor
an authomated tool for linking commits and issues

## Quick Run

### Install requirements
```bash 
# install rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
. "$HOME/.cargo/env"

# install poetry 
pip install poetry 

# optional: install poetry shell plugin
poetry self add poetry-plugin-shell
```
### Setup virtual env
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
### Install python dependencies
```bash
# install dependencies
poetry install --no-root
```
### Install git-wrapper and code-wrapper development use:
```bash
(cd src/git-wrapper && maturin develop)
(cd src/code-wrapper && maturin develop)
```
### Run
```bash 
export OPENAI_API_KEY=<YOUR_OPEN_API_KEY>

# default mode
python3 -m src.main --git <GIT_REPO_URL> --issue <ISSUE_URL>

# interactive mode
python3 -m src.main --git <GIT_REPO_URL> --issue <ISSUE_URL> --interactive

# debug logs enabled
python3 -m src.main --git <GIT_REPO_URL> --issue <ISSUE_URL> --debug
```
Here is a simple sample for git-anchor on github:
```bash 
export OPENAI_API_KEY=<YOUR_OPEN_API_KEY>

python3 -m src.main --git https://github.com/pallets/flask --issue https://github.com/pallets/flask/issues/5472 --interactive
```

## Benchmarks
### EALink dataset
To run the benchmark on ealink dataset:
```bash 
python3 -m bench.ealink 

# benchmark a simple project:
python3 -m bench.ealink <PROJECT-NAME>

# benchmark upto a certain links (for quick results)
python3 -m bench.ealink --count <NUM>

# rerun benchmark on records that recieved rate-limits from LLM API:
python3 -m bench.ealink --repair
```
Note that the above command downloads the dataset if not available on your local disk. 

After running the benchmark you can see the results via:
```bash 
python3 -m bench.ealink --eval --count <NUM>
```
### Practical dataset
To run benchmark on practical dataset:
```bash 
python3 -m bench.practical
```
