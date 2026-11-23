# Stock Market Intelligence Dashboard

An interactive stock market analytics portfolio project built with Python, Streamlit, Yahoo Finance (`yfinance`), Pandas and Plotly. It tracks price performance, daily returns, volatility, trading volume and moving averages, compares multiple tickers, and exports clean CSV data for Power BI.

## Features
- Latest available adjusted closing prices and daily percentage changes
- Historical price chart with 20-day and 50-day simple moving averages
- Period return and annualised historical volatility
- Trading-volume chart and average volume KPI
- Normalised multi-stock comparison (starting value = 100)
- Daily-return distribution
- Downloadable Power BI-ready CSV
- Supports US tickers (e.g. `AAPL`, `MSFT`) and Yahoo Finance India symbols (e.g. `RELIANCE.NS`, `TCS.NS`, `INFY.NS`)

## Dashboard preview
Run the app locally to view the interactive dashboard. The app uses a dark analytics layout and interactive Plotly charts.

## Tech stack
- Python 3.10+
- Streamlit
- yfinance (Yahoo Finance market data)
- Pandas / NumPy
- Plotly

## Run locally

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch dashboard
streamlit run app.py
```

Open the local URL printed in the terminal (usually http://localhost:8501).

## Suggested tickers
| Company | Yahoo Finance symbol |
|---|---|
| Apple | AAPL |
| Microsoft | MSFT |
| NVIDIA | NVDA |
| Reliance Industries | RELIANCE.NS |
| TCS | TCS.NS |
| Infosys | INFY.NS |
| HDFC Bank | HDFCBANK.NS |

Enter symbols in the sidebar separated by commas.

## Power BI integration
1. Run the dashboard and click **Download market data CSV (Power BI ready)**.
2. Open Power BI Desktop.
3. Select **Home → Get data → Text/CSV** and select `stock_market_data.csv`.
4. Check data types: Date = Date, prices = Decimal number, Volume = Whole number.
5. Build visuals:
   - Line chart: Date vs Close, legend = Ticker
   - KPI cards: Latest close, Period return, Annualised volatility
   - Column chart: Ticker vs Volume
   - Slicers: Ticker and Date
   - Table: OHLC, Daily Return, SMA 20, SMA 50

### Suggested DAX measures
```DAX
Latest Close =
VAR LatestDate = MAX(StockMarket[Date])
RETURN
    CALCULATE(MAX(StockMarket[Close]), StockMarket[Date] = LatestDate)

Average Daily Volume =
AVERAGE(StockMarket[Volume])

Average Daily Return % =
AVERAGE(StockMarket[Daily Return])
```

Rename the imported table to `StockMarket` before using the measures.

## GitHub publishing
Create a new **public** repository named `stock-market-intelligence-dashboard` on GitHub, then run these commands from this project folder:

```bash
git init
git add .
git commit -m "Build stock market intelligence dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/stock-market-intelligence-dashboard.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Your repository link will then be:
`https://github.com/YOUR-USERNAME/stock-market-intelligence-dashboard`

## Deploy online (optional)
You can deploy the repository using Streamlit Community Cloud:
1. Push the project to GitHub.
2. Sign in at https://share.streamlit.io/
3. Select **New app**, choose the repository, branch `main`, and file `app.py`.
4. Deploy.

## Important notes
- Yahoo Finance data is provided for educational and personal research use; availability, history and rate limits may change.
- “Real-time” in this project means the latest data available from the source; quotes can be delayed and are not guaranteed to be exchange real-time.
- This is an educational analytics project, not investment advice.
