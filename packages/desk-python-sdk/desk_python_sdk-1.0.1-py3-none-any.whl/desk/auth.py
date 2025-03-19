from eth_account import Account
from web3 import Web3
from eth_keys import keys
from eth_account.messages import  encode_defunct

from desk.api import Api
from desk.utils.utils import generate_nonce, get_sub_account
from desk.types import NetworkOption
from desk.constant.common import CHAIN_ID

class Auth(Api):
    """Authentication class for DESK. Is needed if want to use "Exchange" class.

    Args:
        network (NetworkOption): network (mainnet, testnet)
        rpc_url (str): rpc url can be found on https://chainlist.org/
        account (str): evm account address
        sub_account_id (int): sub account id (max 255 but in web only display up to 5 (0 - 4))
        private_key (str): private key
        jwt (str): jwt (if provided, skip generating)

    """
    def __init__(self, network: NetworkOption, rpc_url: str, account: str, sub_account_id: int, private_key: str, jwt: str = None):
        if not rpc_url or sub_account_id == None or not private_key or not account:
            raise ValueError("rpc_url, sub_account_id, and private_key are required")
        super().__init__(network)
        self.chain_id = CHAIN_ID[network]
        self.rpc_url = rpc_url
        self.sub_account_id = str(sub_account_id)

        self.eth_provider = self.__get_provider()
        self.eth_signer = Account.from_key(private_key)
        self.account = account

        self.sub_account = get_sub_account(account, sub_account_id)
        
        if jwt:
            print('JWT provided, skip generating...')
            self.jwt = jwt
        else:

            self.nonce = str(generate_nonce())
            self.signature = self.__sign_msg()

            self.jwt, self.crm_jwt = self.__generate_jwt()


    def __get_provider(self) -> Web3:
        return Web3(Web3.HTTPProvider(self.rpc_url, request_kwargs={'timeout': 60}))


    def __sign_msg(self) -> str:
        msg = f"""Welcome to DESK!

Please sign this message to verify ownership of your wallet and proceed. By signing, you confirm the following: you have read, understood, and agreed to the Terms & Conditions, Privacy Policy, and any other relevant terms and conditions announced by DESK.

This request will not trigger a blockchain transaction or cost any gas fees.

Wallet address: {self.account.lower()}
Sub-account id: {self.sub_account_id}
Nonce: {self.nonce}"""

        encoded_msg = encode_defunct(text=msg)
        pk = keys.PrivateKey(self.eth_signer.key)
        signed_data = Account.sign_message(encoded_msg, pk)

        return signed_data.signature.to_0x_hex()
    
    def __generate_jwt(self) -> str:
        jwt = self.__api_generate_jwt(self.account, self.sub_account_id, self.nonce, self.signature)
        crm_jwt = self.__api_generate_jwt_crm(self.account, self.sub_account_id, self.nonce, self.signature)

        return jwt, crm_jwt
    
    def __api_generate_jwt(self, account: str, sub_account_id: str, nonce: str, signature: str) -> str:
        resp = self.post(f"/v2/auth/evm", payload={
            "account": account,
            "subaccount_id": sub_account_id,
            "nonce": nonce,
            "signature": signature
        })

        return resp["jwt"]
    
    def __api_generate_jwt_crm(self, account: str, sub_account_id: str, nonce: str, signature: str) -> str:
        resp = self.post_crm(f"/v1/users/auth", payload={
            "wallet_address": account,
            "subaccount_id": sub_account_id,
            "nonce": nonce,
            "signature": signature
        })

        return resp["access_token"]