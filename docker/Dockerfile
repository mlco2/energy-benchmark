FROM ghcr.io/ggerganov/llama.cpp:full-cuda AS base
COPY docker /build/docker
COPY pyproject.toml /build/
COPY requirements /build/requirements/
WORKDIR /build
RUN /build/docker/install.sh


FROM base AS app
COPY . /build/
ENTRYPOINT []
CMD ["cli.py"]