import tkinter as tk
from threading import Thread, Event
import time
import os

from BinanceFutureTrading.main import startToTrading

# 반복 작업을 멈추기 위한 이벤트 생성
stop_event = Event()

def save_to_config(data1, data2, data3, data4, data5, symbols, stopLoss):
    # 입력 데이터를 secrets.py와 settings.py 파일에 저장
    with open("./config/secrets.py", "w") as file:
        file.write(f"APIKey = '{data1}'\n")
        file.write(f"secretKey = '{data2}'\n")

    with open("./config/settings.py", "w") as file:
        file.write(f"testnetYN = '{data3}'\n")
        file.write(f"usdt_ratio = {float(data4)}\n")  # 소수점 저장
        file.write(f"leverage = {int(data5)}\n")  # 정수로 저장
        file.write(f"symbols = {symbols}\n")  # symbols는 리스트 형식으로 저장
        file.write(f"stopLoss = {float(stopLoss)}\n")  # 소수점 저장

    log_to_console("설정값 저장 완료!")

def load_from_config():
    if os.path.exists("./config/secrets.py") and os.path.exists("./config/settings.py"):
        try:
            secrets_data = {}
            with open("./config/secrets.py", "r", encoding="utf-8") as file:
                exec(file.read(), secrets_data)

            setting_data = {}
            with open("./config/settings.py", "r", encoding="utf-8") as file:
                exec(file.read(), setting_data)

            entry_one.delete(0, tk.END)
            entry_two.delete(0, tk.END)
            entry_one.insert(0, secrets_data.get("APIKey", ""))
            entry_two.insert(0, secrets_data.get("secretKey", ""))

            test_yn = setting_data.get("testnetYN", "Y")
            if test_yn == "Y":
                radio_var.set("Y")
            else:
                radio_var.set("N")

            entry_usdt_ratio.delete(0, tk.END)
            entry_leverage.delete(0, tk.END)
            entry_stopLoss.delete(0, tk.END)
            entry_usdt_ratio.insert(0, setting_data.get("usdt_ratio", ""))
            entry_leverage.insert(0, setting_data.get("leverage", ""))
            entry_stopLoss.insert(0, setting_data.get("stopLoss", ""))

            symbols = setting_data.get("symbols", [])
            entry_symbols.delete(0, tk.END)
            entry_symbols.insert(0, ", ".join(symbols))

            log_to_console("설정값 불러오기 성공!")
        except Exception as e:
            log_to_console(f"Error loading settings: {e}")
    else:
        log_to_console("secrets.py or settings.py file not found.")

def background_task():
    """ 무한 반복 작업 수행 함수 """
    log_to_console("백그라운드 작업 시작...")
    while not stop_event.is_set():
        startToTrading()
        time.sleep(1)  # 실제 작업 로직 대신 1초 대기
    log_to_console("백그라운드 작업 중지됨.")

def on_button_click():
    disable_inputs()
    log_to_console("프로그램 실행! (설정값 변경 불가)")
    btn_execute.config(state=tk.DISABLED)
    btn_stop.config(state=tk.NORMAL)

    # 스레드 시작
    stop_event.clear()
    thread = Thread(target=background_task, daemon=True)
    thread.start()

def stop_button_click():
    stop_event.set()  # 이벤트를 설정하여 반복 종료
    enable_inputs()
    log_to_console("프로그램 중지!")
    btn_execute.config(state=tk.NORMAL)
    btn_stop.config(state=tk.DISABLED)

def setting_button_click():
    input_one = entry_one.get()
    input_two = entry_two.get()
    input_three = radio_var.get()
    input_four = entry_usdt_ratio.get()
    input_five = entry_leverage.get()
    symbols = entry_symbols.get()
    input_stopLoss = entry_stopLoss.get()

    if input_one and input_two and input_three and input_four and input_five and input_stopLoss:
        symbols_list = [symbol.strip() for symbol in symbols.split(",") if symbol.strip()]
        save_to_config(input_one, input_two, input_three, input_four, input_five, symbols_list, input_stopLoss)
    else:
        log_to_console("모든 설정값을 입력해 주세요.")

def disable_inputs():
    entry_one.config(state=tk.DISABLED)
    entry_two.config(state=tk.DISABLED)
    entry_usdt_ratio.config(state=tk.DISABLED)
    entry_leverage.config(state=tk.DISABLED)
    entry_symbols.config(state=tk.DISABLED)
    radio_y.config(state=tk.DISABLED)
    radio_n.config(state=tk.DISABLED)
    entry_stopLoss.config(state=tk.DISABLED)

def enable_inputs():
    entry_one.config(state=tk.NORMAL)
    entry_two.config(state=tk.NORMAL)
    entry_usdt_ratio.config(state=tk.NORMAL)
    entry_leverage.config(state=tk.NORMAL)
    entry_symbols.config(state=tk.NORMAL)
    radio_y.config(state=tk.NORMAL)
    radio_n.config(state=tk.NORMAL)
    entry_stopLoss.config(state=tk.NORMAL)

def log_to_console(message):
    console.config(state=tk.NORMAL)
    console.insert(tk.END, message + "\n")
    console.yview(tk.END)
    console.config(state=tk.DISABLED)

root = tk.Tk()
root.title("Binance Future Trading")

frame_left = tk.Frame(root)
frame_left.grid(row=0, column=0, padx=10, pady=10)

frame_right = tk.Frame(root)
frame_right.grid(row=0, column=1, padx=10, pady=10)

label_status = tk.Label(root, text="Enter your settings below.")
label_status.grid(row=1, column=0, columnspan=2, pady=10)

tk.Label(frame_left, text="API_KEY:").grid(row=0, column=0, sticky="w", pady=5)
entry_one = tk.Entry(frame_left, width=30)
entry_one.grid(row=0, column=1, pady=5)

tk.Label(frame_left, text="SECRET_KEY:").grid(row=1, column=0, sticky="w", pady=5)
entry_two = tk.Entry(frame_left, width=30, show="*")
entry_two.grid(row=1, column=1, pady=5)

tk.Label(frame_left, text="TEST_YN:").grid(row=2, column=0, sticky="w", pady=5)
radio_var = tk.StringVar(value="N")
radio_y = tk.Radiobutton(frame_left, text="Y", variable=radio_var, value="Y")
radio_y.grid(row=2, column=1, sticky="w", padx=5)
radio_n = tk.Radiobutton(frame_left, text="N", variable=radio_var, value="N")
radio_n.grid(row=2, column=1, sticky="w", padx=50)

tk.Label(frame_right, text="잔고 사용률 (100% = 1) :").grid(row=0, column=0, sticky="w", pady=5)
entry_usdt_ratio = tk.Entry(frame_right, width=30)
entry_usdt_ratio.grid(row=0, column=1, pady=5)

tk.Label(frame_right, text="레버리지 :").grid(row=1, column=0, sticky="w", pady=5)
entry_leverage = tk.Entry(frame_right, width=30)
entry_leverage.grid(row=1, column=1, pady=5)

tk.Label(frame_right, text="Symbols (comma separated):").grid(row=2, column=0, sticky="w", pady=5)
entry_symbols = tk.Entry(frame_right, width=30)
entry_symbols.grid(row=2, column=1, pady=5)

tk.Label(frame_right, text="손절매 (0.1 = 10%) :").grid(row=3, column=0, sticky="w", pady=5)
entry_stopLoss = tk.Entry(frame_right, width=30)
entry_stopLoss.grid(row=3, column=1, pady=5)

btn_save = tk.Button(root, text="저장", command=setting_button_click)
btn_save.grid(row=2, column=0, pady=10)

btn_load = tk.Button(root, text="불러오기", command=load_from_config)
btn_load.grid(row=2, column=1, pady=10)

btn_execute = tk.Button(root, text="실행", command=on_button_click)
btn_execute.grid(row=3, column=0, pady=10)

btn_stop = tk.Button(root, text="중지", command=stop_button_click, state=tk.DISABLED)
btn_stop.grid(row=3, column=1, pady=10)

console = tk.Text(root, height=10, width=80)
console.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
console.config(state=tk.DISABLED)

load_from_config()
root.mainloop()
