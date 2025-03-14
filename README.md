# setup

```
poetry install
```
This will not install dependencies for all tasks. Only enough for cli helpers.
You might need torch, transformers...
```pip install -r requirements/inference.txt```

Some dependencies might not be needed, to install everything:
```
poetry install --extras "download measure llm"
```

# run a benchmark 

To run a single model:
```
make clean; make torch
```

This will output 2 files:
- emissions.csv
- events.jsonl

You can use the files in ./notebooks to analyze the results.


To run a complete set from a yaml file:
```
./cli.py bench run benchmarks/smollm2-135m.yaml torch
./cli.py results parse-results bench-smollm2-135m-1.jsonl
```

# using docker
You can use the cli script to get a shell in a container or run a task in docker:
```
./cli.py docker build
./cli.py docker shell
cd /build
poetry run ./cli.py bench torch HuggingFaceTB/SmolLM2-135M
```
Or to run a command: 
```
/cli.py docker bench torch HuggingFaceTB/SmolLM2-135M
```

Useful folders:
- /app: llama.cpp
- /build: this app

You can also run the container directly. See commands/docker.py for an example with cuda and powercap.

# settings
Some settings can be set using a .env file or env vars.

- LLAMA_CPP_LOAD_OPTIONS: json providing additional options to `from_pretrained`
  ex: '{"n_gpu_layers":30,"n_threads":"1","n_batch":1}'

# links
