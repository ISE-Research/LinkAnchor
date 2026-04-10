FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/ISE-Research/LinkAnchor"

# 1. Install Rust toolchain
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Add Rust to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# 2. Set working directory
WORKDIR /app

# 4. Copy project files
COPY . .

# 5. Install Python dependencies
RUN pip install . 

# 6. Build rust-written modules using maturin
RUN cd /app/src/git-wrapper && maturin build --release && pip install --no-cache-dir target/wheels/*.whl
RUN cd /app/src/code-wrapper && maturin build --release && pip install --no-cache-dir target/wheels/*.whl

# 7. Define the entry point for the agent
ENTRYPOINT ["python", "-m", "src.main"]
