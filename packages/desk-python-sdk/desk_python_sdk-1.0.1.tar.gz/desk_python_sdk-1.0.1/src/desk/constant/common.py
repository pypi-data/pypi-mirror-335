from typing import Dict
from desk.types import NetworkOption, ChainOption


BROKER = "DESK-SDK"

BASE_URLS: Dict[NetworkOption, str] = {
    "mainnet": "https://api.happytrading.global",
    "testnet": "https://stg-trade-api.happytrading.global"
}

CRM_URLS: Dict[NetworkOption, str] = {
    "mainnet": "https://api.desk.exchange",
    "testnet": "https://dev-api.desk.exchange"
}

WSS_URLS: Dict[NetworkOption, str] = {
    "mainnet": "wss://ws-api.happytrading.global/ws",
    "testnet": "wss://stg-trade-ws-api.happytrading.global/ws"
}

CHAIN_ID: Dict[NetworkOption | ChainOption, int] = {
    "mainnet": 8453,
    "testnet": 421614,
    "base": 8453,
    "arbitrumSepolia": 421614
}

