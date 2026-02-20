# Stock Research Assistant

AI-powered multi-agent stock research tool for the Indian equity market (NSE/BSE).

## Quick Reference

- **Framework:** CrewAI (6 agents, sequential process) + Mistral AI via LiteLLM
- **Interfaces:** Streamlit web UI (`app.py`), Telegram bot (`bot/telegram_bot.py`), CLI (`run_analysis.py`)
- **Package manager:** uv (use `uv sync` to install, `uv run` to execute)
- **Python:** 3.11+
- **Config:** pydantic-settings in `config.py`, env vars from `.env`

## Project Structure

```
agents/          # 6 CrewAI agents (market_data, news, fundamental, technical, strategist, report)
tools/           # @tool decorated functions returning JSON strings
  market_data.py   # yfinance: prices, info, historical, indices, NSE quotes
  analysis.py      # Technical indicators (RSI, MACD, Bollinger, pivots) + fundamentals
  news_scraper.py  # RSS (ET, Google News) + HTML scraping (Economic Times)
  institutional.py # NSE API: FII/DII flows, bulk/block deals, holdings
crews/           # research_crew.py - sequential task orchestration
bot/             # telegram_bot.py - async Telegram bot (python-telegram-bot v21+)
tests/           # pytest suite, 384+ tests, 89% coverage
app.py           # Streamlit dashboard (~994 lines, 5 tabs)
config.py        # Settings, market constants, thresholds
run_analysis.py  # CLI entry point
run_bot.py       # Telegram bot entry point
```

## Commands

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v --tb=short

# Run tests with coverage
uv run pytest tests/ -v --tb=short --cov=tools --cov=agents --cov=config --cov=crews --cov-report=term

# Run only unit tests (fast)
uv run pytest tests/ -m unit -v

# Run Streamlit app
uv run streamlit run app.py

# Run CLI analysis
uv run python run_analysis.py RELIANCE
uv run python run_analysis.py TCS --quick
uv run python run_analysis.py INFY --type technical-only

# Run Telegram bot
uv run python run_bot.py
```

## Architecture

### Agent Pipeline (Sequential)

```
Task 1: market_data_agent    → price, volume, company info
Task 2: news_analyst_agent   → news from 3 sources, sentiment
Task 3: fundamental_agent    → P/E, P/B, ROE, debt, holdings (context: Task 1)
Task 4: technical_agent      → RSI, MACD, Bollinger, pivots (context: Task 1)
Task 5: strategist_agent     → BUY/HOLD/SELL recommendation (context: Tasks 2-4)
Task 6: report_agent         → professional markdown report (context: all tasks)
```

### Key Data Flow

- All tools return **JSON strings** (CrewAI requirement)
- Error responses include `"DATA_UNAVAILABLE": True` and `"Do NOT guess"` message
- Crew runs synchronously; async wrapper (`asyncio.to_thread`) used in bot/Streamlit
- Mistral returns list-of-blocks format; patched in `crews/research_crew.py` (lines 16-33)

## Coding Conventions

### Tool Functions

- Decorated with `@tool` from crewai_tools
- Always return `json.dumps(...)` — never raw dicts
- Use `_safe_json_dumps()` for data with potential NaN/Infinity (technical indicators)
- Symbol normalization: `_get_nse_symbol("RELIANCE")` → `"RELIANCE.NS"` for yfinance
- Every error path must include `DATA_UNAVAILABLE: True` flag

### Caching

- Thread-safe LRU using `OrderedDict` + `threading.Lock`
- Market data cache: 200 entries, 15-min TTL (`tools/market_data.py`)
- News cache: 100 entries, 10-min TTL (`tools/news_scraper.py`)
- Do NOT use functools.lru_cache (not thread-safe, no TTL)

### Agent Configuration

- Temperatures: 0.3 (market_data, technical, report) to 0.4 (news, fundamental, strategist)
- Every agent backstory includes anti-hallucination guardrail: "only report data from tools"
- Report agent has mandatory STEP 1: call `get_stock_price` before writing anything
- LLM model: `mistral/mistral-large-latest` via LiteLLM

### Error Handling

- Use specific exception types (no bare `except:`)
- Tools catch exceptions and return JSON error objects (never raise to CrewAI)
- NSE API requires session cookies — use `_get_nse_session()` which visits homepage first

### Testing

- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`, `@pytest.mark.critical`
- All external APIs mocked (yfinance, httpx, nsetools)
- Streamlit tests: `sys.modules['streamlit'] = MagicMock()` + `importlib.reload()`
- Bot tests: `AsyncMock` for async command handlers
- `# pragma: no cover` only on `if __name__ == "__main__"` blocks

### Report Generation

- PDF: fpdf2 with Helvetica (latin-1 only) — sanitize Unicode via `_sanitize_for_pdf` (₹→Rs., —→--)
- DOCX: python-docx with Calibri, tables, bold/italic parsing, XML borders
- Both generate to `BytesIO` for Streamlit download buttons

## Anti-Hallucination Rules (Critical)

These are non-negotiable guardrails:

1. **Tool errors must signal clearly** — always include `DATA_UNAVAILABLE: True` + `"Do NOT guess"`
2. **Agent prompts must say** "only report data returned by your tools" — never remove this
3. **Report agent verifies price** — STEP 1 must call `get_stock_price` before writing
4. **Low temperatures** — keep factual agents at 0.3-0.4, never raise above 0.5
5. **No phantom indicators** — only reference indicators the tools actually compute (RSI, MACD, Bollinger, SMA, EMA, ATR, pivots). Do NOT add Stochastic, ADX, OBV, Fibonacci, candlestick patterns to prompts
6. **No phantom data sources** — tools don't provide DCF models, sector averages, F&O data, or peer comparisons. Don't claim they do in agent prompts

## Data Sources

| Data | Source | Notes |
|------|--------|-------|
| Stock prices/info | yfinance | Append `.NS` suffix for NSE |
| NSE delivery % | nsetools | Falls back to yfinance on failure |
| FII/DII flows | NSE API `/api/fiidiiTradeReact` | Requires session cookies |
| Bulk/block deals | NSE API `/api/snapshot-capital-market-largedeal` | Requires session cookies |
| News (primary) | ET RSS feed | Most reliable source |
| News (backup) | Google News RSS, ET HTML scraping | Deduplication across sources |
| Moneycontrol | BLOCKED (403 WAF) | Do not attempt to restore |
| Business Standard | BLOCKED (403 WAF) | Do not attempt to restore |

## Environment Variables

Required in `.env` (see `.env.example`):

```
MISTRAL_API_KEY=          # Required for AI analysis
TELEGRAM_BOT_TOKEN=       # Required for bot only
TELEGRAM_ADMIN_IDS=       # Comma-separated, for bot only
CREWAI_TELEMETRY_OPT_OUT=true
OTEL_SDK_DISABLED=true
```

## Important Context

- **Indian market focus** — all constants, sectors, stock lists are NSE/BSE specific
- **NIFTY50 stocks** defined in `config.py:NIFTY50_STOCKS` (50 stocks)
- **Sectors** defined in `config.py:SECTORS` (10 sectors with constituent stocks)
- **Number formatting** uses Indian system: lakhs (L) and crores (Cr), not millions/billions
- **Pivot points** use standard daily formula: `(prevH + prevL + prevC) / 3` — not 20-day range
- **Technical config thresholds** in `config.py:TECHNICAL_CONFIG` and `FUNDAMENTAL_THRESHOLDS`
- **CI/CD** runs on GitHub Actions (Python 3.11, uv, codecov)
