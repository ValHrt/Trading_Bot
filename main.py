import tkinter as tk
import logging
from connectors.binance_futures import BinanceFuturesClient
import config

logger = logging.getLogger()

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

if __name__ == '__main__':

    binance = BinanceFuturesClient(config.api_key_testnet_binance, config.api_secret_testnet_binance, True)
    print(binance.get_balances())
    print(binance.get_order_status('BTCUSDT', 2678231258))

    root = tk.Tk()
    root.mainloop()
