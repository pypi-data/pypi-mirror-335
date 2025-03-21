# Yototec Market Python Client

A lightweight Python client to interact with the Yototec Market [REST API](https://market.yototec.com).

This library provides convenience methods for:

- Retrieving a time series of aggregated price data for a ticker between a date range.
- Retrieving the latest available aggregated price data for a ticker.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Initializing the Client](#initializing-the-client)
  - [Examples](#examples)
- [Supports](#supports)

## Features

- Historical Data
  - Fetch a time series of aggregated prices for a given ticker in a specified frequency (minute/hour/day), within a date range.
- Latest Data
  - Fetch the latest available aggregated price data for a given ticker.

## Requirements

- Python 3.8+ (recommend)
- [requests](https://pypi.org/project/requests/) library

## Installation

Since this is a standalone Python file, you can simply:
1. Clone or download this repository.
2. Ensure you have `requests` installed:
   ```bash
   pip install requests
   ```
3. Place `client.py` in your project, or install it as a local module.

## Usage

### Initializing the Client

```python
from yototec.client import Client

# If you have an API key:
api_key = "YOUR_YOTOTEC_API_KEY"

# Initialize the client with the default Yototec Market API URL
client = Client(api_key=api_key)

# Or override the base URL if needed:
# client = Client(base_url="https://some-other-domain.com", api_key=api_key)
```

### Examples

This is an example of how you might use this client:

```python
from yototec.client import Client

def main():
    # Replace with your real API key
    api_key = "YOUR_YOTOTEC_API_KEY"
    client = Client(api_key=api_key)

    # Example: Fetch hourly data for a ticker from 2025-01-01 to 2025-01-05
    sdate = "2025-01-01T00:00:00"
    edate = "2025-01-05T00:00:00"
    data = client.get_data(tic="BTCUSD", sdate=sdate, edate=edate, freq="hour")

    if data:
        print("Historical Data:", data)
    else:
        print("No data or an error occurred")

if __name__ == "__main__":
    main()
```

## Supports

Contributions, bug reports, and feature requests are welcome! Feel free to email us at info@yototec.com