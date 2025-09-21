import yfinance as yf
from generated.service.stock import stock_service_pb2, stock_service_pb2_grpc

class StockService(stock_service_pb2_grpc.StockServiceServicer):
    def GetStockInfo(self, request, context):
        # Fetch data using yfinance
        ticker_obj = yf.Ticker(request.ticker)

        # Basic info
        info = ticker_obj.info

        # Financials
        financials = ticker_obj.financials

        # Some fields may not exist; handle with defaults
        def safe_get(d, key, default=0):
            return d.get(key, default)

        return stock_service_pb2.StockResponse(
            ticker=request.ticker,
            name=safe_get(info, "longName", request.ticker),
            year="TTM",
            current_price=safe_get(info, "currentPrice", 0.0),
            total_revenue=financials.loc["Total Revenue"].iloc[0] if "Total Revenue" in financials.index else 0,
            operating_income=financials.loc["Operating Income"].iloc[0] if "Operating Income" in financials.index else 0,
            net_income=financials.loc["Net Income"].iloc[0] if "Net Income" in financials.index else 0,
            ebitda=financials.loc["EBITDA"].iloc[0] if "EBITDA" in financials.index else 0,
            eps=safe_get(info, "trailingEps", 0.0),
            basic_average_shares=safe_get(info, "sharesOutstanding", 0),
            total_expenses=financials.loc["Total Expenses"].iloc[0] if "Total Expenses" in financials.index else 0
        )
