import math
import time
from binance import BinanceAPIException, BinanceRequestException

from BinaceFutureTrading.syncedToServerTime import returnTo_synced_timestamp
from config.secrets import APIKey, secretKey
from config.settings import testnetYN, symbols, usdt_ratio  # symbols를 리스트로 받음
from binance.client import Client

client = Client(APIKey, secretKey)
if testnetYN == "Y" :
    client.FUTURES_URL = client.FUTURES_TESTNET_URL  # testnetYN = "Y" 일시 테스트넷으로 적용

def get_symbol_precision(symbol):
    """
    심볼의 소수점 자리수 및 최소 수량 정보를 가져옵니다.
    """
    exchange_info = client.futures_exchange_info()
    for s in exchange_info["symbols"]:
        if s["symbol"] == symbol:
            min_qty = float(s["filters"][1]["minQty"])  # 최소 주문 수량
            step_size = float(s["filters"][1]["stepSize"])  # 수량 소수점 스텝
            precision = int(round(-math.log(step_size, 10)))  # 소수점 자리수 계산
            return precision, min_qty
    return None, None

def place_order(symbol, side, usdt_ratio, synced_timestamp):
    """
    선물 매매 주문을 실행하는 함수.

    Args:
        symbol (str): 거래할 종목 (예: "BTCUSDT").
        side (str): 매매 방향 ("BUY" 또는 "SELL").
        usdt_ratio (float): USDT 잔고의 몇 퍼센트를 사용할지 (예: 0.1 => 10%).
    """
    # 현재 USDT 잔고 가져오기
    account_balance = client.futures_account_balance()
    usdt_balance = next(
        (balance for balance in account_balance if balance["asset"] == "USDT"), None
    )
    if usdt_balance is None:
        print("USDT 잔고를 찾을 수 없습니다.")
        return

    available_balance = float(usdt_balance["balance"])
    order_amount_usdt = available_balance * usdt_ratio  # 주문할 USDT 금액

    # 현재 가격 가져오기
    ticker = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(ticker["price"])

    # 수량 계산
    quantity = order_amount_usdt / current_price

    # 심볼별 소수점 자리수와 최소 수량 가져오기
    precision, min_qty = get_symbol_precision(symbol)
    if precision is None:
        print(f"{symbol}의 정보를 가져올 수 없습니다.")
        return

    # 소수점 제한 및 최소 수량 보정
    quantity = max(round(quantity, precision), min_qty)

    # 주문 실행
    order = client.futures_create_order(
        symbol=symbol,
        side=side,  # "BUY" 또는 "SELL"
        type="MARKET",  # 시장가 주문
        quantity=quantity,  # 계산된 수량
        timestamp=synced_timestamp,
    )
    print(f"{symbol} 주문 완료: {order}")

# 여러 개의 심볼에 대해 매매 진행
def place_orders_for_multiple_symbols(symbols, side, usdt_ratio, synced_timestamp):
    for symbol in symbols:
        place_order(symbol, side, usdt_ratio, synced_timestamp)

# 테스트 실행
synced_timestamp = returnTo_synced_timestamp()
# symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT"]  # 여러 심볼을 리스트로 받음
place_orders_for_multiple_symbols(symbols, "BUY", usdt_ratio, synced_timestamp)  # 여러 심볼을 USDT의 10%로 매수
