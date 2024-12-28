import pandas as pd
import numpy as np
from binance.client import Client
from BinaceFutureTrading.config.secrets import APIKey, secretKey
from BinaceFutureTrading.config.settings import testnetYN, symbol

client = Client(APIKey, secretKey)
if testnetYN == "Y" :
    client.FUTURES_URL = client.FUTURES_TESTNET_URL # testnetYN = "Y" 일시 테스트넷으로 적용


# RSI 계산 함수
def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# RSI 분석 함수
def analyze_rsi(rsi_values):
    latest_rsi = rsi_values.iloc[-1]  # 최신 RSI 값
    prev_rsi = rsi_values.iloc[-2]   # 바로 직전 RSI 값

    if latest_rsi > 70:
        signal = "과매수 - 매도 신호"
    elif latest_rsi < 30:
        signal = "과매도 - 매수 신호"
    else:
        if latest_rsi > prev_rsi:
            signal = "상승 추세"
        else:
            signal = "하락 추세"
    return signal, latest_rsi

# Binance에서 데이터 가져오기
def fetch_klines(symbol, interval, limit=100):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                         'close_time', 'quote_asset_volume', 'number_of_trades',
                                         'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'])
    data['close'] = data['close'].astype(float)
    return data

def returnToRsi():
    # 심볼 및 설정
    interval = Client.KLINE_INTERVAL_5MINUTE

    # 데이터 가져오기 및 RSI 계산
    data = fetch_klines(symbol, interval)
    data['rsi'] = calculate_rsi(data)

    # RSI 분석
    rsi_values = data['rsi'].dropna()  # NaN 제거
    signal, latest_rsi = analyze_rsi(rsi_values)

    print(f"RSI 분석 결과: {signal}")
    print(f"최신 RSI 값: {latest_rsi:.2f}")
    return {
        "RSI": latest_rsi,
        "Analysis": signal
    }

if __name__ == '__main__':
    returnToRsi()