from service.stock import stock_service_pb2, stock_service_pb2_grpc

class StockService(stock_service_pb2_grpc.StockServiceServicer):
    def GetStockInfo(self, request, context):
        # Example response
        return stock_service_pb2.StockResponse(
            ticker=request.ticker,
            name="NVIDIA Corp",
            year="TTM",
            current_price=450.0,
            total_revenue=28262900000,
            operating_revenue=28262900000,
            operating_income=9022600000,
            net_income=7571600000,
            ebitda=10123600000,
            eps=19.24,
            basic_average_shares=393600000,
            research_and_development=4303700000,
            total_expenses=19240300000
        )
