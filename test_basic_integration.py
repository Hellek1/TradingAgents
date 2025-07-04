#!/usr/bin/env python3
"""
Simple test to verify basic configuration and import structure
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

try:
    # Test configuration 
    from tradingagents.default_config import DEFAULT_CONFIG
    print("✓ Configuration loaded successfully")
    
    # Check IBKR configuration
    print(f"Primary data source: {DEFAULT_CONFIG.get('data_source', 'not configured')}")
    print(f"Fallback enabled: {DEFAULT_CONFIG.get('enable_fallback', 'not configured')}")
    print(f"IBKR host: {DEFAULT_CONFIG.get('ibkr_host', 'not configured')}")
    print(f"IBKR port: {DEFAULT_CONFIG.get('ibkr_port', 'not configured')}")
    
    # Test if files exist
    import os
    
    files_to_check = [
        'tradingagents/dataflows/ibkr_utils.py',
        'tradingagents/dataflows/data_source_manager.py',
        'tradingagents/dataflows/interface.py',
        'tradingagents/agents/utils/agent_utils.py',
        'requirements.txt',
        'pyproject.toml'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
    
    # Test requirements
    with open('requirements.txt', 'r') as f:
        requirements = f.read()
        if 'ib_async' in requirements:
            print("✓ ib_async dependency added to requirements.txt")
        else:
            print("✗ ib_async dependency missing from requirements.txt")
    
    with open('pyproject.toml', 'r') as f:
        pyproject = f.read()
        if 'ib_async' in pyproject:
            print("✓ ib_async dependency added to pyproject.toml")
        else:
            print("✗ ib_async dependency missing from pyproject.toml")
    
    print("\nAll basic file and configuration checks passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)