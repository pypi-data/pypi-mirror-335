from crypticorn.trade.client import (
    BotsApi,
    ExchangesApi,
    NotificationsApi,
    OrdersApi,
    StatusApi,
    StrategiesApi,
    TradingActionsApi,
    FuturesTradingPanelApi,
    APIKeysApi,
    ApiClient,
    Configuration,
)


class TradeClient:
    """
    A client for interacting with the Crypticorn Trade API.
    """

    def __init__(self, base_url: str = None, api_key: str = None, jwt: str = None):
        # Configure Trade client
        self.host = f"{base_url}/v1/trade"
        config = Configuration(
            host=self.host,
            access_token=jwt,  # at the moment we only support JWT auth
        )
        base_client = ApiClient(configuration=config)
        # Instantiate all the endpoint clients
        self.bots = BotsApi(base_client)
        self.exchanges = ExchangesApi(base_client)
        self.notifications = NotificationsApi(base_client)
        self.orders = OrdersApi(base_client)
        self.status = StatusApi(base_client)
        self.strategies = StrategiesApi(base_client)
        self.trading_actions = TradingActionsApi(base_client)
        self.futures = FuturesTradingPanelApi(base_client)
        self.api_keys = APIKeysApi(base_client)
