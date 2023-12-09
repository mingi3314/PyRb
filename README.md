# pyrb - Python Rebalancer

![Python](https://img.shields.io/badge/Python-v3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Supported Brokerages](https://img.shields.io/badge/Supported%20Brokerages-EBest-orange)

`pyrb` is a command-line interface (CLI) tool for automating stock portfolio rebalancing. Built with Python, the tool fetches real-time stock prices and interacts with your brokerage API to place buy/sell orders for optimal asset allocation.

## Features

- Portfolio analysis for asset allocation
- Order placement for portfolio rebalancing
- Supports multiple brokerages through a plug-and-play architecture
  - Currently supports for the EBest brokerage

## Installation

You can install `pyrb` directly from GitHub:

- Pip

  ```bash
  pip install git+https://github.com/mingi3314/pyrb.git
  ```

- Poetry

  ```bash
  poetry add git+https://github.com/mingi3314/pyrb.git
  ```

Or, clone the repository and install manually:

```bash
git clone https://github.com/mingi3314/pyrb.git
cd pyrb
pip install .
```

## Usage

### 1. Set your account

First, set up your account of a brokerage.

```bash
pyrb account set
```

Then, the system would request you to enter the app key and app secret.

```bash
>>> App key: <enter your app key>
>>> App secret: <enter your app secret>
```

### 2. Rebalance your portfolio

For example, you can rebalance your portfolio according to the All-weather asset allocation strategy.

```bash
pyrb asset-allocate --strategy all-weather-kr --investment-amount <amount-you-want-to-invest>
```

Then the system would try to get confirmation from the user about the submition of orders to rebalance.

```bash
┏━━━━━━━━┳━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Symbol ┃ Side ┃ Quantity ┃ Price ┃ Total Amount ┃ Current position value ┃ Expected position value ┃
┡━━━━━━━━╇━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 379800 │ BUY  │ 378      │ 13545 │ 5120010      │ 1868930.0              │ 6988940.0               │
│ 361580 │ BUY  │ 278      │ 18265 │ 5077670      │ 1917538.0              │ 6995208.0               │
│ 411060 │ BUY  │ 370      │ 12200 │ 4514000      │ 1475979.0              │ 5989979.0               │
│ 365780 │ BUY  │ 58       │ 88755 │ 5147790      │ 1774834.0              │ 6922624.0               │
│ 308620 │ BUY  │ 476      │ 10945 │ 5209820      │ 1783768.0              │ 6993588.0               │
│ 272580 │ BUY  │ 85       │ 52995 │ 4504575      │ 1483638.0              │ 5988213.0               │
└────────┴──────┴──────────┴───────┴──────────────┴────────────────────────┴─────────────────────────┘

Do you want to place these orders? [y/N]: 
```

### 3. Check your portfolio

you can check your portfolio with the following command:

```bash
pyrb portfolio
```

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
