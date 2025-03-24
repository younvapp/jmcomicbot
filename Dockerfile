FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
COPY . /jmcomicbot
WORKDIR /jmcomicbot
RUN uv sync --frozen --no-dev
ENTRYPOINT ["uv", "run", "python", "main.py"]