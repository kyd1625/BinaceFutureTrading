import math
import time

from BinaceFutureTrading.UserApi import get_position_for_symbol, get_position_for_symbol_with_pnl
from BinaceFutureTrading.closePosition import close_position
from BinaceFutureTrading.stopLoss import manage_stop_loss
from BinaceFutureTrading.syncedToServerTime import returnTo_synced_timestamp
from config.secrets import APIKey, secretKey
from config.settings import testnetYN, symbols, usdt_ratio, stopLoss, leverage  # symbols를 리스트로 받음
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

def get_symbol_price_and_market_info(symbol):
    """
    특정 심볼의 현재가와 시장가 정보를 가져옵니다.

    Args:
        symbol (str): 조회할 심볼 (예: "BTCUSDT")

    Returns:
        dict: 현재가와 시장가 정보
    """
    try:
        # 현재가 가져오기
        ticker = client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker["price"])

        # 시장가 정보 가져오기
        market_info = client.futures_exchange_info()
        symbol_info = next(
            (s for s in market_info["symbols"] if s["symbol"] == symbol), None
        )

        if symbol_info is None:
            print(f"심볼 {symbol} 정보를 찾을 수 없습니다.")
            return None

        # 필요한 시장 정보 추출
        market_data = {
            "symbol": symbol,
            "current_price": current_price,
            "price_precision": int(symbol_info["pricePrecision"]),
            "quantity_precision": int(symbol_info["quantityPrecision"]),
            "min_price": float(symbol_info["filters"][0]["minPrice"]),  # 최소 가격 단위
            "max_price": float(symbol_info["filters"][0]["maxPrice"]),  # 최대 가격 단위
            "min_qty": float(symbol_info["filters"][1]["minQty"]),      # 최소 수량 단위
            "step_size": float(symbol_info["filters"][1]["stepSize"]),  # 수량 스텝
        }

        return market_data

    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def place_order_backup(symbol, side, usdt_ratio, synced_timestamp):
    """
    선물 매매 주문을 실행하는 함수.

    Args:
        symbol (str): 거래할 종목 (예: "BTCUSDT").
        side (str): 매매 방향 ("BUY" 또는 "SELL").
        usdt_ratio (float): USDT 잔고의 몇 퍼센트를 사용할지 (예: 0.1 => 10%).
    """

    # 현재 포지션 확인후 현재 포지션과 다른 매매 시 현재 포지션 청산
    nowPosition = get_position_for_symbol(symbol)

    if(nowPosition != None):

        if(nowPosition.get("positionAmt") > 0):
            nowSide = "BUY"
        else:
            nowSide = "SELL"

        current_PnL = get_position_for_symbol_with_pnl(symbol).get("PnL")

        if(nowSide != side and current_PnL > 5): # 수익률 5퍼로 잡음
            close_position(symbol)
            return
        else:
            print(symbol + " 의 포지션이 존재 하며 수익률에 달성하지 못하였습니다.")
            return



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
    print("order_amount_usdt -> " + order_amount_usdt.__str__())

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
    print("quantity -> " + quantity.__str__())

    # 주문 실행
    order = client.futures_create_order(
        symbol=symbol,
        side=side,  # "BUY" 또는 "SELL"
        type="MARKET",  # 시장가 주문
        quantity=quantity,  # 계산된 수량
        timestamp=synced_timestamp,
    )
    print(f"{symbol} 주문 완료: {order}")
    manage_stop_loss(symbol) # 손절매

def place_order(symbol, side, usdt_ratio, synced_timestamp):
    """
    선물 매매 주문을 실행하는 함수.

    Args:
        symbol (str): 거래할 종목 (예: "BTCUSDT").
        side (str): 매매 방향 ("BUY" 또는 "SELL").
        usdt_ratio (float): USDT 잔고의 몇 퍼센트를 사용할지 (예: 0.1 => 10%).
    """

    # 현재 포지션 확인 후 다른 방향의 포지션이 있을 경우 처리

    nowPosition = get_position_for_symbol(symbol)
    if nowPosition:
        if nowPosition.get("positionAmt") > 0:
            nowSide = "BUY"
        else:
            nowSide = "SELL"

        current_PnL = get_position_for_symbol_with_pnl(symbol).get("PnL")
        if (nowSide != side and current_PnL > 5) or current_PnL > 5:  # 수익률 5% 이상일 때 청산
            close_position(symbol)
            return
        else:
            print(f"{symbol} 포지션이 존재하며 수익률이 목표에 도달하지 않았습니다.")
            return

    # 현재 USDT 잔고 가져오기
    account_balance = client.futures_account_balance()
    usdt_balance = next(
        (balance for balance in account_balance if balance["asset"] == "USDT"), None
    )
    if usdt_balance is None:
        print("USDT 잔고를 찾을 수 없습니다.")
        return

    available_balance = float(usdt_balance["balance"])
    order_amount_usdt = available_balance * usdt_ratio  # 사용할 USDT 금액

    # 수수료를 고려하여 조정
    fee_rate = 0.0004  # 예시 수수료율
    adjusted_order_amount_usdt = order_amount_usdt * (1 - fee_rate)

    print(f"Order Amount (USDT) after fee adjustment: {adjusted_order_amount_usdt}")

    # 현재 가격 가져오기
    ticker = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(ticker["price"])

    # 수량 계산
    quantity = adjusted_order_amount_usdt / current_price

    # 심볼별 소수점 자리수와 최소 수량 가져오기
    precision, min_qty = get_symbol_precision(symbol)
    if precision is None:
        print(f"{symbol}의 정보를 가져올 수 없습니다.")
        return

    # 소수점 제한 및 최소 수량 보정
    quantity = max(round(quantity, precision), min_qty)
    print(f"Calculated Quantity: {quantity} (Min Qty: {min_qty}, Precision: {precision})")

    # 최소 주문 금액(PERCENT_PRICE 필터) 확인
    notional_value = quantity * current_price
    if notional_value < 5:  # 바이낸스 최소 주문 금액 제한 (보통 5 USDT)
        print(f"주문 금액({notional_value:.2f} USDT)가 최소 요구 금액(5 USDT)을 충족하지 못합니다.")
        return

    # 주문 실행
    if side != "HOLD":
        try:
            order = client.futures_create_order(
                symbol=symbol,
                side=side,  # "BUY" 또는 "SELL"
                type="MARKET",  # 시장가 주문
                quantity=quantity,  # 계산된 수량
                timestamp=synced_timestamp,
            )
            print(f"{symbol} 주문 완료: {order}")
            manage_stop_loss(symbol)  # 손절매 설정

        except Exception as e:
            print(f"주문 실패: {e}")


def place_order_with_leverage(symbol, side, usdt_ratio, synced_timestamp):
    """
    레버리지를 고려한 선물 매매 주문 실행 함수.

    Args:
        symbol (str): 거래할 종목 (예: "BTCUSDT").
        side (str): 매매 방향 ("BUY" 또는 "SELL").
        usdt_ratio (float): USDT 잔고의 몇 퍼센트를 사용할지 (예: 0.1 => 10%).
        leverage (int): 설정할 레버리지 배율.
        synced_timestamp (int): 서버 동기화된 타임스탬프.
    """

    # 현재 포지션 확인 후 다른 방향의 포지션이 있을 경우 처리
    nowPosition = get_position_for_symbol(symbol)
    if nowPosition:
        if nowPosition.get("positionAmt") > 0:
            nowSide = "BUY"
        else:
            nowSide = "SELL"

        current_PnL = get_position_for_symbol_with_pnl(symbol).get("PnL")

        if nowSide != side and current_PnL > 5:  # 수익률 5% 이상일 때 청산
            close_position(symbol)
            return
        else:
            print(f"{symbol} 포지션이 존재하며 수익률이 목표에 도달하지 않았습니다.")
            return

    # 레버리지 설정
    try:
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        print(f"{symbol}의 레버리지가 {leverage}배로 설정되었습니다.")
    except Exception as e:
        print(f"레버리지 설정 실패: {e}")
        return

    # 현재 USDT 잔고 가져오기
    account_balance = client.futures_account_balance()
    usdt_balance = next(
        (balance for balance in account_balance if balance["asset"] == "USDT"), None
    )
    if usdt_balance is None:
        print("USDT 잔고를 찾을 수 없습니다.")
        return

    available_balance = float(usdt_balance["balance"])
    order_amount_usdt = available_balance * usdt_ratio  # 사용할 USDT 금액

    # 레버리지를 반영한 주문 금액
    leverage_amount_usdt = order_amount_usdt * leverage
    print(f"레버리지 적용 후 주문 금액 (USDT): {leverage_amount_usdt}")

    # 수수료를 고려하여 조정
    fee_rate = 0.0004  # 예시 수수료율
    adjusted_order_amount_usdt = leverage_amount_usdt * (1 - fee_rate)

    print(f"Order Amount (USDT) after fee adjustment: {adjusted_order_amount_usdt}")

    # 현재 가격 가져오기
    ticker = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(ticker["price"])

    # 수량 계산
    quantity = adjusted_order_amount_usdt / current_price

    # 심볼별 소수점 자리수와 최소 수량 가져오기
    precision, min_qty = get_symbol_precision(symbol)
    if precision is None:
        print(f"{symbol}의 정보를 가져올 수 없습니다.")
        return

    # 소수점 제한 및 최소 수량 보정
    quantity = max(round(quantity, precision), min_qty)
    print(f"Calculated Quantity: {quantity} (Min Qty: {min_qty}, Precision: {precision})")

    # 최소 주문 금액(PERCENT_PRICE 필터) 확인
    notional_value = quantity * current_price
    if notional_value < 5:  # 바이낸스 최소 주문 금액 제한 (보통 5 USDT)
        print(f"주문 금액({notional_value:.2f} USDT)가 최소 요구 금액(5 USDT)을 충족하지 못합니다.")
        return

    # 주문 실행
    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,  # "BUY" 또는 "SELL"
            type="MARKET",  # 시장가 주문
            quantity=quantity,  # 계산된 수량
            timestamp=synced_timestamp,
        )
        print(f"{symbol} 주문 완료: {order}")
        manage_stop_loss(symbol)  # 손절매 설정

    except Exception as e:
        print(f"주문 실패: {e}")




# 여러 개의 심볼에 대해 매매 진행
def place_orders_for_multiple_symbols(symbols, side, usdt_ratio, synced_timestamp):
    for symbol in symbols:
        place_order(symbol, side, usdt_ratio, synced_timestamp)

# 테스트 실행
#synced_timestamp = returnTo_synced_timestamp()
#symbols = ["BTCUSDT"]  # 여러 심볼을 리스트로 받음
#place_orders_for_multiple_symbols(symbols, "BUY", usdt_ratio, synced_timestamp)  # 여러 심볼을 USDT의 10%로 매수

def realTrading(symbol, side):
    synced_timestamp = returnTo_synced_timestamp() # 서버타임 설정
    place_order(symbol, side, usdt_ratio, synced_timestamp) # 포지션 잡기
    #place_order_with_leverage(symbol, side, usdt_ratio, synced_timestamp)

