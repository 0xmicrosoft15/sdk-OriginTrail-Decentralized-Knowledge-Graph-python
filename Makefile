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

run-test:
	pytest

help:
	@echo "Available commands:"
	@echo "  install   - Install dependencies and set up pre-commit hooks"
	@echo "  ruff      - Format code and fix linting issues using ruff"
	@echo "  run-test  - Run tests"
	@echo "  demo      - Run /examples/demo.py file"
	@echo "  async-demo - Run /examples/async_demo.py file"
	@echo "  paranet-demo - Run /examples/paranets_demo.py file"

test-neuroweb-testnet:
	PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

report-neuroweb-testnet:
	python report_Testnet_Neuroweb.py

test-neuroweb-node_01-testnet:
	NODE_TO_TEST="Node 01" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_04-testnet:
	NODE_TO_TEST="Node 04" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_05-testnet:
	NODE_TO_TEST="Node 05" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_06-testnet:
	NODE_TO_TEST="Node 06" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_07-testnet:
	NODE_TO_TEST="Node 07" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_08-testnet:
	NODE_TO_TEST="Node 08" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_09-testnet:
	NODE_TO_TEST="Node 09" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_10-testnet:
	NODE_TO_TEST="Node 10" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_13-testnet:
	NODE_TO_TEST="Node 13" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_14-testnet:
	NODE_TO_TEST="Node 14" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_21-testnet:
	NODE_TO_TEST="Node 21" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_23-testnet:
	NODE_TO_TEST="Node 23" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-neuroweb-node_37-testnet:
	NODE_TO_TEST="Node 37" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Neuroweb_Testnet.py

test-gnosis-testnet:
	PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

report-gnosis-testnet:
	python report_Testnet_Gnosis.py

test-gnosis-node_01-testnet:
	NODE_TO_TEST="Node 01" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_04-testnet:
	NODE_TO_TEST="Node 04" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_05-testnet:
	NODE_TO_TEST="Node 05" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_06-testnet:
	NODE_TO_TEST="Node 06" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_07-testnet:
	NODE_TO_TEST="Node 07" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_08-testnet:
	NODE_TO_TEST="Node 08" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_09-testnet:
	NODE_TO_TEST="Node 09" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_10-testnet:
	NODE_TO_TEST="Node 10" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_13-testnet:
	NODE_TO_TEST="Node 13" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_14-testnet:
	NODE_TO_TEST="Node 14" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_21-testnet:
	NODE_TO_TEST="Node 21" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_23-testnet:
	NODE_TO_TEST="Node 23" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-gnosis-node_37-testnet:
	NODE_TO_TEST="Node 37" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Gnosis_Testnet.py

test-base-testnet:
	PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

report-base-testnet:
	python report_Testnet_Base.py

test-base-node_01-testnet:
	NODE_TO_TEST="Node 01" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_04-testnet:
	NODE_TO_TEST="Node 04" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_05-testnet:
	NODE_TO_TEST="Node 05" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_06-testnet:
	NODE_TO_TEST="Node 06" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_07-testnet:
	NODE_TO_TEST="Node 07" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_08-testnet:
	NODE_TO_TEST="Node 08" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_09-testnet:
	NODE_TO_TEST="Node 09" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_10-testnet:
	NODE_TO_TEST="Node 10" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_13-testnet:
	NODE_TO_TEST="Node 13" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_14-testnet:
	NODE_TO_TEST="Node 14" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_21-testnet:
	NODE_TO_TEST="Node 21" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_23-testnet:
	NODE_TO_TEST="Node 23" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-base-node_37-testnet:
	NODE_TO_TEST="Node 37" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s tests/testnet/Base_Testnet.py

test-neuroweb-node25-mainnet:
	NODE_TO_TEST="Node 25" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html tests/mainnet/Neuroweb_Mainnet.py

test-neuroweb-node26-mainnet:
	NODE_TO_TEST="Node 26" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html tests/mainnet/Neuroweb_Mainnet.py

test-neuroweb-node27-mainnet:
	NODE_TO_TEST="Node 27" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html tests/mainnet/Neuroweb_Mainnet.py

test-neuroweb-node28-mainnet:
	NODE_TO_TEST="Node 28" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html tests/mainnet/Neuroweb_Mainnet.py

test-neuroweb-node29-mainnet:
	NODE_TO_TEST="Node 29" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html tests/mainnet/Neuroweb_Mainnet.py

test-neuroweb-node30-mainnet:
	NODE_TO_TEST="Node 30" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html tests/mainnet/Neuroweb_Mainnet.py

test-gnosis-node25-mainnet:
	NODE_TO_TEST="Node 25" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html tests/mainnet/Gnosis_Mainnet.py

test-gnosis-node26-mainnet:
	NODE_TO_TEST="Node 26" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html tests/mainnet/Gnosis_Mainnet.py

test-gnosis-node27-mainnet:
	NODE_TO_TEST="Node 27" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html tests/mainnet/Gnosis_Mainnet.py

test-gnosis-node28-mainnet:
	NODE_TO_TEST="Node 28" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html tests/mainnet/Gnosis_Mainnet.py

test-gnosis-node29-mainnet:
	NODE_TO_TEST="Node 29" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html tests/mainnet/Gnosis_Mainnet.py

test-gnosis-node30-mainnet:
	NODE_TO_TEST="Node 30" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html tests/mainnet/Gnosis_Mainnet.py

test-base-node25-mainnet:
	NODE_TO_TEST="Node 25" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html tests/mainnet/Base_Mainnet.py

test-base-node26-mainnet:
	NODE_TO_TEST="Node 26" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html tests/mainnet/Base_Mainnet.py

test-base-node27-mainnet:
	NODE_TO_TEST="Node 27" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html tests/mainnet/Base_Mainnet.py

test-base-node28-mainnet:
	NODE_TO_TEST="Node 28" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html tests/mainnet/Base_Mainnet.py

test-base-node29-mainnet:
	NODE_TO_TEST="Node 29" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html tests/mainnet/Base_Mainnet.py

test-base-node30-mainnet:
	NODE_TO_TEST="Node 30" PYTHONUNBUFFERED=1 PYTHONPATH=. poetry run python -u -m pytest -o log_cli=true -o log_cli_level=INFO -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html tests/mainnet/Base_Mainnet.py
