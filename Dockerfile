FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y \
        ffmpeg \
        curl \
        ca-certificates \
        libsm6 \
        libxext6 \
    && rm -rf /var/lib/apt/lists/*

ADD https://astral.sh/uv/0.6.14/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && \
    rm /uv-installer.sh

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

EXPOSE 8081

CMD ["uv", "run", "flask", "run", "--host=0.0.0.0", "--port=8081"]
