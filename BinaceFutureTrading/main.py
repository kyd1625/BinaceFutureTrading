from BinaceFutureTrading.characteristic.BollingerBands import returnToBollinger
from BinaceFutureTrading.characteristic.MACD import returnToMacd
from BinaceFutureTrading.characteristic.RSI import returnToRsi
from BinaceFutureTrading.characteristic.stochastic import returnTostochastic
from BinaceFutureTrading.futureTrading import realTrading
from config.settings import symbols  # symbols를 리스트로 받음
import time


def analyze_indicators(rsi, macd, macdSignal, stoch_k, stoch_d, close_price, bb_upper, bb_lower, symbol):
    """
    지표 데이터를 분석하여 매수/매도 신호를 반환합니다.

    Args:
        rsi (float): RSI 값
        macd (float): MACD 값 (MACD선 - 시그널선)
        stoch_k (float): 스토캐스틱 K선 값
        stoch_d (float): 스토캐스틱 D선 값
        close_price (float): 현재 가격
        bb_upper (float): 볼린저밴드 상단값
        bb_lower (float): 볼린저밴드 하단값

    Returns:
        str: "BUY", "SELL", or "HOLD"
    """
    side = "HOLD"
    buy_signals = 0
    sell_signals = 0

    # RSI 신호
    print("rsi -> " + rsi.__str__())
    if rsi < 30:
        buy_signals += 1
    elif rsi > 70:
        sell_signals += 1



    # MACD 신호
    if macd > macdSignal:  # MACD선이 시그널선 위에 있을 경우
        buy_signals += 1
    elif macd < macdSignal:  # MACD선이 시그널선 아래에 있을 경우
        sell_signals += 1



    # 스토캐스틱 신호
    if stoch_k > stoch_d:  # 골든크로스 + 과매도 구간
        buy_signals += 1
    elif stoch_k < stoch_d:  # 데드크로스 + 과매수 구간
        sell_signals += 1



    # 볼린저밴드 신호
   # if close_price < bb_lower:  # 하단 밴드에서 반등
   #     buy_signals += 1
   # elif close_price > bb_upper:  # 상단 밴드에서 저항
   #     sell_signals += 1

    # 신호 분석
    if buy_signals >= 2:  # 매수 신호가 3개 이상이면 매수
        side = "BUY"
    elif sell_signals >= 2:  # 매도 신호가 3개 이상이면 매도
        side = "SELL"
    else:
        side = "HOLD"  # 신호가 부족하면 대기

    print("buy_signals4 -> " + buy_signals.__str__())
    print("sell_signals4 -> " + sell_signals.__str__())
    print("symbol -> " + symbol)
    print("side -> " + side)


    return side

def main():
    for symbol in symbols:
        #print("=" * 200)
        #print("symbol : " + symbol)
        resultRsi = returnToRsi(symbol)
        resultBollinger = returnToBollinger(symbol)
        resultMacd = returnToMacd(symbol)
        resultchastic = returnTostochastic(symbol)
        #print("=" * 200)


        requestSide = analyze_indicators(resultRsi.get("RSI"), resultMacd.get("MACD"), resultMacd.get("Signal")
                                         , resultchastic.get("stoch_k"), resultchastic.get("stoch_d")
                                         , resultBollinger.get("Close"), resultBollinger.get("Upper Band"), resultBollinger.get("Lower Band")
                                         , symbol)

        if(requestSide != "HOLD"):
            realTrading(symbol, requestSide)
        else:
            print("=" * 200)
            print(symbol + " 은 분석결과 매매에 적합하지 않아 매매가 이루어 지지 않습니다.")
            print("=" * 200)

if __name__ == "__main__":
    while True:
        main()  # 메인 함수 실행
        time.sleep(30)  # 10초 대기
