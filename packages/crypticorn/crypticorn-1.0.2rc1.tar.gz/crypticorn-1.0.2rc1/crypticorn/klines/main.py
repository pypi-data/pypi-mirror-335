from crypticorn.klines.client import FundingRatesApi, OHLCVDataApi, SymbolsApi, UDFApi, HealthCheckApi, Configuration, ApiClient
import pandas as pd

class FundingRatesApiWrapper(FundingRatesApi):
    def get_funding_rates_fmt(self):
        response = self.funding_rate_funding_rates_symbol_get()
        return pd.DataFrame(response.json())
    
class OHLCVDataApiWrapper(OHLCVDataApi):
    def get_ohlcv_data_fmt(self):
        response = self.get_ohlcv_market_timeframe_symbol_get()
        return pd.DataFrame(response.json())
    
class SymbolsApiWrapper(SymbolsApi):
    def get_symbols_fmt(self):
        response = self.symbols_symbols_market_get()
        return pd.DataFrame(response.json())
    
class UDFApiWrapper(UDFApi):
    def get_udf_fmt(self):
        response = self.get_history_udf_history_get()
        return pd.DataFrame(response.json())

class KlinesClient:
    """
    A client for interacting with the Crypticorn Klines API.
    """

    def __init__(self, base_url: str = 'https://api.crypticorn.dev', api_key: str = None, jwt: str = None):
        # Configure Klines client
        self.host = f"{base_url}/v1/klines"
        klines_config = Configuration(
            host=self.host,
        )
        base_client = ApiClient(configuration=klines_config)
        # Instantiate all the endpoint clients
        self.funding = FundingRatesApiWrapper(base_client)
        self.ohlcv = OHLCVDataApiWrapper(base_client)
        self.symbols = SymbolsApiWrapper(base_client)
        self.udf = UDFApiWrapper(base_client)
        self.health = HealthCheckApi(base_client)

