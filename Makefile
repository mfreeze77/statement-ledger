PYTHON ?= python
.PHONY: up down test check format contracts proof migrate doctor worker backup restore gpu logs
up down test check format contracts proof migrate doctor worker backup restore gpu logs:
	$(PYTHON) scripts/dev.py $@ $(ARGS)
