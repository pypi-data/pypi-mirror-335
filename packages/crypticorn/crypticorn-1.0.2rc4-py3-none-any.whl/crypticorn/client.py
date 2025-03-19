from crypticorn.hive import HiveClient
from crypticorn.trade import TradeClient
from crypticorn.klines import KlinesClient

class CrypticornClient:
    def __init__(
        self, base_url: str = "https://api.crypticorn.com", api_key: str = None, jwt: str = None
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.jwt = jwt
        
        # Initialize service clients
        self.hive = HiveClient(base_url, api_key, jwt)
        self.trade = TradeClient(base_url, api_key, jwt)
        self.klines = KlinesClient(base_url, api_key, jwt)
