import numpy as np
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from BinaceFutureTrading.config.secrets import APIKey, secretKey
from BinaceFutureTrading.config.settings import testnetYN, symbol


client = Client(APIKey, secretKey)
if testnetYN == "Y" :
    client.FUTURES_URL = client.FUTURES_TESTNET_URL # testnetYN = "Y" 일시 테스트넷으로 적용

def get_historical_data(symbol, interval, lookback):
    """
    지정된 심볼에 대해 과거 데이터를 가져오는 함수.

    Args:
        symbol (str): 거래할 심볼 (예: "BTCUSDT").
        interval (str): 데이터 간격 (예: '1m', '5m', '1h' 등).
        lookback (int): 조회할 데이터 개수 (예: 1000).

    Returns:
        pd.DataFrame: 과거 가격 데이터
    """
    try:
        # 과거 가격 데이터 요청 (종가만 사용)
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=lookback)
        # 종가 리스트로 변환
        close_prices = [float(kline[4]) for kline in klines]
        # DataFrame으로 변환
        df = pd.DataFrame(close_prices, columns=["close"])
        return df
    except BinanceAPIException as e:
        print(f"데이터 가져오기 오류: {e}")
        return None

def calculate_rsi(df, period=14):
    """
    주어진 데이터프레임에서 RSI 값을 계산하는 함수.

    Args:
        df (pd.DataFrame): 가격 데이터 (종가).
        period (int): RSI를 계산할 기간 (기본값은 14일).

    Returns:
        pd.Series: 계산된 RSI 값
    """
    # 가격 변화 (종가의 차이)
    delta = df['close'].diff()

    # 상승과 하락을 분리
    gain = delta.where(delta > 0, 0)  # 상승
    loss = -delta.where(delta < 0, 0)  # 하락

    # 14일 평균 상승폭, 평균 하락폭 계산
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # RS 계산 (Relative Strength)
    rs = avg_gain / avg_loss

    # RSI 계산
    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_average_rsi(rsi_series, num_values=5):
    """
    최근 num_values개의 RSI 값의 평균을 계산하는 함수.

    Args:
        rsi_series (pd.Series): RSI 값의 시리즈.
        num_values (int): 평균을 계산할 최근 RSI 값의 개수 (기본값은 5).

    Returns:
        float: 최근 num_values개의 RSI 값의 평균
    """
    # 최근 num_values개의 RSI 값을 가져오고 평균 계산
    return rsi_series.tail(num_values).mean()

# RSI 계산 예시
def retrunToRis() :
    global average_rsi
    interval = "5m"  # 5분 간격
    lookback = 1000  # 최근 1000개의 데이터
    df = get_historical_data(symbol, interval, lookback)

    if df is not None:
        rsi = calculate_rsi(df)
        average_rsi = calculate_average_rsi(rsi)
        print(f"최근 5개의 RSI 평균값: {average_rsi}")

    return average_rsi
