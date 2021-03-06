import tkinter as tk
import logging
from connectors.binance_futures import BinanceFuturesClient
from connectors.bitmex import BitmexClient
import config

from interface.root_component import Root

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
    bitmex = BitmexClient(config.api_key_testnet_bitmex, config.api_secret_testnet_bitmex, True)

    root = Root(binance, bitmex)
    root.mainloop()
