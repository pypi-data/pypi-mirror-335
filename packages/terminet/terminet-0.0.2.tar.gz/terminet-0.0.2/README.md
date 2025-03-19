# TermiNet

[![PyPI - Version](https://img.shields.io/pypi/v/terminet.svg)](https://pypi.org/project/terminet)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/terminet.svg)](https://pypi.org/project/terminet)

A terminal-based network monitoring tool built with Textual and Scapy.

<video controls src="terminet.mp4" title="Short video showcasing TermiNet"></video>

## Features

- **Real-time packet monitoring**: Capture and display network packets in a terminal-based interface
- **Protocol identification**: Automatically identify common protocols (TCP, UDP, ICMP, etc.)
- **Bandwidth visualization**: Monitor bandwidth usage with an integrated sparkline graph
- **Customizable interface**: Specify your network interface for targeted monitoring

## Table of Contents

- [Installation](#installation)
  - [Installation Best Practices](#installation-best-practices)
- [Usage](#usage)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Requirements](#requirements)
- [License](#license)

## Installation

### Installation Best Practices

To avoid potential dependency conflicts, it's recommended to install TermiNet using one of these methods:

#### Using pipx (Recommended)

[pipx](https://pypa.github.io/pipx/) installs applications in isolated environments:

```console
# Install pipx if you haven't already
python -m pip install --user pipx
python -m pipx ensurepath

# Install TermiNet
pipx install terminet
```

#### Using a Virtual Environment

```console
# Create a virtual environment
python -m venv terminet-env
# Linux/Unix: source terminet-env/bin/activate  
# On Windows: terminet-env\Scripts\activate

# Install TermiNet in the virtual environment
pip install terminet
```

### Standard Installation

If you prefer a standard installation (not recommended):

```console
pip install terminet
```

### From source

```console
git clone https://github.com/no-kris/terminet.git
cd terminet
pip install .
```

## Usage

After installation, you can run TermiNet with:

```console
terminet
```

### Basic Operation

1. Enter your network interface (e.g., `eth0`, `wlan0`) in the input field
2. Click "Start" to begin monitoring network traffic
3. The data table will populate with packet information
4. The sparkline graph will show bandwidth usage in KB/s
5. Click "Stop" to pause packet capturing
6. Click "Clear" to reset both the table and graph

## Keyboard Shortcuts

| Key      | Action                |
|----------|----------------------|
| ctrl+q   | Quit the application |
| d        | Toggle dark/light mode |

## Requirements

- Python 3.8+
- Dependencies:
  - textual>=2.1.2
  - scapy>=2.6.1


## License

`terminet` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
