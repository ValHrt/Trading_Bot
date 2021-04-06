import logging
import requests
import pprint

logger = logging.getLogger()


def get_contracts():
    response_object = requests.get("https://testnet.binancefuture.com/fapi/v1/exchangeInfo")

    contracts = []

    for contract in response_object.json()['symbols']:
        contracts.append(contract['pair'])

    return contracts


print(get_contracts())
