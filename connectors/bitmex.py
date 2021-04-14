import requests
import logging
import time
import typing

from urllib.parse import urlencode

import hmac
import hashlib

import websocket
import json

import threading

from models import *

logger = logging.getLogger()


class BitmexClient:
    def __init__(self, public_key: str, secret_key: str, testnet: bool):
        if testnet:
            self._base_url = "https://testnet.bitmex.com"
            self._wss_url = "wss://testnet.bitmex.com/realtime"
        else:
            self._base_url = "https://www.bitmex.com"
            self._wss_url = "wss://www.bitmex.com/realtime"

        self._public_key = public_key
        self._secret_key = secret_key

        self._ws = None

        self.contracts = self.get_contracts()
        self.balances = self.get_balances()

        self.prices = dict()

        self.logs = []

        t = threading.Thread(target=self._start_ws)
        t.start()

        logger.info("Bitmex Client initialisé avec succès")

    def _add_log(self, msg: str):
        logger.info("%s", msg)
        self.logs.append({"log": msg, "displayed": False})

    def _generate_signature(self, method: str, endpoint: str, expires: str, data: typing.Dict) -> str:

        message = method + endpoint + "?" + urlencode(data) + expires if len(data) > 0 else method + endpoint + expires
        return hmac.new(self._secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

    def _make_request(self, method: str, endpoint: str, data: typing.Dict):

        headers = dict()
        expires = str(int(time.time()) + 5)
        headers['api-expires'] = expires
        headers['api-key'] = self._public_key
        headers['api-signature'] = self._generate_signature(method, endpoint, expires, data)

        if method == 'GET':
            try:
                response = requests.get(self._base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error("Erreur de connexion en effectuant la requête %s à %s: %s", method, endpoint, e)
                return None

        elif method == 'POST':
            try:
                response = requests.post(self._base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error("Erreur de connexion en effectuant la requête %s à %s: %s", method, endpoint, e)
                return None

        elif method == 'DELETE':
            try:
                response = requests.delete(self._base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error("Erreur de connexion en effectuant la requête %s à %s: %s", method, endpoint, e)
                return None
        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Erreur en effectuant la requête %s à %s :%s (code erreur %s)",
                         method, endpoint, response.json(), response.status_code)
            return None

    def get_contracts(self) -> typing.Dict[str, Contract]:

        instruments = self._make_request("GET", "/api/v1/instrument/active", dict())

        contracts = dict()

        if instruments is not None:
            for s in instruments:
                contracts[s['symbol']] = Contract(s, "bitmex")

        return contracts

    def get_balances(self) -> typing.Dict[str, Balance]:
        data = dict()
        data['currency'] = "all"

        margin_data = self._make_request("GET", "/api/v1/user/margin", data)

        balances = dict()

        if margin_data is not None:
            for a in margin_data:
                balances[a['currency']] = Balance(a, "bitmex")

        return balances

    def get_historical_candles(self, contract: Contract, timeframe: str) -> typing.List[Candle]:
        data = dict()

        data['symbol'] = contract.symbol
        data['partial'] = True
        data['binSize'] = timeframe
        data['count'] = 500
        data['reverse'] = True

        raw_candles = self._make_request("GET", "/api/v1/trade/bucketed", data)

        candles = []

        if raw_candles is not None:
            for c in reversed(raw_candles):
                candles.append(Candle(c, timeframe, "bitmex"))

        return candles

    def place_order(self, contract: Contract, order_type: str, quantity: int, side: str, price=None,
                    tif=None) -> OrderStatus:
        data = dict()

        data['symbol'] = contract.symbol
        data['side'] = side.capitalize()
        data['orderQty'] = round(quantity / contract.lot_size) * contract.lot_size
        data['ordType'] = order_type.capitalize()

        if price is not None:
            data['price'] = round(round(price / contract.tick_size) * contract.tick_size, 8)

        if tif is not None:
            data['timeInForce'] = tif

        order_status = self._make_request("POST", "/api/v1/order", data)

        if order_status is not None:
            order_status = OrderStatus(order_status, 'bitmex')

        return order_status

    def cancel_order(self, order_id: str) -> OrderStatus:
        data = dict()

        data['orderID'] = order_id

        order_status = self._make_request("DELETE", "/api/v1/order", data)

        if order_status is not None:
            order_status = OrderStatus(order_status[0], 'bitmex')

        return order_status

    def get_order_status(self, order_id: str, contract: Contract) -> OrderStatus:
        data = dict()

        data['symbol'] = contract.symbol
        data['reverse'] = True

        order_status = self._make_request("GET", "/api/v1/order", data)

        if order_status is not None:
            for order in order_status:
                if order['orderID'] == order_id:
                    return OrderStatus(order, 'bitmex')

    def _start_ws(self):
        self._ws = websocket.WebSocketApp(self._wss_url, on_open=self._on_open, on_close=self._on_close,
                                          on_error=self._on_error, on_message=self._on_message)

        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error("Bitmex : erreur sur la méthode run_forever() : %s", e)
            time.sleep(2)

    def _on_open(self, ws):
        logger.info("Connexion ouverte avec Bitmex")

        self.subscribe_channel("instrument")

    def _on_close(self, ws):
        logger.warning("Connexion à Bitmex fermée")

    def _on_error(self, ws, msg: str):
        logger.error("Bitmex erreur de connexion : %s", msg)

    def _on_message(self, ws, msg: str):

        data = json.loads(msg)

        if "table" in data:
            if data["table"] == "instrument":

                for d in data["data"]:

                    symbol = d["symbol"]

                    if symbol not in self.prices:
                        self.prices[symbol] = {'bid': None, 'ask': None}

                    if 'bidPrice' in d:
                        self.prices[symbol]['bid'] = d['bidPrice']

                    if 'askPrice' in d:
                        self.prices[symbol]['ask'] = d['askPrice']

                    if symbol == "XBTUSD":
                        self._add_log(symbol + " " + str(self.prices[symbol]["bid"]) + " / " +
                                                         str(self.prices[symbol]["ask"]))

    def subscribe_channel(self, topic: str):
        data = dict()
        data['op'] = 'subscribe'
        data['args'] = []
        data['args'].append(topic)

        try:
            self._ws.send(json.dumps(data))
        except Exception as e:
            logger.error("Erreur Websocket pour souscrire à %s: %s", topic, e)
