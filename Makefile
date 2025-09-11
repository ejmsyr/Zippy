PY := python3

.PHONY: help encode decode smoke test test-ci clean ci

help:
	@echo "Available targets:"
	@echo "  make encode   # Encode texsample.txt -> encoded_output.txt"
	@echo "  make decode   # Decode encoded_output.txt -> stdout"
	@echo "  make smoke    # Run smoke tests matrix"
	@echo "  make test     # Run lightweight test runner (no pytest)"

encode:
	$(PY) Zipper.py --input texsample.txt --output encoded_output.txt --rounds 2 --chunk-size 2 --salt-length 16 --obfuscate

decode:
	$(PY) Unzippy.py --input encoded_output.txt

smoke:
	$(PY) scripts/smoke_tests.py

test:
	$(PY) scripts/run_tests.py

ci: test

clean:
	@echo "Cleaning build artifacts and generated files..."
	rm -f encoded_output.txt
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
