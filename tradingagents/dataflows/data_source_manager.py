"""
Data source manager for handling multiple data sources with fallback logic.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from .config import get_config
from .finnhub_utils import get_data_in_range as get_finnhub_data_in_range
from .ibkr_utils import get_ibkr_data_in_range, cleanup_ibkr_connection

logger = logging.getLogger(__name__)


class DataSourceManager:
    """Manages data sources with fallback logic."""
    
    def __init__(self):
        self.config = get_config()
        self.primary_source = self.config.get("data_source", "finnhub")
        self.enable_fallback = self.config.get("enable_fallback", True)
    
    async def get_data_in_range(
        self, 
        ticker: str, 
        start_date: str, 
        end_date: str, 
        data_type: str, 
        data_dir: str = None,
        period: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get data from configured source with fallback.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            data_type: Type of data to fetch
            data_dir: Directory for local data (used by Finnhub)
            period: Period for data (used by Finnhub)
            **kwargs: Additional parameters
        
        Returns:
            Dict containing the requested data
        """
        primary_data = None
        primary_error = None
        
        # Try primary source first
        try:
            if self.primary_source == "ibkr":
                primary_data = await self._get_ibkr_data(
                    ticker, start_date, end_date, data_type, **kwargs
                )
            else:  # finnhub
                primary_data = self._get_finnhub_data(
                    ticker, start_date, end_date, data_type, data_dir, period
                )
            
            if primary_data:
                logger.info(f"Successfully fetched data from {self.primary_source}")
                return primary_data
        except Exception as e:
            primary_error = e
            logger.warning(f"Failed to fetch data from {self.primary_source}: {e}")
        
        # Try fallback if enabled and primary failed
        if self.enable_fallback and (not primary_data or primary_error):
            try:
                fallback_source = "finnhub" if self.primary_source == "ibkr" else "ibkr"
                logger.info(f"Attempting fallback to {fallback_source}")
                
                if fallback_source == "ibkr":
                    fallback_data = await self._get_ibkr_data(
                        ticker, start_date, end_date, data_type, **kwargs
                    )
                else:  # finnhub
                    fallback_data = self._get_finnhub_data(
                        ticker, start_date, end_date, data_type, data_dir, period
                    )
                
                if fallback_data:
                    logger.info(f"Successfully fetched data from fallback source: {fallback_source}")
                    return fallback_data
            except Exception as e:
                logger.warning(f"Fallback also failed: {e}")
        
        # If both failed, raise the original error or return empty dict
        if primary_error:
            raise primary_error
        return {}
    
    async def _get_ibkr_data(
        self, 
        ticker: str, 
        start_date: str, 
        end_date: str, 
        data_type: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Get data from IBKR."""
        return await get_ibkr_data_in_range(
            ticker, start_date, end_date, data_type, **kwargs
        )
    
    def _get_finnhub_data(
        self, 
        ticker: str, 
        start_date: str, 
        end_date: str, 
        data_type: str, 
        data_dir: str = None, 
        period: str = None
    ) -> Dict[str, Any]:
        """Get data from Finnhub."""
        if data_dir is None:
            from .config import DATA_DIR
            data_dir = DATA_DIR
        
        return get_finnhub_data_in_range(
            ticker, start_date, end_date, data_type, data_dir, period
        )
    
    def cleanup(self):
        """Clean up resources."""
        try:
            cleanup_ibkr_connection()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")


# Global data source manager instance
_data_source_manager = None


def get_data_source_manager() -> DataSourceManager:
    """Get or create data source manager instance."""
    global _data_source_manager
    if _data_source_manager is None:
        _data_source_manager = DataSourceManager()
    return _data_source_manager


def get_data_in_range_with_fallback(
    ticker: str, 
    start_date: str, 
    end_date: str, 
    data_type: str, 
    data_dir: str = None,
    period: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Synchronous wrapper for get_data_in_range with fallback logic.
    """
    manager = get_data_source_manager()
    
    # Run the async function
    loop = None
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(
            manager.get_data_in_range(
                ticker, start_date, end_date, data_type, data_dir, period, **kwargs
            )
        )
    finally:
        # Don't close the loop if it was already running
        if loop.is_running():
            pass
        else:
            try:
                loop.close()
            except:
                pass


def cleanup_data_sources():
    """Clean up all data source resources."""
    global _data_source_manager
    if _data_source_manager:
        _data_source_manager.cleanup()
        _data_source_manager = None