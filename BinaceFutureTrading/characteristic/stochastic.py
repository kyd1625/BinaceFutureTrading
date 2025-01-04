import pandas as pd
from binance.client import Client
from BinaceFutureTrading.config.secrets import APIKey, secretKey
from BinaceFutureTrading.config.settings import testnetYN

client = Client(APIKey, secretKey)
if testnetYN == "Y" :
    client.FUTURES_URL = client.FUTURES_TESTNET_URL # testnetYN = "Y" 일시 테스트넷으로 적용

# Binance API Key & Secret
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"

# Binance 클라이언트 초기화
client = Client(api_key, api_secret)

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

def calculate_stochastic(data, period=14, smooth_k=3, smooth_d=3):
    """
    스토캐스틱 오실레이터 (%K, %D) 계산 및 분석.

    Parameters:
        - data (pd.DataFrame): 'close', 'high', 'low' 열이 포함된 캔들 데이터.
        - period (int): 스토캐스틱을 계산할 기간 (기본값: 14).
        - smooth_k (int): %K의 평활화 기간 (기본값: 3).
        - smooth_d (int): %D의 평활화 기간 (기본값: 3).

    Returns:
        - dict: %K, %D, 분석 결과를 포함한 딕셔너리.
    """
    high = data['high']
    low = data['low']
    close = data['close']

    # %K 계산
    lowest_low = low.rolling(window=period).min()
    highest_high = high.rolling(window=period).max()

    stoch_k = 100 * ((close - lowest_low) / (highest_high - lowest_low))

    # %K의 평활화 (Smoothing)
    stoch_k_smoothed = stoch_k.rolling(window=smooth_k).mean()

    # %D 계산 (%K의 EMA)
    stoch_d = stoch_k_smoothed.rolling(window=smooth_d).mean()

    # 최신 %K, %D 값
    latest_k = stoch_k_smoothed.iloc[-1]
    latest_d = stoch_d.iloc[-1]

    # 분석: %K와 %D의 교차 및 과매수/과매도 판단
    if latest_k > latest_d:
        analysis = "매수 신호 (K > D)"
    elif latest_k < latest_d:
        analysis = "매도 신호 (K < D)"
    elif latest_k > 80:
        analysis = "과매수 (Overbought)"
    elif latest_k < 20:
        analysis = "과매도 (Oversold)"
    else:
        analysis = "중립"

    return {
        "stoch_k": latest_k,
        "stoch_d": latest_d,
        "Analysis": analysis
    }


def returnTostochastic(symbol):
    # 심볼 및 타임프레임 설정
    interval = Client.KLINE_INTERVAL_1MINUTE

    # 캔들 데이터 가져오기
    data = fetch_klines(symbol, interval)

    # 스토캐스틱 계산 및 분석
    result = calculate_stochastic(data)
    #print(result)

    return result

#if __name__ == '__main__':
    #returnTostochastic("BTCUSDT") # stoch_k / stoch_d