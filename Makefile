.PHONY: install test notebooks clean-outputs
install:
	pip install -r requirements.txt
test:
	python -m pytest -q
notebooks:
	python scripts/run_pipeline.py
clean-outputs:
	rm -f reports/tables/*.csv reports/figures/*.png data/processed/*.csv
