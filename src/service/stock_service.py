from generated import stock_service_pb2, stock_service_pb2_grpc
from .stock_data_service import StockDataService

class StockService(stock_service_pb2_grpc.StockServiceServicer):

    def __init__(self):
        self.stock_data_service = StockDataService()

    def GetStockInfo(self, request, context):

        if request.year:
            data = self.stock_data_service.get_financials(request.ticker, request.year)
        else:
            data = self.stock_data_service.get_ttm_stock_data(request.ticker)

        return stock_service_pb2.StockResponse(
            ticker=data["ticker"],
            name=data["name"],
            year=data["year"],
            current_price=data["current_price"] or 0.0,
            total_revenue=data["total_revenue"] or 0.0,
            operating_income=data["operating_income"] or 0.0,
            net_income=data["net_income"] or 0.0,
            eps=data["eps"] or 0.0,
            basic_average_shares=data["basic_average_shares"] or 0.0,
            total_expenses=data["total_expenses"] or 0.0,
        )

    def GetCagrForecast(self, request, context):
        # response = self.stock_data_service.predict_cagr(request.ticker, request.start, request.end)
        response = self.stock_data_service.predict_5y_eps_growth("AMZN")
        print("response: ", response)

        return stock_service_pb2.CagrForecastResponse(
            message="passed"
        )