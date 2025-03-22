from enum import Enum
import grpc
from . import exchange_pb2 as exchange
from . import exchange_pb2_grpc

from dataclasses import dataclass

@dataclass
class Response:
    status: str
    message: str

class OrderSide(Enum):
    BUY = 0
    SELL = 1
    
class OrderTif(Enum):
    DAY = 0
    IOC = 1

class Trader():
    def __init__(self, account, api_key, url, secure = True):
        if secure:
            self.channel = grpc.secure_channel(url)
        else:
            self.channel = grpc.insecure_channel(url)
        self.stub = exchange_pb2_grpc.ExchangeStub(self.channel)
        self.api_key = api_key
        self.account = account
    
    def submit_order(self, symbol: str, size: int, price: int, side: OrderSide, tif: OrderTif) -> Response:
        return submit_order(self.stub, symbol, size, price, side, tif, self.account, self.api_key)
    
    def cancel_order(self, order_id) -> Response:
        return cancel_order(self.stub, order_id, self.account, self.api_key)
        
    

def submit_order(stub: exchange_pb2_grpc.ExchangeStub, symbol: str, size: int, price: int, side: OrderSide, tif: OrderTif, account: str, api_key: str) -> Response: 
    request = exchange.OrderRequest(symbol = symbol, logging = "", size = str(size), price = str(price), side = side, tif = tif, account = account, api_key = api_key)
    response = stub.SubmitOrder(request)
    return Response(status = response.status, message = response.message)
    

    
def cancel_order(stub: exchange_pb2_grpc.ExchangeStub, order_id: str, account: str, api_key: str) -> Response:
    request = exchange.CancelOrderRequest(order_id = order_id, account = account, api_key = api_key)
    response = stub.CancelOrder(request)
    return Response(status = response.status, message = response.message)
    
