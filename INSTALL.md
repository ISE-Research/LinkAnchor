# Installation

> Estimated setup time: < 10 minutes.

## Prerequisites
- Rust: Required for the git and code wrapper modules.
- Python 3.10+: Recommended environment.

## Installation Steps

```Bash

# 1. Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
. "$HOME/.cargo/env"

# 2. Setup Virtual Environment (using uv or venv)
python3 -m venv venv
source venv/bin/activate

# 3. Install Python Dependencies
pip install . 

# 4. Install Git & Code Wrapper modules
(cd src/git-wrapper && maturin develop)
(cd src/code-wrapper && maturin develop)
```
