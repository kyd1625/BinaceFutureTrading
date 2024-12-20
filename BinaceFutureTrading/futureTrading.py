from config.secrets import APIKey, secretKey
from config.settings import url, symbol
from binance.client import Client

client = Client(APIKey, secretKey)
client.FUTURES_URL = url # url 설정

def trading(type, side, quantity):
    # param 정리
    # type = 시장가 고정, side = 매수/매도.
    try:
        order = client.futures_create_test_order(
            symbol = symbol,
            side = side,
            type=type,
            quantity=quantity
        )
        print(order)
    except Exception as e:
        print(f"매매 failed: {e}")

if __name__ == "__main__":
    server_time = client.futures_time()
    print(f"Server time: {server_time}")
    trading('MARKET', 'BUY', '0.01')
