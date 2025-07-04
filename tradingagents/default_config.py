import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
    # Data source settings
    "data_source": "finnhub",  # Options: "finnhub", "ibkr"
    "enable_fallback": True,  # Whether to fallback to finnhub when ibkr fails
    # IBKR settings
    "ibkr_host": "127.0.0.1",
    "ibkr_port": 7497,  # TWS port (7497 for live, 7496 for paper)
    "ibkr_client_id": 1,
    "ibkr_timeout": 30,
}
