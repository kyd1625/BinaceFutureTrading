from binance.client import Client
from binance.exceptions import BinanceAPIException
import time

from BinanceFutureTrading.config.secrets import APIKey, secretKey
from BinanceFutureTrading.config.settings import testnetYN

client = Client(APIKey, secretKey)
if testnetYN == "Y" :
    client.FUTURES_URL = client.FUTURES_TESTNET_URL # testnetYN = "Y" 일시 테스트넷으로 적용

def close_all_positions():
    try:
        # 열린 포지션 정보 가져오기
        positions = client.futures_position_information()

        # 열린 포지션이 있을 경우
        for position in positions:
            symbol = position['symbol']
            position_amt = float(position['positionAmt'])

            if position_amt != 0:
                side = "SELL" if position_amt > 0 else "BUY"
                # 시장가로 반대방향 포지션 종료
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=abs(position_amt)
                )
                print(f"{symbol} 포지션 닫기: {side} {abs(position_amt)}")
    except BinanceAPIException as e:
        print(f"에러 발생: {e}")


def close_position(symbol):
    try:
        # 열린 포지션 정보 가져오기
        positions = client.futures_position_information(symbol=symbol)

        # 열린 포지션이 있을 경우
        for position in positions:
            position_amt = float(position['positionAmt'])

            if position_amt != 0:
                side = "SELL" if position_amt > 0 else "BUY"
                # 시장가로 반대방향 포지션 종료
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=abs(position_amt)
                )
                print(f"{symbol} 포지션 닫기: {side} {abs(position_amt)}")
    except BinanceAPIException as e:
        print(f"에러 발생: {e}")
