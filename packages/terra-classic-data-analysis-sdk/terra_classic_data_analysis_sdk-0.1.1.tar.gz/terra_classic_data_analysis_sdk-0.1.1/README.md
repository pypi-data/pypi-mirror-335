<br/>
<br/>

<div  align="center"> <p > <img src="https://raw.githubusercontent.com/geoffmunn/terra.py/main/docs/img/logo.png" width=500 alt="py-sdk-logo"></p>

The Python SDK for Terra Classic
<br/>

<p><sub>(Unfamiliar with Terra?  <a href="https://docs.terra.money/">Check out the Terra Docs</a>)</sub></p>

  <p > <img alt="GitHub" src="https://img.shields.io/github/license/terra-money/terra-sdk-python">
<img alt="Python" src="https://img.shields.io/pypi/pyversions/terra-sdk">
  <img alt="pip" src="https://img.shields.io/pypi/v/terra-sdk"></p>
<p>
  <a href="https://terra-money.github.io/terra.py/index.html"><strong>Explore the Docs »</strong></a>
<br/>
  <a href="https://pypi.org/project/terra-classic-sdk/">PyPI Package</a>
  ·
  <a href="https://github.com/geoffmunn/terra.py">GitHub Repository</a>
</p></div>

The Terra Classic Software Development Kit (SDK) in Python is a simple library toolkit for building software that can interact with the Terra Classic blockchain and provides simple abstractions over core data structures, serialization, key management, and API request generation.

## Features

- Written in Python with extensive support libraries
- Versatile support for key management solutions
- Exposes the Terra Classic API through LCDClient
- Supports non-Terra Classic addresses for transactions
- IBC swaps between non-Terra Classic chains are partially supported (where IBC channels exist)
- Osmosis support (requires terra.proto 3.0.2 or newer)

## Recent changes

### 3.0.2
- Fixes for governance voting and other minor issues with the 0.47 chain upgrade

### 3.0.0
- Compatibility with terra.proto 4.0.0. This is backward compatible with terra.proto 3.1.2, but going forward will be built and tested against the newest version of the Cosmos SDK.

### 2.1.4
- Liquidity pool support added, you can now join and exit liquidity pools on Osmosis
 - This is specifically matched with terra.proto version 3.1.2 

### 2.1.3
- All packages have been upgraded to the latest version, except for betterproto which is already on a pre-release version.

### 2.1.2
- Governance voting and proposal analysis now works
- Governance APIs updated to version 1
- Documentation reviewed and updated

### 2.1.1
- Better Osmosis support. Pools can now be requested by pool ID, or the entire list can be requested.

### 2.1.0
- Osmosis support. This is just a simple exposure of the messages in terra.proto.

<br/>

# Table of Contents

- [API Reference](#api-reference)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Dependencies](#dependencies)
  - [Tests](#tests)
  - [Code Quality](#code-quality)
- [Usage Examples](#usage-examples)
  - [Getting Blockchain Information](#getting-blockchain-information)
    - [Async Usage](#async-usage)
  - [Building and Signing Transactions](#building-and-signing-transactions)
    - [Example Using a Wallet](#example-using-a-wallet-recommended)
- [Contributing](#contributing)
  - [Reporting an Issue](#reporting-an-issue)
  - [Requesting a Feature](#requesting-a-feature)
  - [Contributing Code](#contributing-code)
  - [Documentation Contributions](#documentation-contributions)
- [License](#license)

<br/>

# API Reference

An intricate reference to the APIs on the Terra SDK can be found <a href="https://terra-money.github.io/terra.py/index.html">here</a>.

<br/>

# Getting Started

A walk-through of the steps to get started with the Terra SDK alongside a few use case examples are provided below. Alternatively, a tutorial video is also available <a href="https://www.youtube.com/watch?v=GfasBlJHKIg">here</a> as reference.

## Requirements

Terra Classic SDK requires <a href="https://www.python.org/downloads/">Python v3.7+</a>.

## Installation

<sub>**NOTE:** _All code starting with a `$` is meant to run on your terminal (a bash prompt). All code starting with a `>>>` is meant to run in a python interpreter, like <a href="https://pypi.org/project/ipython/">ipython</a>._</sub>

Terra SDK can be installed (preferably in a `virtual environment` from PyPI using `pip`) as follows:

```
$ pip install -U terra-classic-sdk
```

<sub>_You might need to run pip via ```python -m pip install -U terra_classic_sdk```. Additionally, you might have `pip3` installed instead of `pip`; proceed according to your own setup._<sub>

## Dependencies

Terra Classic SDK uses <a href="https://python-poetry.org/">Poetry</a> to manage dependencies. To get set up with all the required dependencies, run:

```
$ pip install poetry
$ poetry install
```

## Tests

Terra Classic SDK provides extensive tests for data classes and functions. To run them, after the steps in [Dependencies](#dependencies):

```
$ make test
```

## Code Quality

Terra Classic SDK uses <a href="https://black.readthedocs.io/en/stable/">Black</a>, <a href="https://isort.readthedocs.io/en/latest/">isort</a>, and <a href="https://mypy.readthedocs.io/en/stable/index.html">Mypy</a> for checking code quality and maintaining style. To reformat, after the steps in [Dependencies](#dependencies):

```
$ make qa && make format
```

<br/>

# Usage Examples

Terra Classic SDK can help you read block data, sign and send transactions, deploy and interact with contracts, and many more.
The following examples are provided to help you get started. Use cases and functionalities of the Terra Classic SDK are not limited to the following examples and can be found in full <a href="https://github.com/geoffmunn/utility-scripts/">here</a>.

In order to interact with the Terra Classic blockchain, you'll need a connection to a Terra Classic node. This can be done through setting up an LCDClient (The LCDClient is an object representing an HTTP connection to a Terra Classic LCD node.):

```python
>>> from terra_classic_sdk.client.lcd import LCDClient
>>> terra = LCDClient(chain_id="columbus-5", url="https://terra-classic-lcd.publicnode.com")
```

## Getting Blockchain Information

Once properly configured, the `LCDClient` instance will allow you to interact with the Terra Classic blockchain. Try getting the latest block height:

```python
>>> terra.tendermint.block_info()['block']['header']['height']
```

`'1687543'`

### Async Usage

If you want to make asynchronous, non-blocking LCD requests, you can use AsyncLCDClient. The interface is similar to LCDClient, except the module and wallet API functions must be awaited.

```python
>>> import asyncio 
>>> from terra_classic_sdk.client.lcd import AsyncLCDClient

>>> async def main():
      terra = AsyncLCDClient("https://terra-classic-lcd.publicnode.com", "columbus-5")
      total_supply = await terra.bank.total()
      print(total_supply)
      await terra.session.close # you must close the session

>>> asyncio.get_event_loop().run_until_complete(main())
```

## Building and Signing Transactions

If you wish to perform a state-changing operation on the Terra Classic blockchain such as sending tokens, swapping assets, withdrawing rewards, or even invoking functions on smart contracts, you must create a **transaction** and broadcast it to the network.
Terra Classic SDK provides functions that help create StdTx objects.

### Example Using a Wallet (_recommended_)

A `Wallet` allows you to create and sign a transaction in a single step by automatically fetching the latest information from the blockchain (chain ID, account number, sequence).

Use `LCDClient.wallet()` to create a Wallet from any Key instance. The Key provided should correspond to the account you intend to sign the transaction with.
  
<sub>**NOTE:** *If you are using MacOS and got an exception 'bad key length' from MnemonicKey, please check your python implementation. if `python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"` returns LibreSSL 2.8.3, you need to reinstall python via pyenv or homebrew.*</sub>

```python
>>> from terra_classic_sdk.client.lcd import LCDClient
>>> from terra_classic_sdk.key.mnemonic import MnemonicKey

>>> mk = MnemonicKey(mnemonic=MNEMONIC)
>>> terra = LCDClient("https://terra-classic-lcd.publicnode.com", "columbus-5")
>>> wallet = terra.wallet(mk)
```

Once you have your Wallet, you can simply create a StdTx using `Wallet.create_and_sign_tx`.

```python
>>> from terra_classic_sdk.core.fee import Fee
>>> from terra_classic_sdk.core.bank import MsgSend
>>> from terra_classic_sdk.client.lcd.api.tx import CreateTxOptions

>>> tx = wallet.create_and_sign_tx(CreateTxOptions(
        msgs=[MsgSend(
            wallet.key.acc_address,
            RECIPIENT,
            "1000000uluna"    # send 1 luna
        )],
        memo="test transaction!",
        fee=Fee(200000, "120000uluna")
    ))
```

You should now be able to broadcast your transaction to the network.

```python
>>> result = terra.tx.broadcast(tx)
>>> print(result)
```

<br/>

# Contributing

Community contribution, whether it's a new feature, correction, bug report, additional documentation, or any other feedback is always welcome. Please read through this section to ensure that your contribution is in the most suitable format for us to effectively process.

<br/>

## Reporting an Issue

First things first: **Do NOT report security vulnerabilities in public issues!** Please disclose responsibly by submitting your findings to the [Terra Bugcrowd submission form](https://www.terra.money/bugcrowd). The issue will be assessed as soon as possible.
If you encounter a different issue with the Python SDK, check first to see if there is an existing issue on the <a href="https://github.com/terra-money/terra-sdk-python/issues">Issues</a> page, or if there is a pull request on the <a href="https://github.com/terra-money/terra-sdk-python/pulls">Pull requests</a> page. Be sure to check both the Open and Closed tabs addressing the issue.

If there isn't a discussion on the topic there, you can file an issue. The ideal report includes:

- A description of the problem / suggestion.
- How to recreate the bug.
- If relevant, including the versions of your:
  - Python interpreter
  - Terra SDK
  - Optionally of the other dependencies involved
- If possible, create a pull request with a (failing) test case demonstrating what's wrong. This makes the process for fixing bugs quicker & gets issues resolved sooner.
  </br>

## Requesting a Feature

If you wish to request the addition of a feature, please first check out the <a href="https://github.com/terra-money/terra-sdk-python/issues">Issues</a> page and the <a href="https://github.com/terra-money/terra-sdk-python/pulls">Pull requests</a> page (both Open and Closed tabs). If you decide to continue with the request, think of the merits of the feature to convince the project's developers, and provide as much detail and context as possible in the form of filing an issue on the <a href="https://github.com/terra-money/terra-sdk-python/issues">Issues</a> page.

<br/>

## Contributing Code

If you wish to contribute to the repository in the form of patches, improvements, new features, etc., first scale the contribution. If it is a major development, like implementing a feature, it is recommended that you consult with the developers of the project before starting the development to avoid duplicating efforts. Once confirmed, you are welcome to submit your pull request.
</br>

### For new contributors, here is a quick guide:

1. Fork the repository.
2. Build the project using the [Dependencies](#dependencies) and [Tests](#tests) steps.
3. Install a <a href="https://virtualenv.pypa.io/en/latest/index.html">virtualenv</a>.
4. Develop your code and test the changes using the [Tests](#tests) and [Code Quality](#code-quality) steps.
5. Commit your changes (ideally follow the <a href="https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit">Angular commit message guidelines</a>).
6. Push your fork and submit a pull request to the repository's `main` branch to propose your code.

A good pull request:

- Is clear and concise.
- Works across all supported versions of Python. (3.7+)
- Follows the existing style of the code base (<a href="https://pypi.org/project/flake8/">`Flake8`</a>).
- Has comments included as needed.
- Includes a test case that demonstrates the previous flaw that now passes with the included patch, or demonstrates the newly added feature.
- Must include documentation for changing or adding any public APIs.
- Must be appropriately licensed (MIT License).
  </br>

## Documentation Contributions

Documentation improvements are always welcome. The documentation files live in the [docs](./docs) directory of the repository and are written in <a href="https://docutils.sourceforge.io/rst.html">reStructuredText</a> and use <a href="https://www.sphinx-doc.org/en/master/">Sphinx</a> to create the full suite of documentation.
</br>
When contributing documentation, please do your best to follow the style of the documentation files. This means a soft limit of 88 characters wide in your text files and a semi-formal, yet friendly and approachable, prose style. You can propose your improvements by submitting a pull request as explained above.

### Need more information on how to contribute?

You can give this <a href="https://opensource.guide/how-to-contribute/#how-to-submit-a-contribution">guide</a> read for more insight.

<br/>

# License

This software is licensed under the MIT license. See [LICENSE](./LICENSE) for full disclosure.

© 2021 Terraform Labs, PTE.

<hr/>

<p>&nbsp;</p>
<p align="center">
    <a href="https://terra.money/"><img src="https://assets.website-files.com/611153e7af981472d8da199c/61794f2b6b1c7a1cb9444489_symbol-terra-blue.svg" alt="Terra-logo" width=200/></a>
<div align="center">
  <sub><em>Powering the innovation of money.</em></sub>
</div>
