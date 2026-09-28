.PHONY: test demo serve contracts spec check

test:
	python -m pytest -q

demo:
	statement-ledger --db data/demo.sqlite3 demo

serve:
	statement-ledger --db data/demo.sqlite3 serve

contracts:
	python scripts/export-contracts.py

spec:
	python scripts/compile-spec.py

check:
	python -m compileall -q src
	python -m pytest -q
	python scripts/check-standalone.py
