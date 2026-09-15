.PHONY: harness-check check

harness-check:
	python3 tools/validate_harness.py

check: harness-check
