.DEFAULT_GOAL := clean torch graph


clean:
	rm emissions.csv *.json *.jsonl

torch:
	./cli.py bench torch HuggingFaceTB/SmolLM2-135M

llamacpp:
	./cli.py bench torch HuggingFaceTB/SmolLM2-135M

ollama:
	./cli.py bench ollama HuggingFaceTB/SmolLM2-135M

graph:
	echo "Open notebooks/parse_data.ipynb with jupyter"

bench:
	./cli.py bench run benchmarks/test2.yaml llamacpp
