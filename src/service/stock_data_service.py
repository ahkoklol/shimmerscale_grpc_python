import yfinance as yf

class StockDataService:
    def __init__(self):
        pass

    def get_ttm_stock_data(self, ticker: str) -> dict:
        stock = yf.Ticker(ticker)

        # Company metadata
        info = stock.info

        # Trailing Twelve Months (TTM) Income Statement
        income_stmt = stock.get_income_stmt(freq="trailing")  # DataFrame
        latest_col = income_stmt.columns[0] if not income_stmt.empty else None

        def safe_get(key, scale_million=True):
            """Helper to safely extract values, optionally in millions"""
            try:
                val = float(income_stmt.loc[key, latest_col])
                if scale_million:
                    return val / 1_000_000
                return val
            except Exception:
                return None

        return {
            "ticker": ticker,
            "name": info.get("shortName"),
            "year": "TTM",
            "current_price": info.get("currentPrice"),
            "total_revenue": safe_get("TotalRevenue"),
            "operating_revenue": safe_get("OperatingRevenue"),
            "operating_income": safe_get("OperatingIncome"),
            "net_income": safe_get("NetIncome"),
            "ebitda": safe_get("EBITDA"),
            "eps": safe_get("BasicEPS", scale_million=False),
            "basic_average_shares": safe_get("BasicAverageShares"),
            "research_and_development": safe_get("ResearchAndDevelopment"),
            "total_expenses": safe_get("TotalExpenses"),
        }
