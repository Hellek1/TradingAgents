#!/usr/bin/env python3
"""
Example script demonstrating IBKR integration in TradingAgents.

This script shows how to configure and use the IBKR data source
with fallback to FinnHub.

Prerequisites:
- Interactive Brokers TWS or Gateway running with API enabled
- Configure the connection settings below
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.dataflows.config import set_config
from tradingagents.dataflows import (
    get_finnhub_news,  # Will use IBKR if configured
    get_ibkr_real_time_data,  # IBKR-specific function
    get_ibkr_company_info,    # IBKR-specific function
    get_ibkr_historical_data  # IBKR-specific function
)


def configure_ibkr():
    """Configure TradingAgents to use IBKR as primary data source."""
    config = {
        # Set IBKR as primary data source
        "data_source": "ibkr",
        "enable_fallback": True,  # Fallback to FinnHub if IBKR fails
        
        # IBKR connection settings
        "ibkr_host": "127.0.0.1",
        "ibkr_port": 7497,  # Use 7496 for paper trading
        "ibkr_client_id": 1,
        "ibkr_timeout": 30,
    }
    
    set_config(config)
    print("✓ Configured to use IBKR as primary data source with FinnHub fallback")


def test_fallback_functionality(ticker="AAPL", date="2024-01-15"):
    """Test the fallback functionality for existing functions."""
    print(f"\n--- Testing Fallback Functionality for {ticker} ---")
    
    try:
        # This function will try IBKR first, then fallback to FinnHub if needed
        news_data = get_finnhub_news(ticker, date, 7)
        
        if news_data:
            print(f"✓ Successfully retrieved news data (length: {len(news_data)} chars)")
            print(f"Preview: {news_data[:200]}...")
        else:
            print("! No news data available")
            
    except Exception as e:
        print(f"✗ Error retrieving news data: {e}")


def test_ibkr_specific_functions(ticker="AAPL", date="2024-01-15"):
    """Test IBKR-specific functions."""
    print(f"\n--- Testing IBKR-Specific Functions for {ticker} ---")
    
    # Test real-time data
    try:
        print("Testing real-time data...")
        real_time_data = get_ibkr_real_time_data(ticker, date)
        
        if "Real-Time Market Data" in real_time_data:
            print("✓ Successfully retrieved real-time data")
            print(f"Preview: {real_time_data[:300]}...")
        else:
            print(f"! Real-time data response: {real_time_data}")
            
    except Exception as e:
        print(f"✗ Error retrieving real-time data: {e}")
    
    # Test company info
    try:
        print("\nTesting company information...")
        company_info = get_ibkr_company_info(ticker, date)
        
        if "Company Information" in company_info:
            print("✓ Successfully retrieved company information")
            print(f"Preview: {company_info[:300]}...")
        else:
            print(f"! Company info response: {company_info}")
            
    except Exception as e:
        print(f"✗ Error retrieving company info: {e}")
    
    # Test historical data
    try:
        print("\nTesting historical data...")
        historical_data = get_ibkr_historical_data(ticker, date, 5, "1 day")
        
        if "Historical Data" in historical_data:
            print("✓ Successfully retrieved historical data")
            print(f"Preview: {historical_data[:300]}...")
        else:
            print(f"! Historical data response: {historical_data}")
            
    except Exception as e:
        print(f"✗ Error retrieving historical data: {e}")


def main():
    """Main function to demonstrate IBKR integration."""
    print("TradingAgents IBKR Integration Example")
    print("=====================================")
    
    # Configure IBKR
    configure_ibkr()
    
    # Test with AAPL
    ticker = "AAPL"
    date = "2024-01-15"
    
    print(f"\nTesting with ticker: {ticker}, date: {date}")
    print("Note: If IBKR is not available, functions will fallback to FinnHub")
    
    # Test fallback functionality
    test_fallback_functionality(ticker, date)
    
    # Test IBKR-specific functions
    test_ibkr_specific_functions(ticker, date)
    
    print("\n--- Example Complete ---")
    print("\nNotes:")
    print("- If you see connection errors, ensure TWS/Gateway is running")
    print("- If you see 'No data available' messages, this is normal when IBKR is not connected")
    print("- The fallback to FinnHub should work for news data")
    print("- See IBKR_INTEGRATION.md for detailed setup instructions")


if __name__ == "__main__":
    main()