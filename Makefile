.PHONY: install, run-demo, ruff, help

install:
	poetry install
	pre-commit install

demo:
	python3 examples/demo.py

async-demo:
	python3 examples/async_demo.py

paranet-demo:
	python3 examples/paranets_demo.py

ruff:
	ruff check --fix
	ruff format

help:
	@echo "Available commands:"
	@echo "  install   - Install dependencies and set up pre-commit hooks"
	@echo "  ruff      - Format code and fix linting issues using ruff"
	@echo "  demo      - Run /examples/demo.py file"
	@echo "  async-demo - Run /examples/async_demo.py file"
	@echo "  paranet-demo - Run /examples/paranets_demo.py file"

test-neuroweb-testnet:
	pytest tests/testnet/Neuroweb_Testnet.py -s --json-report --json-report-file=.report/testnet_neuroweb.json --html=.report/testnet_neuroweb.html --self-contained-html

report-neuroweb-testnet:
	python report_Testnet_Neuroweb.py

test-base-testnet:
	pytest tests/testnet/Base_Testnet.py -s --json-report --json-report-file=.report/testnet_base.json --html=.report/testnet_base.html --self-contained-html

report-base-testnet:
	python report_Testnet_Base.py

test-gnosis-testnet:
	pytest tests/testnet/Gnosis_Testnet.py -s --json-report --json-report-file=.report/testnet_gnosis.json --html=.report/testnet_gnosis.html --self-contained-html

report-gnosis-testnet:
	python report_Testnet_Gnosis.py

test-neuroweb-mainnet:
	pytest tests/mainnet/Neuroweb_Mainnet.py -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html

report-neuroweb-mainnet:
	python report_Mainnet_Neuroweb.py

test-base-mainnet:
	pytest tests/mainnet/Base_Mainnet.py -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html

report-base-mainnet:
	python report_Mainnet_Base.py

test-gnosis-mainnet:
	pytest tests/mainnet/Gnosis_Mainnet.py -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html

report-gnosis-mainnet:
	python report_Mainnet_Gnosis.py
