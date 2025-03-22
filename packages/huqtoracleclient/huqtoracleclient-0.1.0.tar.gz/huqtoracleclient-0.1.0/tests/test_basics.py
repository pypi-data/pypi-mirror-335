from huqt_oracle_client import client


def run():
    # Create a channel to the server at the given address (e.g., localhost:50051).
    trader = client.Trader("account", "sigma", 'localhost:50051', secure=False)
    trader2 = client.Trader("account2", "rigma", 'localhost:50051', secure=False)
    
    # Prepare a request message
    response = trader.submit_order(symbol = "BTC", size = 2, price = 100, side = 0, tif = 0)
    print(response)
    
    id = response.message
    response = trader2.cancel_order(order_id = id)
    print(response)
    
    response = trader.cancel_order(order_id = id)
    print(response)
    
    response = trader.submit_order(symbol = "BTC", size = 2, price = 100, side = 0, tif = 0)
    print(response)
    
    response = trader2.submit_order(symbol = "BTC", size = "2", price = "98", side = 1, tif = 0)
    print(response)
    
if __name__ == '__main__':
    run()