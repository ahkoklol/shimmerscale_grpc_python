import numpy as np

class StockForecastingService:
    def __init__(self, excel_service):
        self.excel_service = excel_service

    def historical_cagr(self, ticker: str, start_year: int, end_year: int):
        """
        Compute actual CAGR between two years using historical revenue data.
        """
        df = self.excel_service._load_excel(ticker)
        df = df.sort_values("year")

        row_start = df[df["year"] == start_year]
        row_end = df[df["year"] == end_year]

        if row_start.empty or row_end.empty:
            print(f"[HIST_CAGR] Missing data for {ticker} in {start_year} or {end_year}")
            return None

        start_rev = row_start.iloc[0]["total_revenue"]
        end_rev = row_end.iloc[0]["total_revenue"]
        years = end_year - start_year

        return self.compute_cagr(start_rev, end_rev, years)

    def compute_cagr(self, start, end, years):
        if start is None or end is None or years <= 0:
            print(f"[CAGR] Invalid input → start={start}, end={end}, years={years}")
            return None
        if start <= 0 or end <= 0:
            print(f"[CAGR] Negative/zero revenue → start={start}, end={end}")
            return None
        cagr = (end / start) ** (1 / years) - 1
        print(f"[CAGR] Computed CAGR from {start} → {end} over {years} years = {cagr:.4f}")
        return cagr

    def rolling_cagr_forecast(self, ticker: str, start_year: int, end_year: int, horizon: int = 5):
        df = self.excel_service._load_excel(ticker)
        df = df.sort_values("year")

        print(f"[ROLLING] Data loaded for {ticker}:\n{df[['year','total_revenue']]}")

        results = []

        for train_start in range(start_year, end_year - horizon + 1):
            train_end = train_start + horizon - 1
            forecast_start = train_end + 1
            forecast_end = forecast_start + (horizon - 1)

            print(f"\n[ROLLING] Train {train_start}–{train_end}, Forecast {forecast_start}–{forecast_end}")

            train_data = df[(df["year"] >= train_start) & (df["year"] <= train_end)]
            if len(train_data) < 2:
                print(f"[ROLLING] Skipping: insufficient train data ({len(train_data)} rows)")
                continue

            start_rev = train_data.iloc[0]["total_revenue"]
            end_rev = train_data.iloc[-1]["total_revenue"]
            print(f"[ROLLING] Start revenue={start_rev}, End revenue={end_rev}")

            cagr = self.compute_cagr(start_rev, end_rev, horizon - 1)

            forecasts = {}
            if cagr is not None:
                for i in range(forecast_start, forecast_end + 1):
                    years_out = i - train_end
                    forecasts[i] = end_rev * ((1 + cagr) ** years_out)
            else:
                for i in range(forecast_start, forecast_end + 1):
                    forecasts[i] = None
            print(f"[ROLLING] Forecasts: {forecasts}")

            actuals = df[(df["year"] >= forecast_start) & (df["year"] <= forecast_end)]
            actual_dict = {int(row["year"]): row["total_revenue"] for _, row in actuals.iterrows()}
            print(f"[ROLLING] Actuals: {actual_dict}")

            results.append({
                "train_period": f"{train_start}-{train_end}",
                "forecast_period": f"{forecast_start}-{forecast_end}",
                "cagr": cagr,
                "forecasts": forecasts,
                "actuals": actual_dict
            })

        return results

    def compare_forecasts(self, forecasts: dict, actuals: dict):
        """
        Compare forecasted values with actuals.
        Returns MAPE and RMSE.
        """
        y_true = []
        y_pred = []

        for year, actual in actuals.items():
            if year in forecasts and actual is not None:
                y_true.append(actual)
                y_pred.append(forecasts[year])

        if not y_true:
            return {"MAPE": None, "RMSE": None}

        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

        return {"MAPE": mape, "RMSE": rmse}
