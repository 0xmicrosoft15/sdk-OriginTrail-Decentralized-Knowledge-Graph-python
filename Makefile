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
	PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

report-neuroweb-testnet:
	python report_Testnet_Neuroweb.py

test-neuroweb-node_01-testnet:
	NODE_TO_TEST="Node 01" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_04-testnet:
	NODE_TO_TEST="Node 04" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_05-testnet:
	NODE_TO_TEST="Node 05" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_06-testnet:
	NODE_TO_TEST="Node 06" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_07-testnet:
	NODE_TO_TEST="Node 07" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_08-testnet:
	NODE_TO_TEST="Node 08" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_09-testnet:
	NODE_TO_TEST="Node 09" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_10-testnet:
	NODE_TO_TEST="Node 10" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_13-testnet:
	NODE_TO_TEST="Node 13" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_14-testnet:
	NODE_TO_TEST="Node 14" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_21-testnet:
	NODE_TO_TEST="Node 21" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_23-testnet:
	NODE_TO_TEST="Node 23" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-neuroweb-node_37-testnet:
	NODE_TO_TEST="Node 37" PYTHONPATH=. pytest tests/testnet/Neuroweb_Testnet.py -s

test-gnosis-testnet:
	PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

report-gnosis-testnet:
	python report_Testnet_Gnosis.py

test-gnosis-node_01-testnet:
	NODE_TO_TEST="Node 01" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_04-testnet:
	NODE_TO_TEST="Node 04" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_05-testnet:
	NODE_TO_TEST="Node 05" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_06-testnet:
	NODE_TO_TEST="Node 06" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_07-testnet:
	NODE_TO_TEST="Node 07" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_08-testnet:
	NODE_TO_TEST="Node 08" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_09-testnet:
	NODE_TO_TEST="Node 09" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_10-testnet:
	NODE_TO_TEST="Node 10" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_13-testnet:
	NODE_TO_TEST="Node 13" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_14-testnet:
	NODE_TO_TEST="Node 14" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_21-testnet:
	NODE_TO_TEST="Node 21" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_23-testnet:
	NODE_TO_TEST="Node 23" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-gnosis-node_37-testnet:
	NODE_TO_TEST="Node 37" PYTHONPATH=. pytest tests/testnet/Gnosis_Testnet.py -s

test-base-testnet:
	PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

report-base-testnet:
	python report_Testnet_Base.py

test-base-node_01-testnet:
	NODE_TO_TEST="Node 01" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_04-testnet:
	NODE_TO_TEST="Node 04" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_05-testnet:
	NODE_TO_TEST="Node 05" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_06-testnet:
	NODE_TO_TEST="Node 06" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_07-testnet:
	NODE_TO_TEST="Node 07" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_08-testnet:
	NODE_TO_TEST="Node 08" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_09-testnet:
	NODE_TO_TEST="Node 09" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_10-testnet:
	NODE_TO_TEST="Node 10" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_13-testnet:
	NODE_TO_TEST="Node 13" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_14-testnet:
	NODE_TO_TEST="Node 14" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_21-testnet:
	NODE_TO_TEST="Node 21" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_23-testnet:
	NODE_TO_TEST="Node 23" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-base-node_37-testnet:
	NODE_TO_TEST="Node 37" PYTHONPATH=. pytest tests/testnet/Base_Testnet.py -s

test-neuroweb-node25-mainnet:
	NODE_TO_TEST="Node 25" PYTHONPATH=. pytest tests/mainnet/Neuroweb_Mainnet.py -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html

test-neuroweb-node26-mainnet:
	NODE_TO_TEST="Node 26" PYTHONPATH=. pytest tests/mainnet/Neuroweb_Mainnet.py -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html

test-neuroweb-node27-mainnet:
	NODE_TO_TEST="Node 27" PYTHONPATH=. pytest tests/mainnet/Neuroweb_Mainnet.py -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html

test-neuroweb-node28-mainnet:
	NODE_TO_TEST="Node 28" PYTHONPATH=. pytest tests/mainnet/Neuroweb_Mainnet.py -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html

test-neuroweb-node29-mainnet:
	NODE_TO_TEST="Node 29" PYTHONPATH=. pytest tests/mainnet/Neuroweb_Mainnet.py -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html

test-neuroweb-node30-mainnet:
	NODE_TO_TEST="Node 30" PYTHONPATH=. pytest tests/mainnet/Neuroweb_Mainnet.py -s --json-report --json-report-file=.report/mainnet_neuroweb.json --html=.report/mainnet_neuroweb.html --self-contained-html

test-gnosis-node25-mainnet:
	NODE_TO_TEST="Node 25" PYTHONPATH=. pytest tests/mainnet/Gnosis_Mainnet.py -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html

test-gnosis-node26-mainnet:
	NODE_TO_TEST="Node 26" PYTHONPATH=. pytest tests/mainnet/Gnosis_Mainnet.py -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html

test-gnosis-node27-mainnet:
	NODE_TO_TEST="Node 27" PYTHONPATH=. pytest tests/mainnet/Gnosis_Mainnet.py -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html

test-gnosis-node28-mainnet:
	NODE_TO_TEST="Node 28" PYTHONPATH=. pytest tests/mainnet/Gnosis_Mainnet.py -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html

test-gnosis-node29-mainnet:
	NODE_TO_TEST="Node 29" PYTHONPATH=. pytest tests/mainnet/Gnosis_Mainnet.py -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html

test-gnosis-node30-mainnet:
	NODE_TO_TEST="Node 30" PYTHONPATH=. pytest tests/mainnet/Gnosis_Mainnet.py -s --json-report --json-report-file=.report/mainnet_gnosis.json --html=.report/mainnet_gnosis.html --self-contained-html

test-base-node25-mainnet:
	NODE_TO_TEST="Node 25" PYTHONPATH=. pytest tests/mainnet/Base_Mainnet.py -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html

test-base-node26-mainnet:
	NODE_TO_TEST="Node 26" PYTHONPATH=. pytest tests/mainnet/Base_Mainnet.py -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html

test-base-node27-mainnet:
	NODE_TO_TEST="Node 27" PYTHONPATH=. pytest tests/mainnet/Base_Mainnet.py -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html

test-base-node28-mainnet:
	NODE_TO_TEST="Node 28" PYTHONPATH=. pytest tests/mainnet/Base_Mainnet.py -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html

test-base-node29-mainnet:
	NODE_TO_TEST="Node 29" PYTHONPATH=. pytest tests/mainnet/Base_Mainnet.py -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html

test-base-node30-mainnet:
	NODE_TO_TEST="Node 30" PYTHONPATH=. pytest tests/mainnet/Base_Mainnet.py -s --json-report --json-report-file=.report/mainnet_base.json --html=.report/mainnet_base.html --self-contained-html