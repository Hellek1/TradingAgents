#!/usr/bin/env python3
"""
Simple test script to verify IBKR integration functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    # Test direct imports
    from tradingagents.dataflows.ibkr_utils import IBKRConnection
    print("✓ IBKR utils imported successfully")
    
    from tradingagents.dataflows.data_source_manager import DataSourceManager
    print("✓ Data source manager imported successfully")
    
    # Test configuration
    from tradingagents.default_config import DEFAULT_CONFIG
    print("✓ Configuration loaded successfully")
    
    # Check IBKR configuration
    print(f"Primary data source: {DEFAULT_CONFIG.get('data_source', 'not configured')}")
    print(f"Fallback enabled: {DEFAULT_CONFIG.get('enable_fallback', 'not configured')}")
    print(f"IBKR host: {DEFAULT_CONFIG.get('ibkr_host', 'not configured')}")
    print(f"IBKR port: {DEFAULT_CONFIG.get('ibkr_port', 'not configured')}")
    
    # Test creating connections (but don't actually connect)
    print("\nTesting connection creation...")
    ibkr_conn = IBKRConnection()
    print("✓ IBKR connection object created")
    
    data_manager = DataSourceManager()
    print("✓ Data source manager created")
    
    print("\nAll basic tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)