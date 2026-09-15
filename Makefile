.PHONY: all companion check manifest
all: companion check

companion:
	latexmk -pdf -interaction=nonstopmode -halt-on-error certificates-and-obstructions.tex

check:
	python3 scripts/check_main_certificates.py

manifest:
	python3 scripts/publication.py manifest
