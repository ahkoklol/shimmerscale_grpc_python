import yfinance as yf

from service.excel_data_extracting_service import ExcelDataExtractingService
from service.stock_forecasting_service import StockForecastingService
from service.stock_forecasting_service_ml import StockForecastingServiceML


class StockDataService:
    def __init__(self):
        self.excel_data_extracting = ExcelDataExtractingService()
        self.stock_forecasting = StockForecastingService(self.excel_data_extracting)
        self.stock_forecasting_ml = StockForecastingServiceML(self.excel_data_extracting)

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
            "operating_income": safe_get("OperatingIncome"),
            "net_income": safe_get("NetIncome"),
            "ebitda": safe_get("EBITDA"),
            "eps": safe_get("BasicEPS", scale_million=False),
            "basic_average_shares": safe_get("BasicAverageShares"),
            "research_and_development": safe_get("ResearchAndDevelopment"),
            "total_expenses": safe_get("TotalExpenses"),
        }

    def get_financials(self, ticker, year) -> dict:

        data = self.excel_data_extracting.get_financials(ticker, year)

        stock = yf.Ticker(ticker)
        info = stock.info

        data["name"] = info.get("shortName")
        data["current_price"] = info.get("currentPrice")

        return data

    def predict_cagr(self, ticker: str, start: int, end: int, horizon: int = 5):
        print(f"\n[PREDICT] Starting CAGR prediction for {ticker} {start}–{end}, horizon={horizon}")

        forecasts = self.stock_forecasting.rolling_cagr_forecast(ticker, start, end, horizon=horizon)
        print(f"[PREDICT] Rolling forecasts count = {len(forecasts)}")

        results = []

        for f in forecasts:
            print(f"\n[PREDICT] Processing {f['train_period']} → {f['forecast_period']}")
            actuals = f["actuals"]
            years = sorted(actuals.keys())
            if len(years) >= 2:
                actual_cagr = self.stock_forecasting.historical_cagr(ticker, years[0], years[-1])
            else:
                actual_cagr = None
            print(f"[PREDICT] Predicted CAGR={f['cagr']}, Actual CAGR={actual_cagr}")

            comparison = self.stock_forecasting.compare_forecasts(f["forecasts"], f["actuals"])
            print(f"[PREDICT] Comparison metrics: {comparison}")

            results.append({
                "train_period": f["train_period"],
                "forecast_period": f["forecast_period"],
                "predicted_cagr": f["cagr"],
                "actual_cagr": actual_cagr,
                "forecast_vs_actual": comparison
            })

        final_prediction = forecasts[-1]["cagr"] if forecasts else None
        print(f"\n[PREDICT] Final predicted CAGR = {final_prediction}")

        return {
            "comparisons": results,
            "final_predicted_cagr": final_prediction
        }

    def predict_5y_eps_growth(self, ticker: str):
        """
        Predict the next 5-year EPS CAGR using XGBoost.
        """
        growth = self.stock_forecasting_ml.predict_5y_growth(ticker)
        return {
            "ticker": ticker,
            "predicted_5y_eps_cagr": growth
        }

