run.app:
	uvicorn src.app:app --host 0.0.0.0 --port 8000

test.unit:
	python -m pytest --cov=src --cov-report=term-missing

