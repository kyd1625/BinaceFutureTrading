import pandas as pd
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
    return df

def calculate_macd_and_analyze(data, short_period=12, long_period=26, signal_period=9):
    """
    MACD와 분석 결과를 계산하는 함수.

    Parameters:
        - data (pd.DataFrame): 'close' 열이 포함된 캔들 데이터.
        - short_period (int): 단기 EMA 기간 (기본값: 12).
        - long_period (int): 장기 EMA 기간 (기본값: 26).
        - signal_period (int): 시그널 라인 EMA 기간 (기본값: 9).

    Returns:
        - dict: 최신 MACD 값, 시그널 값, 분석 결과를 포함한 딕셔너리.
    """
    close = data['close']

    # 단기 EMA와 장기 EMA 계산
    short_ema = close.ewm(span=short_period, adjust=False).mean()
    long_ema = close.ewm(span=long_period, adjust=False).mean()

    # MACD 계산 (단기 EMA - 장기 EMA)
    macd = short_ema - long_ema

    # Signal Line 계산 (MACD의 EMA)
    signal = macd.ewm(span=signal_period, adjust=False).mean()

    # 최신 MACD와 Signal 값
    latest_macd = macd.iloc[-1]
    latest_signal = signal.iloc[-1]

    # 분석 (MACD와 Signal의 차이로 판단)
    if latest_macd > latest_signal:
        analysis = "강세 (매수 신호)"
    elif latest_macd < latest_signal:
        analysis = "약세 (매도 신호)"
    else:
        analysis = "중립"



    return {
        "MACD": latest_macd,
        "Signal": latest_signal,
        "Analysis": analysis
    }


def returnToMacd(symbol):
    # 심볼 및 타임프레임 설정
    interval = Client.KLINE_INTERVAL_1MINUTE

    # 캔들 데이터 가져오기
    data = fetch_klines(symbol, interval)

    # MACD 계산 및 분석
    result = calculate_macd_and_analyze(data)
    #print(result)

    return result

#if __name__ == '__main__':
    #returnToMacd("BTCUSDT") # MACD / Signal / Analysis