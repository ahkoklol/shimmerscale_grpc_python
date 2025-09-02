import os
import pandas as pd

class ExcelDataExtractingService:
    def __init__(self, project_root: str = None):
        # Default project root is one level up from src/
        if project_root is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

        self.data_path = os.path.join(project_root, "data")
        self.cache = {}  # to avoid reloading the same Excel many times

    def _load_excel(self, ticker: str) -> pd.DataFrame:
        """
        Load Excel for a given ticker. Cached after first load.
        """
        ticker = ticker.upper()
        if ticker not in self.cache:
            file_path = os.path.join(self.data_path, ticker, f"{ticker}.xlsx")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Excel file not found for ticker {ticker}: {file_path}")

            df = pd.read_excel(file_path)

            # Ensure numeric columns are parsed correctly
            numeric_cols = [
                'year', 'total_revenue', 'operating_income', 'net_income',
                'ebitda', 'eps', 'basic_average_shares',
                'research_and_development', 'total_expenses'
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            self.cache[ticker] = df

        return self.cache[ticker]

    def get_financials(self, ticker: str, year: int) -> dict:
        """
        Get financial data for a given ticker and year.
        Returns a dict you can later map into your proto.
        """
        df = self._load_excel(ticker)
        row = df[(df["ticker"].str.upper() == ticker.upper()) & (df["year"] == year)]

        if row.empty:
            raise ValueError(f"No data found for {ticker} in year {year}")

        return row.iloc[0].to_dict()
