# pyrb - Python Rebalancer

![Python](https://img.shields.io/badge/Python-v3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Supported Brokerages](https://img.shields.io/badge/Supported%20Brokerages-EBest-orange)

`pyrb` is a command-line interface (CLI) tool for automating stock portfolio rebalancing. Built with Python, the tool fetches real-time stock prices and interacts with your brokerage API to place buy/sell orders for optimal asset allocation.

## Features

- Real-time stock price fetching via EBest API
- Portfolio analysis for asset allocation
- Order placement for portfolio rebalancing
- Supports multiple brokerages through a plug-and-play architecture
  - Currently supports for the EBest brokerage

## Installation

You can install `pyrb` directly from GitHub:

```bash
pip install git+https://github.com/yourusername/pyrb.git
```

Or, clone the repository and install manually:

```bash
git clone https://github.com/yourusername/pyrb.git
cd pyrb
pip install .
```

## Usage

First, set up your environment variables to configure EBest API keys:

```bash
export EBEST_APP_KEY="your_app_key_here"
export EBEST_APP_SECRET="your_app_secret_here"
```

Run the tool with:

```bash
pyrb rebalance --investment-amount 1000
```

This will fetch real-time prices and calculate optimal allocation for your portfolio with a total investment of ₩1000.

## Development

This project is built using Python 3.11 and Typer for the CLI interface. The project is specifically tailored for EBest but designed with a plug-and-play architecture to support additional brokerages in the future.

To set up a development environment, clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/pyrb.git
cd pyrb
poetry install --sync
```

### Running Tests

Run the test suite with:

```bash
pytest
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
