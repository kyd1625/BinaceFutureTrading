import time
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from config.secrets import APIKey, secretKey
from config.settings import testnetYN

client = Client(APIKey, secretKey)
if testnetYN == "Y" :
    client.FUTURES_URL = client.FUTURES_TESTNET_URL # testnetYN = "Y" 일시 테스트넷으로 적용

def synchronize_time():
    """
    서버 시간과 로컬 시간의 차이를 계산하여 서버 시간으로 동기화합니다.
    """
    try:
        # 서버 시간 가져오기
        server_time = client.futures_time()["serverTime"]

        # 현재 로컬 시간 (밀리초 단위)
        local_time = int(time.time() * 1000)

        # 시간 차이 계산
        time_offset = server_time - local_time

       # print(f"서버 시간과 로컬 시간의 차이: {time_offset}ms")
        return time_offset
    except (BinanceAPIException, BinanceRequestException) as e:
        print(f"API 오류 발생: {e}")
        return 0

def get_synced_timestamp(time_offset):
    """
    동기화된 서버 시간을 사용해 타임스탬프를 반환합니다.
    """
    # 로컬 시간 + 시간 차이를 보정한 서버 시간
    return int(time.time() * 1000) + time_offset

def returnTo_synced_timestamp():
    # 서버 시간 동기화 후, 동기화된 타임스탬프 확인
    time_offset = synchronize_time()
    synced_timestamp = get_synced_timestamp(time_offset)
    #print(f"동기화된 서버 타임스탬프: {synced_timestamp}")
    return synced_timestamp

