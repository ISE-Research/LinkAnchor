# 💡 LinkAnchor: An Autonomous LLM-Based Agent for Issue-to-Commit Link Recovery

![GHCR Version](https://img.shields.io/badge/ghcr.io-linkanchor:latest-blue?logo=docker)
![License](https://img.shields.io/github/license/ISE-Research/LinkAnchor)

> This repository contains the artifact for the paper **"LinkAnchor: An Autonomous LLM-Based Agent for Issue-to-Commit Link Recovery"**, accepted at FSE 2026.
> For the exact `FSE'26` replication package, please visit the `fse26` branch.

LinkAnchor is the first autonomous LLM-based agent designed specifically for issue-to-commit link recovery (ILR). Unlike prior methods that score issue-commit pairs in isolation, LinkAnchor treats link recovery as a **dynamic heuristic** search over the commit graph. This allows it to aggregate the entire chain of contributing changes to identify the final resolving commit, effectively recovering distributed fixes.

# Table of Contents

* [Overview](#🔍-overview)
* [Installation](#⚙️-installation)
* [Quick Start](#🚀-quick-start)
* [Reproduction Instructions](#📊-reproduction-instructions)
* [Project Structure](#📂-project-structure)

# 🔍 Overview

This artifact provides the complete implementation of the LinkAnchor agent, including its lazy-access architecture and specialized function calls for repository navigation. It is designed to work with both `GitHub` and `Jira` issue-tracking systems and supports a wide range of programming languages via the `Tree-sitter` parser.

# ⚙️ Installation 

## Docker
You can pull the prebuilt Docker image:
```bash 
docker pull ghcr.io/ise-research/linkanchor
```
or to build it manually:
```bash 
docker build . --tag ghcr.io/ise-research/linkanchor
```

## From Source

> Estimated setup time: < 10 minutes.

### Prerequisites
- Rust: Required for the git and code wrapper modules.
- Python 3.10+: Recommended environment.

### Installation Steps

```bash

# 1. Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
. "$HOME/.cargo/env"

# 2. Set up Virtual Environment (using uv or venv)
python3 -m venv venv
source venv/bin/activate

# 3. Install Python Dependencies
pip install . 

# 4. Install Git & Code Wrapper module
(cd src/git-wrapper  && maturin build --release && pip install target/wheels/*.whl)
(cd src/code-wrapper && maturin build --release && pip install target/wheels/*.whl)
```

# 🚀 Quick Start

> You should have an OpenAI API Key; LinkAnchor utilizes LLMs (defaulting to GPT-4o-mini for cost-efficiency).

Use the following command to find the commit hash of the resolving commit:

```bash 
# If using the docker image
docker run -it \
  -e OPENAI_API_KEY=<YOUR_API_KEY> \
  ghcr.io/ise-research/linkanchor \
  --git https://github.com/pallets/flask --issue https://github.com/pallets/flask/issues/5472

# If using raw python3
export OPENAI_API_KEY=<YOUR_API_KEY>
python3 -m src.main --git https://github.com/pallets/flask --issue https://github.com/pallets/flask/issues/5472

# if using uv (Recommended)
export OPENAI_API_KEY=<YOUR_API_KEY>
uv run -m src.main --git https://github.com/pallets/flask --issue https://github.com/pallets/flask/issues/5472
```

Using the `--explain` flag, you can enter interactive mode in which LinkAnchor will explain the decision-making process behind each step of the process.

```bash 
# If using the docker image
docker run -it \
  -e OPENAI_API_KEY=<YOUR_API_KEY> \
  ghcr.io/ise-research/linkanchor \
  --git https://github.com/pallets/flask --issue https://github.com/pallets/flask/issues/5472 --explain

# If using raw python3
export OPENAI_API_KEY=<YOUR_API_KEY>
python3 -m src.main --git https://github.com/pallets/flask --issue https://github.com/pallets/flask/issues/5472 --explain

# if using uv (Recommanded)
export OPENAI_API_KEY=<YOUR_API_KEY>
uv run -m src.main --git https://github.com/pallets/flask --issue https://github.com/pallets/flask/issues/5472 --explain
```


# 📊 Reproduction Instructions

> To reproduce the primary results (Table 2 in the paper).

```bash 
# This script runs LinkAnchor across the Apache dataset (Ambari, Calcite, etc.)
# Note that this script also downloads and cleans up the dataset.
python3 -m bench.eaklink
```

> Results show LinkAnchor outperforms state-of-the-art baselines (EasyLink, EALink) by 41-714% in Hit@1. (For more information, refer to the paper)

# 📂 Project Structure

- [src](src/): Core logic for the LLM agent and repository navigation.
    - [git-wrapper](src/git-wrapper): Rust-based high-performance git interface.
    - [code-wrapper](src/code-wrapper): Rust-based Tree-sitter integration for code analysis.
    - [issue-wrapper](src/issue_wrapper): python-based github/jira integration for issue-centered data retrieval
- [bench](bench): Scripts and tools to reproduce the paper's benchmarks.
    - [data_gen.py](bench/data_gen.py): Script for dataset download and cleanup.
    - [ealink.py](bench/ealink.py): Script for reproducing the experiment on `ealink`'s dataset.
    - [practical.py](bench/practical.py): Script for reproducing the experiment on any arbitrary dataset of github issues.
- [README.md](README.md): Artifact introduction.
- [INSTALL.md](INSTALL.md): Detailed installation instructions.
- [REQUIREMENTS.md](REQUIREMENTS.md): Environmental requirements.
- [STATUS.md](STATUS.md): Badge application status.
- [LICENSE](LICENSE): Open-source license (MIT)
