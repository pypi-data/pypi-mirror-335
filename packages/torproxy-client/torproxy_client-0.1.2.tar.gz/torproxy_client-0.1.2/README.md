![License](https://img.shields.io/badge/license-MIT-blue.svg)
[![PyPI version](https://badge.fury.io/py/torproxy-client.svg)](https://badge.fury.io/py/torproxy-client)
![Build Status](https://img.shields.io/github/workflow/status/mi8bi/torproxy/Publish%20to%20PyPI/main)
![Python Version](https://img.shields.io/badge/python-3.12-blue)

# TorProxy-Client

**TorProxy-Client** is a simple Python library to connect to the internet through the Tor network using a proxy. It helps developers easily route their traffic through the Tor network to achieve better anonymity.

## Features

- Connect to the internet through Tor's SOCKS5 proxy
- Easy integration with Python applications
- Configurable proxy settings
- Support for both local and remote Tor nodes

## Prerequisites

Before using **TorProxy-Client**, you need to have **Tor** installed on your system. Below are the installation instructions for different platforms:

### Windows

1. Install [Scoop](https://scoop.sh/) if you haven't already.
2. Install Tor using the following command:

   ```bash
   scoop install tor
   ```

Alternatively, you can download the official Tor Browser from the Tor Project website, which will also install the Tor service.

3. Ensure that the Tor service is running by checking that the Tor process is active in the task manager or using tor.exe.

### macOS

1. Install Homebrew if you haven't already.

2. Install Tor using the following command:

``` bash
brew install tor
```

3. Start Tor with the following command:

``` bash
tor
```

4. Ensure the Tor service is running by checking for the process using ps aux | grep tor

### Linux
For most Linux distributions, you can install Tor via the package manager.

#### Ubuntu/Debian

1. Update your package list and install Tor:

``` bash
sudo apt update
sudo apt install tor
```

2. Start the Tor service:

```
sudo systemctl start tor
```

3. Enable Tor to start on boot:

```
sudo systemctl enable tor
```

Fedora

1. Install Tor using the following command:

``` bash
sudo dnf install tor
```

2. Start the Tor service:

```bash 
sudo systemctl start tor
```

3. Enable Tor to start on boot:

```
sudo systemctl enable tor
```

#### Arch Linux

1. Install Tor using the following command:

``` bash
sudo pacman -S tor
```

2. Start the Tor service:

```bash
sudo systemctl start tor
```

3. Enable Tor to start on boot:

```bash
sudo systemctl enable tor
```

## Installation

To install **TorProxy-Client**, use `pip`:

```bash
pip install torproxy_client
```

## Usage
Once installed, you can use TorProxy-Client to configure your application to route traffic through the Tor network.

```python
from torproxy_client import TorProxyClient
import requests

# Initialize the Tor proxy client
proxy = TorProxyClient()

# Check if Tor connection is successful
if proxy.tor_initialize():
    print("Tor connection successful!")
else:
    print("Tor connection failed. Please check if the Tor service is running.")

# Request via Tor
url = "https://check.torproject.org"
response = requests.get(url)
print(response.text)
```

## Dependencies
- [PySocks](https://github.com/Anorov/PySocks) (BSD License)
- [certifi](https://github.com/certifi/python-certifi) (Mozilla Public License 2.0)
- [charset-normalizer](https://github.com/Ousret/charset_normalizer) (MIT License)
- [idna](https://github.com/kjd/idna) (BSD License)
- [requests](https://docs.python-requests.org/en/latest/) (Apache 2.0)
- [stem](https://stem.torproject.org/) (LGPLv3)
- [urllib3](https://github.com/urllib3/urllib3) (MIT License)