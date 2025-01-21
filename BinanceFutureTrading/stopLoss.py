import math
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from BinanceFutureTrading.UserApi import get_position_for_symbol, get_position_for_symbol_with_pnl
from config.secrets import APIKey, secretKey
from config.settings import testnetYN, stopLoss  # symbols를 리스트로 받음
from binance.client import Client

client = Client(APIKey, secretKey)
if testnetYN == "Y" :
    client.FUTURES_URL = client.FUTURES_TESTNET_URL  # testnetYN = "Y" 일시 테스트넷으로 적용


def get_position_for_symbol(symbol):
    """
    특정 심볼에 대한 열린 포지션 정보를 가져오는 함수.
    """
    try:
        # 선물 계좌의 포지션 정보 가져오기
        positions = client.futures_position_information()

        # 특정 심볼에 대한 포지션 찾기
        for position in positions:
            if position["symbol"] == symbol:
                position_amt = float(position["positionAmt"])

                if position_amt != 0:  # 포지션이 열려 있을 경우
                    # 필드가 존재하는지 확인 후 기본값 할당
                    unrealized_profit = float(position.get("unrealizedProfit", 0.0))
                    entry_price = float(position.get("entryPrice", 0.0))
                    liquidation_price = float(position.get("liquidationPrice", 0.0))
                    leverage = int(position.get("leverage", 1))
                    isolated = position.get("isolated", "FALSE") == "TRUE"

                    position_info = {
                        "symbol": symbol,
                        "positionAmt": position_amt,
                        "entryPrice": entry_price,
                        "unrealizedProfit": unrealized_profit,
                        "liquidationPrice": liquidation_price,
                        "leverage": leverage,
                        "isolated": isolated,
                    }
                    return position_info
        return None  # 열린 포지션이 없는 경우

    except Exception as e:
        print(f"포지션 정보 가져오기 오류: {e}")
        return None

def calculate_stop_loss_price(entry_price, position_side):
    """
    손절매 가격을 계산하는 함수.

    Args:
        entry_price (float): 포지션의 진입 가격.
        position_side (str): 포지션 방향 ("LONG" 또는 "SHORT").
        stop_loss_percentage (float): 손절매 비율 (예: 0.02 => 2%).

    Returns:
        float: 손절매 가격.
    """
    if position_side == "LONG":
        stop_loss_price = entry_price * (1 - stopLoss)
    elif position_side == "SHORT":
        stop_loss_price = entry_price * (1 + stopLoss)
    else:
        raise ValueError("Invalid position_side. Must be 'LONG' or 'SHORT'.")
    return round(stop_loss_price, 2)  # 소수점 두 자리로 반올림


def set_stop_loss(symbol, stop_loss_price, position_side):
    """
    손절매 주문을 등록하는 함수.

    Args:
        symbol (str): 거래할 심볼 (예: "BTCUSDT").
        stop_loss_price (float): 손절매 가격.
        position_side (str): 포지션 방향 ("LONG" 또는 "SHORT").

    Returns:
        dict: 주문 결과 또는 오류 메시지.
    """
    try:
        # 포지션 방향에 따른 주문 방향
        side = "SELL" if position_side == "LONG" else "BUY"

        # 손절매 주문 생성
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="STOP_MARKET",  # 시장가 손절매 주문
            stopPrice=stop_loss_price,  # 손절매 가격
            closePosition=True,  # 포지션 청산 여부
        )

        print(f"손절매 주문 등록 성공: {order}")
        return order

    except BinanceAPIException as e:
        print(f"Binance API 오류: {e}")
        return {"error": str(e)}

    except BinanceRequestException as e:
        print(f"Binance 요청 오류: {e}")
        return {"error": str(e)}

    except Exception as e:
        print(f"오류 발생: {e}")
        return {"error": str(e)}


# 통합 실행 로직
def manage_stop_loss(symbol):
    """
    특정 심볼의 포지션에 손절매를 설정하는 통합 함수.

    Args:
        symbol (str): 거래할 심볼 (예: "BTCUSDT").

    """
    position_info = get_position_for_symbol(symbol)

    if position_info:
        entry_price = position_info["entryPrice"]
        position_amt = position_info["positionAmt"]
        position_side = "LONG" if position_amt > 0 else "SHORT"

        # 손절매 가격 계산
        stop_loss_price = calculate_stop_loss_price(
            entry_price, position_side
        )

        print(
            f"심볼: {symbol}, 진입 가격: {entry_price}, 포지션 방향: {position_side}, 손절매 가격: {stop_loss_price}"
        )

        # 손절매 주문 등록
        set_stop_loss(symbol, stop_loss_price, position_side)
    else:
        print(f"{symbol}에 대한 열린 포지션이 없습니다.")


# 테스트 실행
#manage_stop_loss("BTCUSDT")
#print(get_position_for_symbol("BTCUSDT"))

