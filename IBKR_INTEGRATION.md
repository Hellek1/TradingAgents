# IBKR Integration Documentation

This document explains how to use the Interactive Brokers (IBKR) integration in TradingAgents.

## Overview

The IBKR integration provides access to real-time market data, historical data, company information, and fundamental data through Interactive Brokers' TWS (Trader Workstation) or Gateway API. The integration includes fallback functionality to use Finnhub when IBKR is unavailable.

## Configuration

### Default Configuration

The following configuration options are available in `tradingagents/default_config.py`:

```python
# Data source settings
"data_source": "finnhub",  # Options: "finnhub", "ibkr"
"enable_fallback": True,   # Whether to fallback to finnhub when ibkr fails

# IBKR settings
"ibkr_host": "127.0.0.1",
"ibkr_port": 7497,         # TWS port (7497 for live, 7496 for paper)
"ibkr_client_id": 1,
"ibkr_timeout": 30,
```

### Setting up IBKR

1. **Install TWS or Gateway**: Download and install Interactive Brokers' Trader Workstation (TWS) or Gateway from their website.

2. **Enable API Access**: In TWS/Gateway:
   - Go to Configure → API → Settings
   - Enable "Enable ActiveX and Socket Clients"
   - Set the socket port (default: 7497 for live, 7496 for paper trading)
   - Add the client ID to the trusted list

3. **Configure TradingAgents**: 
   - Set `data_source` to `"ibkr"` to use IBKR as the primary data source
   - Adjust `ibkr_host`, `ibkr_port`, and `ibkr_client_id` as needed

## Available Functions

### Standard Functions (with fallback)

These functions will use IBKR when configured as primary source, with fallback to Finnhub:

- `get_finnhub_news()` - Gets news data
- `get_finnhub_company_insider_sentiment()` - Gets insider sentiment
- `get_finnhub_company_insider_transactions()` - Gets insider transactions

### IBKR-Specific Functions

These functions provide data that's only available through IBKR:

#### Real-Time Market Data
```python
get_ibkr_real_time_data(ticker, curr_date)
```
Returns real-time bid/ask, volume, and price data.

#### Company Information
```python
get_ibkr_company_info(ticker, curr_date)
```
Returns detailed company information including exchange, industry, trading hours, etc.

#### Historical Data
```python
get_ibkr_historical_data(ticker, curr_date, look_back_days, bar_size="1 day")
```
Returns historical OHLCV data with customizable bar sizes (1 day, 1 hour, 5 mins, etc.).

#### Fundamental Data
```python
get_ibkr_fundamentals(ticker, curr_date)
```
Returns fundamental data including financial statements and ratios.

## Agent Tools

The following tools are available in the `Toolkit` class for agents:

- `get_ibkr_real_time_data`
- `get_ibkr_company_info`
- `get_ibkr_historical_data`
- `get_ibkr_fundamentals`

## Error Handling

The integration includes several error handling mechanisms:

1. **Connection Errors**: If IBKR is not available, functions will fallback to Finnhub (if enabled)
2. **Timeout Handling**: Requests have configurable timeouts to prevent hanging
3. **Graceful Degradation**: Failed requests return empty results rather than crashing
4. **Resource Cleanup**: Connections are properly closed when the application exits

## Example Usage

```python
from tradingagents.dataflows import get_ibkr_real_time_data, get_ibkr_company_info

# Get real-time data
real_time_data = get_ibkr_real_time_data("AAPL", "2024-01-15")

# Get company information
company_info = get_ibkr_company_info("AAPL", "2024-01-15")

# Get historical data with different bar sizes
historical_data = get_ibkr_historical_data("AAPL", "2024-01-15", 30, "1 hour")
```

## Troubleshooting

### Common Issues

1. **Connection Failed**: Ensure TWS/Gateway is running and API access is enabled
2. **Port Issues**: Check that the port configuration matches TWS/Gateway settings
3. **Client ID Conflicts**: Use a unique client ID if multiple applications are connecting
4. **Data Permissions**: Ensure your IBKR account has permissions for the requested data

### Debug Mode

Enable debug logging to see detailed connection and request information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dependencies

The IBKR integration requires the following additional dependency:

- `ib_async>=2.0.0` - Python wrapper for Interactive Brokers API

This dependency is automatically included in the project requirements.

## Limitations

- Requires active IBKR account with API access
- Real-time data subject to IBKR data permissions
- Historical data requests are rate-limited by IBKR
- Some fundamental data may require premium subscriptions