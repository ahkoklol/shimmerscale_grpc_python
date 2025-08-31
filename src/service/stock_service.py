from generated import stock_service_pb2, stock_service_pb2_grpc
from .stock_data_service import StockDataService

class StockService(stock_service_pb2_grpc.StockServiceServicer):

    def __init__(self):
        self.stock_data_service = StockDataService()

    def GetStockInfo(self, request, context):
        data = self.stock_data_service.get_ttm_stock_data(request.ticker)

        return stock_service_pb2.StockResponse(
            ticker=data["ticker"],
            name=data["name"],
            year=data["year"],
            current_price=data["current_price"] or 0.0,
            total_revenue=data["total_revenue"] or 0.0,
            operating_revenue=data["operating_revenue"] or 0.0,
            operating_income=data["operating_income"] or 0.0,
            net_income=data["net_income"] or 0.0,
            ebitda=data["ebitda"] or 0.0,
            eps=data["eps"] or 0.0,
            basic_average_shares=data["basic_average_shares"] or 0.0,
            research_and_development=data["research_and_development"] or 0.0,
            total_expenses=data["total_expenses"] or 0.0,
        )
