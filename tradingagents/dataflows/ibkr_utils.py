"""
IBKR (Interactive Brokers) data utilities using ib_async library.
"""

import asyncio
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from ib_async import IB, Stock, Contract, NewsArticle, util
from .config import get_config

# Configure logging
logger = logging.getLogger(__name__)


class IBKRConnection:
    """Manages IBKR connection and data retrieval."""
    
    def __init__(self):
        self.ib = IB()
        self.config = get_config()
        self.host = self.config.get("ibkr_host", "127.0.0.1")
        self.port = self.config.get("ibkr_port", 7497)
        self.client_id = self.config.get("ibkr_client_id", 1)
        self.timeout = self.config.get("ibkr_timeout", 30)
        self.connected = False
    
    async def connect(self):
        """Connect to IBKR TWS/Gateway."""
        try:
            await self.ib.connectAsync(
                host=self.host,
                port=self.port,
                clientId=self.client_id,
                timeout=self.timeout
            )
            self.connected = True
            logger.info(f"Connected to IBKR at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to IBKR: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from IBKR."""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IBKR")
    
    def get_contract(self, ticker: str, exchange: str = "SMART") -> Contract:
        """Get contract for a ticker."""
        return Stock(ticker, exchange, "USD")
    
    async def get_historical_data(
        self, 
        ticker: str, 
        duration: str = "1 Y", 
        bar_size: str = "1 day",
        what_to_show: str = "TRADES"
    ) -> pd.DataFrame:
        """Get historical market data."""
        if not self.connected:
            await self.connect()
        
        contract = self.get_contract(ticker)
        
        # Request historical data
        bars = await self.ib.reqHistoricalDataAsync(
            contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow=what_to_show,
            useRTH=True,
            formatDate=1
        )
        
        # Convert to DataFrame
        df = util.df(bars)
        return df
    
    async def get_news_articles(
        self, 
        ticker: str, 
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Get news articles for a ticker."""
        if not self.connected:
            await self.connect()
        
        contract = self.get_contract(ticker)
        
        # Get contract details to find news providers
        contract_details = await self.ib.reqContractDetailsAsync(contract)
        if not contract_details:
            return []
        
        # Request news articles
        news_articles = []
        try:
            # Get news providers for this contract
            providers = await self.ib.reqNewsProvidersAsync()
            if providers:
                # Use first available provider
                provider_code = providers[0].code
                
                # Request news articles
                articles = await self.ib.reqHistoricalNewsAsync(
                    conId=contract_details[0].contract.conId,
                    providerCodes=provider_code,
                    startDateTime=datetime.now() - timedelta(days=days_back),
                    endDateTime=datetime.now(),
                    totalResults=100
                )
                
                for article in articles:
                    news_articles.append({
                        'time': article.time,
                        'providerCode': article.providerCode,
                        'articleId': article.articleId,
                        'headline': article.headline
                    })
        except Exception as e:
            logger.warning(f"Failed to get news for {ticker}: {e}")
        
        return news_articles
    
    async def get_company_info(self, ticker: str) -> Dict[str, Any]:
        """Get company information."""
        if not self.connected:
            await self.connect()
        
        contract = self.get_contract(ticker)
        
        # Get contract details
        contract_details = await self.ib.reqContractDetailsAsync(contract)
        if not contract_details:
            return {}
        
        detail = contract_details[0]
        
        return {
            'symbol': detail.contract.symbol,
            'exchange': detail.contract.exchange,
            'currency': detail.contract.currency,
            'longName': detail.longName,
            'industry': detail.industry,
            'category': detail.category,
            'subcategory': detail.subcategory,
            'timeZoneId': detail.timeZoneId,
            'tradingHours': detail.tradingHours,
            'liquidHours': detail.liquidHours,
            'evRule': detail.evRule,
            'evMultiplier': detail.evMultiplier,
            'minTick': detail.minTick,
            'orderTypes': detail.orderTypes,
            'validExchanges': detail.validExchanges,
            'underConId': detail.underConId,
            'marketRuleIds': detail.marketRuleIds
        }
    
    async def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """Get fundamental data."""
        if not self.connected:
            await self.connect()
        
        contract = self.get_contract(ticker)
        
        try:
            # Get fundamental data
            fundamental_data = await self.ib.reqFundamentalDataAsync(
                contract, 
                'ReportSnapshot'  # Available types: ReportSnapshot, ReportsFinSummary, ReportRatios, ReportsFinStatements, RESC, CalendarReport
            )
            
            return {'fundamentals': fundamental_data}
        except Exception as e:
            logger.warning(f"Failed to get fundamentals for {ticker}: {e}")
            return {}
    
    async def get_real_time_data(self, ticker: str) -> Dict[str, Any]:
        """Get real-time market data."""
        if not self.connected:
            await self.connect()
        
        contract = self.get_contract(ticker)
        
        # Request market data
        self.ib.reqMktData(contract, '', False, False)
        
        # Wait for data to be received
        await asyncio.sleep(2)
        
        # Get the ticker data
        ticker_data = self.ib.ticker(contract)
        
        if ticker_data:
            return {
                'symbol': ticker_data.contract.symbol,
                'bid': ticker_data.bid,
                'ask': ticker_data.ask,
                'last': ticker_data.last,
                'lastSize': ticker_data.lastSize,
                'volume': ticker_data.volume,
                'high': ticker_data.high,
                'low': ticker_data.low,
                'close': ticker_data.close,
                'halted': ticker_data.halted,
                'bidSize': ticker_data.bidSize,
                'askSize': ticker_data.askSize,
                'time': ticker_data.time
            }
        
        return {}


# Global connection instance
_ibkr_connection = None


def get_ibkr_connection() -> IBKRConnection:
    """Get or create IBKR connection instance."""
    global _ibkr_connection
    if _ibkr_connection is None:
        _ibkr_connection = IBKRConnection()
    return _ibkr_connection


async def get_ibkr_data_in_range(
    ticker: str, 
    start_date: str, 
    end_date: str, 
    data_type: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get IBKR data within a date range.
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        data_type: Type of data (news, historical, fundamentals, etc.)
        **kwargs: Additional parameters
    
    Returns:
        Dict containing the requested data
    """
    conn = get_ibkr_connection()
    
    try:
        if data_type == "news":
            # Calculate days back from start_date to end_date
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            days_back = (end_dt - start_dt).days
            
            articles = await conn.get_news_articles(ticker, days_back)
            
            # Group by date
            grouped_data = {}
            for article in articles:
                date_str = article['time'].strftime("%Y-%m-%d")
                if start_date <= date_str <= end_date:
                    if date_str not in grouped_data:
                        grouped_data[date_str] = []
                    grouped_data[date_str].append(article)
            
            return grouped_data
        
        elif data_type == "historical":
            # Get historical data
            duration = kwargs.get('duration', '1 Y')
            bar_size = kwargs.get('bar_size', '1 day')
            what_to_show = kwargs.get('what_to_show', 'TRADES')
            
            df = await conn.get_historical_data(ticker, duration, bar_size, what_to_show)
            
            # Filter by date range
            if not df.empty:
                df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
                filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
                
                # Convert to dict grouped by date
                grouped_data = {}
                for _, row in filtered_df.iterrows():
                    date_str = row['date']
                    grouped_data[date_str] = row.to_dict()
                
                return grouped_data
            
            return {}
        
        elif data_type == "fundamentals":
            fundamental_data = await conn.get_fundamentals(ticker)
            return {end_date: fundamental_data} if fundamental_data else {}
        
        elif data_type == "company_info":
            company_info = await conn.get_company_info(ticker)
            return {end_date: company_info} if company_info else {}
        
        elif data_type == "real_time":
            real_time_data = await conn.get_real_time_data(ticker)
            return {end_date: real_time_data} if real_time_data else {}
        
        else:
            logger.warning(f"Unknown data type: {data_type}")
            return {}
    
    except Exception as e:
        logger.error(f"Error fetching IBKR data: {e}")
        raise


def cleanup_ibkr_connection():
    """Clean up IBKR connection."""
    global _ibkr_connection
    if _ibkr_connection:
        try:
            asyncio.run(_ibkr_connection.disconnect())
        except Exception as e:
            logger.warning(f"Error during IBKR cleanup: {e}")
        _ibkr_connection = None