.PHONY: all check manifest verify
all: check

check:
	python3 scripts/check_main_certificates.py
	python3 scripts/examples/proximity-prize/check_points.py

manifest:
	python3 scripts/publication.py manifest

verify:
	python3 scripts/publication.py verify
