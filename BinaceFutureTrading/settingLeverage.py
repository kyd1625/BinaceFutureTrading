from binance.client import Client
from binance.exceptions import BinanceAPIException

from BinaceFutureTrading.syncedToServerTime import returnTo_synced_timestamp
from config.secrets import APIKey, secretKey
from config.settings import testnetYN, symbol, leverage


client = Client(APIKey, secretKey)
if testnetYN == "Y" :
    client.FUTURES_URL = client.FUTURES_TESTNET_URL # testnetYN = "Y" 일시 테스트넷으로 적용

def set_leverage(symbol, leverage, synced_timestamp):
    """
    레버리지를 설정하는 함수.
    포지션이 있을 경우 레버리지를 설정할 수 없습니다.

    Args:
        symbol (str): 거래할 심볼 (예: "BTCUSDT").
        leverage (int): 설정할 레버리지 값.
    """
    # 현재 포지션 확인
    positions = client.futures_position_information(symbol=symbol)
    position_open = any(float(position["positionAmt"]) != 0 for position in positions)

    if position_open:
        print(f"포지션이 열려있어 {symbol}의 레버리지를 변경할 수 없습니다.")
        return

    try:
        # 레버리지 설정
        response = client.futures_change_leverage(symbol=symbol, leverage=leverage, timestamp=synced_timestamp)
        print(f"{symbol}의 레버리지가 {leverage}배로 설정되었습니다.")
        print(response)
    except BinanceAPIException as e:
        print(f"레버리지 설정 중 오류 발생: {e}")

# 테스트 실행
synced_timestamp = returnTo_synced_timestamp()
set_leverage(symbol, leverage, synced_timestamp)  # BTCUSDT의 레버리지를 10배로 설정
