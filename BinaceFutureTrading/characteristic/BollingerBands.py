import pandas as pd
import numpy as np
from binance.client import Client
from BinaceFutureTrading.config.secrets import APIKey, secretKey
from BinaceFutureTrading.config.settings import testnetYN

client = Client(APIKey, secretKey)
if testnetYN == "Y" :
    client.FUTURES_URL = client.FUTURES_TESTNET_URL # testnetYN = "Y" 일시 테스트넷으로 적용


def fetch_klines(symbol, interval, limit=100):
    """
    Binance API를 사용하여 캔들스틱 데이터를 가져오는 함수.

    Parameters:
        - symbol (str): 거래 쌍 (예: "BTCUSDT").
        - interval (str): 캔들 간격 (예: Client.KLINE_INTERVAL_15MINUTE).
        - limit (int): 가져올 캔들 데이터의 개수 (기본값: 100).

    Returns:
        - pd.DataFrame: 캔들스틱 데이터프레임.
    """
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    return df

def calculate_bollinger_bands(data, period=20, std_dev=2):
    """
    볼린저 밴드 계산 및 분석.

    Parameters:
        - data (pd.DataFrame): 'close', 'high', 'low' 열이 포함된 캔들 데이터.
        - period (int): 이동 평균을 계산할 기간 (기본값: 20).
        - std_dev (int): 표준편차의 배수 (기본값: 2).

    Returns:
        - dict: 볼린저 밴드와 분석 결과를 포함한 딕셔너리.
    """
    close = data['close']

    # 중앙선 (Middle Band): 이동 평균
    middle_band = close.rolling(window=period).mean()

    # 표준편차
    std_dev_value = close.rolling(window=period).std()

    # 상단 밴드 (Upper Band)와 하단 밴드 (Lower Band) 계산
    upper_band = middle_band + (std_dev * std_dev_value)
    lower_band = middle_band - (std_dev * std_dev_value)

    # 최신 데이터
    latest_close = close.iloc[-1]
    latest_upper_band = upper_band.iloc[-1]
    latest_lower_band = lower_band.iloc[-1]

    # 분석: 가격이 상단 밴드를 넘으면 과매수, 하단 밴드를 넘으면 과매도
    if latest_close > latest_upper_band:
        analysis = "매도 신호" # 과매수시 매도 신호
    elif latest_close < latest_lower_band:
        analysis = "매수 신호" # 과매도시 매수 신호
    else:
        analysis = "중립"

    return {
        "Upper Band": latest_upper_band,
        "Lower Band": latest_lower_band,
        "Middle Band": middle_band.iloc[-1],
        "Close": latest_close,
        "Analysis": analysis
    }

def returnToBollinger(symbol):
    # 심볼 및 타임프레임 설정
    interval = Client.KLINE_INTERVAL_5MINUTE

    # 캔들 데이터 가져오기
    data = fetch_klines(symbol, interval)

    # 볼린저 밴드 계산 및 분석
    result = calculate_bollinger_bands(data)
    #print(result)

    return result

# 테스트용 MAIN함수 마지막 주석 처리 예정
#if __name__ == '__main__':
    #returnToBollinger("BTCUSDT") # Upper Band / Lower Band / Middle Band / Close / Analysis