from typing import Any, List, Optional
import requests
from web3 import Web3
from desk.api import Api
from desk.auth import Auth
from desk.types import CancelAllOrdersFn, CancelAllOrdersRequest, CancelOrderFn, CancelOrderRequest, CreatePlaceOrderFn, NetworkOption, OrderRequest, OrderSide, OrderType, PlaceOrderResponse, TimeInForce
import desk.enum as enum
from desk.constant.contract import VAULT_CONTRACT_ABI, ERC20_ABI_PATH
from desk.constant.common import BROKER, BASE_URLS
from desk.utils import (
    load_contract, 
    map_token_profile,
    generate_nonce
)
from desk.utils.utils import convert_enum_to_string



class Exchange:
    """
    Exchange class for creating and managing orders / deposit or withdraw collateral

    Needed "Auth" object to be initialized
    """
    def __init__(self, network: NetworkOption, auth: Auth = None):
        self.network = network
        self.jwt = auth.jwt
        self.auth = auth

        if not auth or not auth.jwt:
            raise Exception("Auth is required")

        self.api = Api(network=network, headers={
                       "Authorization": f"Bearer {self.jwt}"})

        
        self.contract_address = self.__get_contract_address()

        self.vault_contract = load_contract(
            self.auth.eth_provider, self.contract_address["peripherals"]["vault"], VAULT_CONTRACT_ABI)

        self.token_profile = self.__get_token_profile()

    def __get_token_profile(self):
        resp = self.api.get("/v2/collaterals")
        return map_token_profile(resp, self.auth.chain_id)
    
    def __get_contract_address(self):
        resp = requests.get(f"{BASE_URLS[self.network]}/addresses-config?chain_id={self.auth.chain_id}")
        return resp.json()

    def __create_place_order_payload(self, order: CreatePlaceOrderFn):
        nonce = generate_nonce()

        order_type = convert_enum_to_string(order["orderType"])
        side = convert_enum_to_string(order["side"])
        symbol = convert_enum_to_string(order["symbol"])
        
        payload: OrderRequest = {
            "nonce": str(nonce),
            "amount": order["amount"],
            "price": order["price"],

            "broker_id": BROKER,
            "subaccount": self.auth.sub_account,

            "order_type": order_type,
            "side": side,
            "symbol": symbol,
        }

        # TIF
        if order_type == "Limit" or order_type == "Stop":
            payload["time_in_force"] = convert_enum_to_string(order["timeInForce"])

        # Optional args
        if "reduceOnly" in order:
            payload["reduce_only"] = order["reduceOnly"]

        if "triggerPrice" in order:
            payload["trigger_price"] = order["triggerPrice"]

        if "clientOrderId" in order:
            payload["client_order_id"] = order["clientOrderId"]
        
        if "waitForReply" in order:
            payload["wait_for_reply"] = order["waitForReply"]

        return payload

    def place_order(
        self,
        amount: str,
        price: str,
        side: OrderSide | enum.OrderSide,
        symbol: str | enum.MarketSymbol,
        order_type: OrderType | enum.OrderType,
        reduce_only: Optional[bool] = None,
        trigger_price: Optional[str] = None,
        time_in_force: Optional[TimeInForce | enum.TimeInForce] = None,
        wait_for_reply: bool = False,
        client_order_id: Optional[str] = None
    ) -> PlaceOrderResponse:
        """Place order

        Args:
            amount (str): order amount
            price (str): order price
            side (OrderSide): order side
            symbol (str): market symbol
            order_type (OrderType): order type
            reduce_only (Optional[bool]): whether the order is a reduce only order
            trigger_price (Optional[str]): trigger price
            time_in_force (Optional[TimeInForce]): time in force
            wait_for_reply (bool): should api wait for reply
            client_order_id (Optional[str]): client order id (max alphanumeric 36 characters)
        """
        order: CreatePlaceOrderFn = {
            "amount": amount,
            "price": price,
            "side": side,
            "symbol": symbol,
            "orderType": order_type,
            "reduceOnly": reduce_only,
            "triggerPrice": trigger_price,
            "timeInForce": time_in_force,
            "waitForReply": wait_for_reply,
            "clientOrderId": client_order_id
        }
        payload = self.__create_place_order_payload(order)
        return self.api.post("/v2/place-order", payload=payload)
    
    def batch_place_order(self, orders: List[CreatePlaceOrderFn]) -> Any:
        if len(orders) == 0:
            raise Exception("Orders is empty")
        payloads = [self.__create_place_order_payload(order) for order in orders]
        return self.api.post("/v2/batch-place-order", payload=payloads)

    def __create_cancel_order_payload(self, order: CancelOrderFn) -> CancelOrderRequest:
        nonce = generate_nonce()
        
        if ("orderDigest" not in order or order["orderDigest"] is None) and ("clientOrderId" not in order or order["clientOrderId"] is None):
            raise Exception("Either orderDigest or clientOrderId is required")

        payload: CancelOrderRequest = {
            "nonce": str(nonce),
            "subaccount": self.auth.sub_account,
            "symbol": convert_enum_to_string(order["symbol"]),
        }

        if "isConditionalOrder" in order:
            payload["is_conditional_order"] = order["isConditionalOrder"]

        if "waitForReply" in order:
            payload["wait_for_reply"] = order["waitForReply"]

        if "clientOrderId" in order:
            payload["client_order_id"] = order["clientOrderId"]

        if "orderDigest" in order:
            payload["order_digest"] = order["orderDigest"]

        return payload

    def cancel_order(
        self,
        symbol: str | enum.MarketSymbol,
        is_conditional_order: bool,
        order_digest: Optional[str] = None,
        wait_for_reply: bool = False,
        client_order_id: Optional[str] = None
    ) -> Any:
        """Cancel order

        Args:
            symbol (str): market symbol
            order_digest (str): order digest
            is_conditional_order (bool): whether the order is a conditional order
            wait_for_reply (bool): should api wait for reply
            client_order_id (str): client order id to cancel
        """
        order: CancelOrderFn = {
            "symbol": convert_enum_to_string(symbol),
            "orderDigest": order_digest,
            "isConditionalOrder": is_conditional_order,
            "waitForReply": wait_for_reply,
            "clientOrderId": client_order_id
        }
        payload = self.__create_cancel_order_payload(order)
        return self.api.post("/v2/cancel-order", payload=payload)
    
    def batch_cancel_order(self, orders: List[CancelOrderFn]) -> Any:
        """Batch cancel order

        Args:
            orders (List[CancelOrderFn]): list of orders to cancel

            CancelOrderFn: {
                "symbol": str,
                "orderDigest": str,
                "isConditionalOrder": bool, # optional
                "waitForReply": bool, # optional
                "clientOrderId": str # optional
            }
        """
        if len(orders) == 0:
            raise Exception("Orders is empty")
        payloads = [self.__create_cancel_order_payload(order) for order in orders]
        return self.api.post("/v2/batch-cancel-order", payload=payloads)
    
    def __create_cancel_all_orders_payload(self, order: CancelAllOrdersFn) -> CancelAllOrdersRequest:
        nonce = generate_nonce()

        payload: CancelAllOrdersRequest = {
            "nonce": str(nonce),
            "subaccount": self.auth.sub_account,
            "symbol": convert_enum_to_string(order["symbol"]),
            "is_conditional_order": order["isConditionalOrder"],
            "wait_for_reply": order["waitForReply"],
        }
        return payload
    
    def cancel_all_orders(self, symbol: str | enum.MarketSymbol = None, is_conditional_order: bool = False, wait_for_reply: bool = False) -> Any:
        """Cancel all orders

        Args:
            symbol (str): symbol to cancel all orders for
            is_conditional_order (bool): whether the order is a conditional order
            wait_for_reply (bool): should api wait for reply
        """
        order: CancelAllOrdersFn = {
            "symbol": convert_enum_to_string(symbol),
            "isConditionalOrder": is_conditional_order,
            "waitForReply": wait_for_reply,
        }
        payload = self.__create_cancel_all_orders_payload(order)
        return self.api.post("/v2/cancel-all-orders", payload=payload)

    def deposit_collateral(self, asset: str, amount: float):
        """Deposit collateral

        Args:
            asset (str): asset name
            amount (float): amount to deposit (human readable)

        Returns:
            transaction hash: str   
        """
        asset_str = convert_enum_to_string(asset)
        if asset_str not in self.token_profile:
            raise Exception(f"Collateral '{asset_str}' not recognized in token profile.")

        collateral = self.token_profile[asset_str]
        collateral_address = collateral["address"]

        vault_address = Web3.to_checksum_address(
            self.contract_address["peripherals"]["vault"])

        if not collateral_address:
            raise Exception("Collateral address not found")

        checksum_collateral_address = Web3.to_checksum_address(
            collateral_address)
        
        token_instance = load_contract(
            self.auth.eth_provider, checksum_collateral_address, ERC20_ABI_PATH)
        
        token_decimal = token_instance.functions.decimals().call()
        amount_wei = int(
            amount * 10 ** token_decimal)
        
        min_deposit = self.vault_contract.functions.minDeposits(checksum_collateral_address).call()
        if amount_wei < min_deposit:
            raise Exception(f"Amount is less than minimum deposit {float(min_deposit) / 10 ** token_decimal} {collateral['asset']}")

        signer_address = Web3.to_checksum_address(self.auth.eth_signer.address)

        allowance = token_instance.functions.allowance(
            signer_address, vault_address).call()

        if allowance < amount_wei:
            self.__send_transaction(token_instance.functions.approve(vault_address, amount_wei))
            
        return self.__send_transaction(self.vault_contract.functions.deposit(checksum_collateral_address, self.auth.sub_account, amount_wei))


    def withdraw_collateral(self, asset: str | enum.CollateralSymbol, amount: float):
        """Withdraw collateral

        Args:
            asset (str): asset name
            amount (float): amount to withdraw (human readable)

        Returns:
            transaction hash: str
        """
        asset_str = convert_enum_to_string(asset)
        if asset_str not in self.token_profile:
            raise Exception(f"Collateral '{asset_str}' not recognized in token profile.")
        
        collateral = self.token_profile[asset_str]
        collateral_address = collateral["address"]

        if not collateral_address:
            raise Exception("Collateral address not found")
        
        checksum_collateral_address = Web3.to_checksum_address(
            collateral_address)
        
        is_withdrawable = self.vault_contract.functions.withdrawableTokens(checksum_collateral_address).call()
        if not is_withdrawable:
            raise Exception(f"Collateral {asset_str} is not withdrawable")

        token_instance = load_contract(
            self.auth.eth_provider, checksum_collateral_address, ERC20_ABI_PATH)
        
        token_decimal = token_instance.functions.decimals().call()
        amount_wei = int(
            amount * 10 ** token_decimal)
        
        return self.__send_transaction(self.vault_contract.functions.withdraw(checksum_collateral_address, self.auth.sub_account, amount_wei))
    

    def __send_transaction(self, function):
        txn = function.build_transaction({
            "from": self.auth.eth_signer.address,
            "nonce": self.auth.eth_provider.eth.get_transaction_count(self.auth.eth_signer.address),
            "gas": 1000000,
            "gasPrice": self.auth.eth_provider.eth.gas_price
        })

        signed_txn = self.auth.eth_signer.sign_transaction(txn)
        txn_hash = self.auth.eth_provider.eth.send_raw_transaction(signed_txn.raw_transaction)
        if self.auth.eth_provider.eth.wait_for_transaction_receipt(txn_hash) == 0:
            raise Exception(f"Failed to send transaction {function} {txn_hash.hex()}")
        return txn_hash.hex()
