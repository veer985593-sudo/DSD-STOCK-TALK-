# Stock Research Assistant - Copilot Instructions

## Project Overview

This is a CrewAI multi-agent stock research assistant for the **Indian equity market** (NSE/BSE). It uses 6 AI agents orchestrated sequentially to produce investment research reports. There are 3 interfaces: Streamlit web UI, Telegram bot, and CLI.

**Tech stack:** Python 3.11+, CrewAI, Mistral AI (via LiteLLM), yfinance, nsetools, httpx, BeautifulSoup, Streamlit, python-telegram-bot v21+, fpdf2, python-docx.

**Package manager:** uv (not pip). Use `uv sync` to install, `uv run` to execute.

## Project Structure

```
agents/              # 6 CrewAI agents (singletons created at import time)
  market_data_agent.py, news_agent.py, fundamental_agent.py,
  technical_agent.py, strategist_agent.py, report_agent.py
tools/               # CrewAI @tool functions (return JSON strings)
  market_data.py     # yfinance: prices, info, historical, indices
  analysis.py        # Technical indicators + fundamental metrics
  news_scraper.py    # RSS feeds (ET, Google News) + HTML scraping
  institutional.py   # NSE API: FII/DII, bulk/block deals, holdings
crews/
  research_crew.py   # Sequential crew orchestration + Mistral patch
bot/
  telegram_bot.py    # Async Telegram bot with commands + callbacks
tests/               # pytest, 384+ tests, 89% coverage
app.py               # Streamlit dashboard (~994 lines, 5 tabs)
config.py            # Pydantic settings + market constants + thresholds
run_analysis.py      # CLI entry point
run_bot.py           # Telegram bot entry point
```

## Code Conventions

### Tool Functions (tools/)

- **Always return JSON strings** — `json.dumps(result)`, never raw dicts
- Use `_safe_json_dumps()` for data with potential NaN/Infinity values
- Symbol normalization: append `.NS` for yfinance (e.g., `RELIANCE` → `RELIANCE.NS`)
- Error responses **must** include: `{"error": "...", "DATA_UNAVAILABLE": True, "message": "Do NOT guess."}`
- Use specific exception types, never bare `except:`
- Tools never raise exceptions to CrewAI — they catch and return JSON error objects

### Caching

- Thread-safe LRU caches using `OrderedDict` + `threading.Lock`
- Market data: 200 max entries, 15-min TTL (in `tools/market_data.py`)
- News: 100 max entries, 10-min TTL (in `tools/news_scraper.py`)
- Do NOT use `functools.lru_cache` (not thread-safe, no TTL support)

### Agent Configuration (agents/)

- Each file has a `create_*_agent()` function + module-level singleton
- Agent temperatures: 0.3-0.4 (low, for factual accuracy)
- Every agent backstory contains: "only report data returned by your tools"
- LLM: `mistral/mistral-large-latest` via LiteLLM
- Report agent has mandatory price verification step before writing

### Testing (tests/)

- Framework: pytest with markers (`unit`, `integration`, `slow`, `critical`)
- **All external APIs must be mocked** — yfinance, httpx, nsetools, NSE API
- Streamlit mocking: `sys.modules['streamlit'] = MagicMock()` + `importlib.reload()`
- Telegram bot: `AsyncMock` for async handlers
- `# pragma: no cover` only on `if __name__ == "__main__"` blocks
- Run: `uv run pytest tests/ -v --tb=short`

### Report Generation (in app.py)

- PDF: fpdf2, Helvetica font (latin-1 only) — Unicode must be sanitized (₹→Rs., —→--)
- DOCX: python-docx, Calibri font, tables with XML borders
- Both output to `BytesIO` for Streamlit download

## Critical Rules

### Anti-Hallucination (DO NOT VIOLATE)

1. Tool error responses must always include `"DATA_UNAVAILABLE": True` and `"Do NOT guess"`
2. Agent prompts must include "only report data returned by your tools" — never remove
3. Report agent STEP 1: must call `get_stock_price` to verify current price before writing
4. Keep agent temperatures at 0.3-0.4 — never set above 0.5
5. Only reference indicators tools actually compute: RSI, MACD, Bollinger, SMA (20/50/200), EMA (12/26), ATR, standard daily pivots, ROC
6. Do NOT add to prompts: Stochastic, ADX, OBV, Fibonacci, candlestick patterns, DCF, sector averages, F&O data

### Data Sources

| Source | Status | Notes |
|--------|--------|-------|
| yfinance | Working | Append `.NS` for NSE symbols |
| nsetools | Working | Fallback to yfinance on failure |
| NSE API (FII/DII, deals) | Working | Requires `_get_nse_session()` for cookies |
| ET RSS feed | Working | Primary news source |
| Google News RSS | Working | Backup news source |
| ET HTML scraping | Working | Secondary news source |
| Moneycontrol | BLOCKED (403) | Do not restore |
| Business Standard | BLOCKED (403) | Do not restore |

### Indian Market Context

- All stocks are NSE/BSE listed — use NSE symbols (RELIANCE, TCS, INFY, etc.)
- NIFTY50 stock list and 10 sector mappings defined in `config.py`
- Number formatting: Indian system — lakhs (L) for 100K+, crores (Cr) for 10M+
- Currency: INR (₹), not USD
- Pivot points: standard daily formula `(prevH + prevL + prevC) / 3`
- Technical thresholds in `config.py:TECHNICAL_CONFIG`
- Fundamental thresholds in `config.py:FUNDAMENTAL_THRESHOLDS`

## Architecture Notes

- Crew runs **sequentially** (Process.sequential) — later agents need earlier context
- Async wrapper: `asyncio.to_thread()` wraps sync CrewAI for Streamlit/Telegram
- Mistral response format patched in `crews/research_crew.py` (list-of-blocks → string)
- NSE API requires session cookies — `_get_nse_session()` visits homepage first
- News aggregator (`get_stock_news`) deduplicates across 3 sources by title

## Environment Variables

```
MISTRAL_API_KEY          # Required for AI analysis
TELEGRAM_BOT_TOKEN       # For Telegram bot only
TELEGRAM_ADMIN_IDS       # Comma-separated admin IDs
CACHE_TTL_MINUTES=15     # Cache duration
LOG_LEVEL=INFO
CREWAI_TELEMETRY_OPT_OUT=true
OTEL_SDK_DISABLED=true
```
