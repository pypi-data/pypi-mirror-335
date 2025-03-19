import httpx
import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel
from typing import Optional, Union, List
from urllib.parse import urljoin
from datetime import datetime, timedelta

from crypticorn.hive import HiveClient
from crypticorn.trade import TradeClient
from crypticorn.klines import KlinesClient

class PredictionData(BaseModel):
    id: Optional[int] = None
    action: Optional[str] = None
    course_change: Optional[float]
    symbol: str
    timestamp: int
    version: str
    base_price: Optional[float]
    p10: list[float]
    p30: list[float]
    p50: list[float]
    p70: list[float]
    p90: list[float]


class TrendData(BaseModel):
    timestamps: Optional[list[int]]
    positive_prob: list[float]
    symbol: str
    version: Optional[str]


class TrendQuery(BaseModel):
    symbol: str
    limit: int
    offset: int
    sort: str
    dir: str
    from_ts: int
    to_ts: int
    version: str = "1"

default_version = "1.5"

class CrypticornClient:
    def __init__(
        self, base_url: str = "https://api.crypticorn.com", api_key: str = None, jwt: str = None
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.jwt = jwt
        self.client = httpx.Client()
        
        # Initialize service clients
        self.hive = HiveClient(base_url, api_key, jwt)
        self.trade = TradeClient(base_url, api_key, jwt)
        self.klines = KlinesClient(base_url, api_key, jwt)

    def get_response(
        self, endpoint: str, params: dict = None, dict_key: str = None
    ) -> Union[DataFrame, dict]:
        full_url = urljoin(self.base_url, "/v1/miners" + endpoint)
        print(full_url)
        print(params)
        try:
            response = self.client.get(full_url, params=params, timeout=None)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return {}
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            return {}

        formatted_response = response.json()

        if dict_key:
            return formatted_response.get(dict_key, {})

        return DataFrame(formatted_response)
    
    # -------------------- START OF DATA PLATFORM SERVICE ------------------------ #
    def get_economics_news(self, entries: int, reverse: bool = False) -> DataFrame:
        class NewsData(BaseModel):
            timestamp: int
            country: Union[str, None]
            event: Union[str, None]
            currency: Union[str, None]
            previous: Union[float, None]
            estimate: Union[float, None]
            actual: Union[float, None]
            change: Union[float, None]
            impact: Union[str, None]
            changePercentage: Union[float, None]

        res = self.get_response("/ec", {"entries": entries, "reverse": reverse}, "data")
        df = DataFrame(res)
        df.columns = NewsData.__annotations__
        df.sort_values(by="timestamp", ascending=False, inplace=True)
        return df

    def get_bc_historical(
        self, ticker: str, interval: str, entries: int, reverse: bool = False
    ) -> DataFrame:
        """

        get: ticker + open_unix + OHLC + Volume data , as pandas dataframe

        --- structure reference: ---

        (column name: data type)

        timestamp: int,
        ticker: str
        open_interval: float,
        high_interval: float,
        low_interval: float,
        close_interval: float,
        volume_interval: float,
        """
        df = self.get_response(
            "/historical",
            {"ticker": ticker + "@" + interval, "entries": entries, "reverse": reverse},
        )
        desired_order = [
            "timestamp",
            "ticker",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        df = df[desired_order]
        df.rename(
            columns={
                "ticker": "coin",
                "open": f"open_{interval}",
                "high": f"high_{interval}",
                "low": f"low_{interval}",
                "close": f"close_{interval}",
                "volume": f"volume_{interval}",
            },
            inplace=True,
        )
        df[["coin", "interval"]] = df["coin"].str.split("@", expand=True)
        df.pop("interval")
        df.sort_values(by="timestamp", ascending=False, inplace=True)
        df["timestamp"] = df["timestamp"] // 1000
        return df

    def get_fgi_historical(self, days: int) -> DataFrame:
        """

        get: unix_time + value , as pandas dataframe

        --- structure reference: ---

        (column name: data type)

        unix_time: int,
        value: int,

        """
        df = self.get_response(endpoint="/historical/fgi", params={"days": days})
        return df

    def post_prediction(self, data: PredictionData) -> dict:
        response = self.client.post(
            urljoin(self.base_url, "/v1/predictions"),
            json=data.dict(),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        return response.json()

    def get_latest_predictions(self, version: str = default_version) -> DataFrame:
        response = self.client.get(
            urljoin(self.base_url, f"/v1/predictions/latest?version={version}"),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        arr = response.json()
        flatarr = []
        for i in arr:
            for index, _ in enumerate(i["p50"]):
                interval = 900
                ts = i["timestamp"]
                ts = ts - (ts % interval)
                ts = ts + (index * interval)
                pred_dict = {
                    "id": i["id"],
                    "action": i["action"],
                    "course_change": i["course_change"],
                    "symbol": i["symbol"],
                    "timestamp": ts,
                    "version": i["version"],
                    # "base_price": i["base_price"],
                    "p10": i["p10"][index],
                    "p30": i["p30"][index],
                    "p50": i["p50"][index],
                    "p70": i["p70"][index],
                    "p90": i["p90"][index],
                }
                flatarr.append(pred_dict)
        df = DataFrame(flatarr)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        return df

    def get_prediction(self, pair: str, version: str = default_version, limit: int = 1) -> PredictionData:
        response = self.client.get(
            urljoin(self.base_url, f"/v1/predictions/symbol/{pair}?version={version}&limit={limit}"),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        return response.json()

    def get_prediction_time(self, id) -> DataFrame:
        response = self.client.get(
            urljoin(self.base_url, f"/v1/predictions/time/{id}"),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        arr = response.json()
        return DataFrame(arr)

    def get_udf_history(self, symbol: str, entries: int) -> DataFrame:
        now = int(pd.Timestamp.now().timestamp())
        response = self.client.get(
            urljoin(self.base_url, "/v1/udf/history"),
            headers={"Authorization": f"Bearer {self.api_key}"},
            params={
                "from": now - (entries * 900),
                "to": now,
                "symbol": symbol,
                "resolution": "15",
                "countback": entries,
            },
        )
        # # {'s': 'ok', 't': [1710982800.0, 1710983700.0], 'c': [67860.61, 67930.01], 'o': [67656.01, 67860.6], 'h': [67944.69, 67951.15], 'l': [67656.0, 67792.06], 'v': [448.61539, 336.9907]}
        result = response.json()
        # construct dataframe for t, c, o, h, l, v arrays
        df = DataFrame(result)
        df["t"] = pd.to_datetime(df["t"], unit="s")
        df.pop("s")
        return df

    def post_trend(self, data: TrendData) -> dict:
        response = self.client.post(
            urljoin(self.base_url, "/v1/trends"),
            json=data.dict(),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        return response.json()

    def get_trends(self, query: TrendQuery):
        response = self.client.get(
            urljoin(self.base_url, "/v1/trends"),
            headers={"Authorization": f"Bearer {self.api_key}"},
            params=query.dict(),
        )
        df = DataFrame(response.json())
        return df

    # -------------------- END OF DATA PLATFORM SERVICE ------------------------ #

    # -------------------- START OF KLINE SERVICE ------------------------ #
    def get_symbols(self, market: str) -> DataFrame:
        """
        get: symbol for futures or spot, as pandas dataframe
        market: futures or spot
        """
        response = self.klines.symbols.symbols_symbols_market_get(market=market)
        if response.status_code == 200:
            df = DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get symbols: {response.json()}")

    def get_klines(self, market: str, symbol: str,  interval: str, limit: int, start_timestamp: int = None, end_timestamp: int = None, sort: str = "desc") -> DataFrame:
        """
        get: unix_time + OHLCV data , as pandas dataframe
        symbol have to be in capital case e.g. (BTCUSDT)
        market: futures or spot
        interval: 1m, 3m, 5m, 15m, 30m, 1h, 4h, 1d
        """
        params = {"limit": limit}
        if start_timestamp is not None:
            params["start"] = start_timestamp
        if end_timestamp is not None:
            params["end"] = end_timestamp
        if sort is not None:
            params["sort_direction"] = sort

        response = self.client.get(
            urljoin(self.base_url, f"/v1/klines/{market}/{interval}/{symbol}"),
            params=params, timeout=None
        )
        if response.status_code == 200:
            df = DataFrame(response.json())
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['timestamp'] = df['timestamp'].astype("int64") // 10 ** 9 # use int64 instead of int for windows
            return df
        else:
            raise Exception(f"Failed to get klines: {response.json()}")
    
    def get_funding_rate(self, symbol: str, start_timestamp: int = None, end_timestamp: int = None, limit: int = 2000) -> DataFrame:
        """
        get: unix_time + funding rate data , as pandas dataframe
        symbol have to be in capital case e.g. (BTCUSDT)
        start_timestamp and end_timestamp are optional
        """
        params = {"limit": limit}
        if start_timestamp is not None:
            params["start"] = start_timestamp
        if end_timestamp is not None:
            params["end"] = end_timestamp

        response = self.client.get(
            urljoin(self.base_url, f"/v1/klines/funding_rates/{symbol}"),
            params=params, timeout=None
        )
        if response.status_code == 200:
            df = DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get funding rates: {response.json()}")
    
    # -------------------- END OF KLINE SERVICE ------------------------ #
    
    # -------------------- START OF TRADE SERVICE ------------------------ #
    def list_orders(self) -> DataFrame:
        response = self.client.get(
            urljoin(self.base_url, "/v1/trade/orders"),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        return DataFrame(response.json())
    
    def get_enabled_bots(self) -> DataFrame:
        response = self.client.get(
            urljoin(self.base_url, "/v1/trade/bots/enabled"),
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        data = response.json()
        return {
            "bots": DataFrame(data["bots"]),
            "api_keys": DataFrame(data["api_keys"])
        }
    
    # -------------------- END OF TRADE SERVICE ------------------------ #
    
    # -------------------- START OF GOOGLE TRENDS ------------------------ #
    # Get all keywords available for Google Trends
    def get_google_trend_keywords_available(self) -> DataFrame:
        response = self.client.get(
            urljoin(self.base_url, "/v1/google/keywords"),
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get google trends keywords available: {response.json()}")

    # Get Google Trends data for a specific keyword
    def get_google_trend_keyword(self, keyword: str, timeframe: str = '8m', limit: int = 100) -> DataFrame:
        """
        Retrieves Google Trends data for a specific keyword.

        Args:
            keyword (str): The keyword to retrieve Google Trends data for.
            timeframe (str, optional): The timeframe for the data. Defaults to '8m'.
            limit (int, optional): The maximum number of data points to retrieve. Defaults to 100.

        Returns:
            DataFrame: A pandas DataFrame containing the Google Trends data.

        """
        response = self.client.get(
            urljoin(self.base_url, f"/v1/google/trends/{keyword}"),
            params={"timeframe": timeframe, "limit": limit}, timeout=None
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json()['data'])
            df.rename(columns={"values": "trend_val", "timestamps": "timestamp"}, inplace=True)
            return df
        else:
            raise Exception(f"Failed to get google trends: {response.json()}")

    # -------------------- END OF GOOGLE TRENDS ------------------------ #
    
    # -------------------- START OF MARKET SERVICE ------------------------ #
    def get_exchange_all_symbols(self, exchange_name: str) -> DataFrame:
        """Exchange names to be added as follows: 
        Binance, KuCoin, Gate.io, Bybit, Bingx, Bitget
        """
        if exchange_name not in ['Binance', 'KuCoin', 'Gate.io', 'Bybit', 'Bingx', 'Bitget']:
            raise ValueError("Invalid exchange name it needs to be one of the following: Binance, KuCoin, Gate.io, Bybit, Bingx, Bitget")
        response = self.client.get(
            urljoin(self.base_url, f"/v1/market/exchange-data/{exchange_name}"), timeout=None
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get exchange all symbols: {response.json()}")

    def get_symbol_info_exchange(self, exchange_name: str, symbol: str, market: str = 'spot') -> DataFrame:
        """
        Exchange names to be added as follows: 
        Binance, KuCoin, Gate.io, Bybit, Bingx, Bitget

        Exchange symbols to be added as follows:
        Spot -> BTC-USDT, ETH-USDT, LTC-USDT
        Futures -> BTC-USDT-USDT, ETH-USDT-USDT, LTC-USDT-USDT
        """
        if market == 'futures':
            symbol = symbol + '-USDT'
        response = self.client.get(
            urljoin(self.base_url, f"/v1/market/exchange-data/{exchange_name}/{symbol}"), timeout=None
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get symbol info: {response.json()}")
    
    def get_cnn_sentiment(self, indicator_name: str, start_date: str = None, end_date: str = None, limit: int = None) -> DataFrame:
        """
        Retrieves Fear and Greed Index data for a specific indicator name.

        Args:
            indicator_name (str): The indicator name / keyword to retrieve Fear and Greed Index data for.
            start_date (str, optional): The start date for the data. Defaults to None.
            end_date (str, optional): The end date for the data. Defaults to None.
            limit (int, optional): The maximum number of data points to retrieve. Defaults to None.

        Returns:
            DataFrame: A pandas DataFrame containing the Fear and Greed Index data.

        """
        response = self.client.get(
            urljoin(self.base_url, f"/v1/market/fng-index/{indicator_name}"),
            params={"start_date": start_date, "end_date": end_date, "limit": limit}, timeout=None
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get cnn sentiment: {response.json()}")

    def get_cnn_keywords(self) -> DataFrame:
        response = self.client.get(
            urljoin(self.base_url, "/v1/market/fng-index/list-indicators"), timeout=None
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            df.columns = ['indicator_name']
            return df
        else:
            raise Exception(f"Failed to get cnn keywords: {response.json()}")
    
    def get_economic_calendar_events(self, start_timestamp: int = None, end_timestamp: int = None, currency: str = 'EUR', country_code: str = 'DE') -> DataFrame:
        """
        Function returns a pandas dataframe with the economic calendar events for the specified currency and country code during given time period.
        currency: EUR, CNY, NZD, AUD, USD, JPY, UAH, GBP, CHF, CAD
        country_code: CA, UA, ES, US, FR, JP, IT, NZ, AU, CN, UK, CH, EMU, DE
        """
        start_date = None
        end_date = None
        if isinstance(start_timestamp, int):
            start_date = pd.to_datetime(start_timestamp, unit='s').strftime('%Y-%m-%d')
        if isinstance(end_timestamp, int):
            end_date = pd.to_datetime(end_timestamp, unit='s').strftime('%Y-%m-%d')
            
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "currency": currency,
            "country_code": country_code
        }
        response = self.client.get(
            urljoin(self.base_url, f"/v1/market/ecocal"), timeout=None, params=params
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get economic calendar events: {response.json()}")
    
    def get_bitstamp_symbols(self) -> List[str]:
        response = self.client.get(
            urljoin(self.base_url, f"/v1/market/bitstamp/symbols"), timeout=None
        )
        if response.status_code == 200:
            symbols = response.json()
            # convert all symbols to uppercase
            symbols = [symbol.upper() for symbol in symbols]
            return symbols
        else:
            raise Exception(f"Failed to get bitstamp symbols: {response.json()}")
    
    def get_bitstamp_ohlcv_spot(self, symbol: str,  interval: str, limit: int, start_timestamp: int = None, end_timestamp: int = None) -> DataFrame:
        """
        get: unix_time + OHLCV data , as pandas dataframe
        symbol have to be in capital case e.g. (BTCUSDT)
        interval: 15m, 30m, 1h, 4h, 1d
        """
        params = {"limit": limit}
        if start_timestamp is not None:
            params["start"] = start_timestamp
        if end_timestamp is not None:
            params["end"] = end_timestamp
            
        response = self.client.get(
            urljoin(self.base_url, f"/v1/market/bitstamp/{symbol}/{interval}"),
            params=params, timeout=None
        )
        if response.status_code == 200: 
            df = DataFrame(response.json())
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['timestamp'] = df['timestamp'].astype("int64") // 10 ** 9 # use int64 instead of int for windows
            return df
        else:
            raise Exception(f"Failed to get bitstamp ohlcv spot: {response.json()}")
        
    # -------------------- END OF MARKET SERVICE ------------------------ #
    
    # -------------------- START OF MARKETCAP METRICS SERVICE ------------------------ #
    # Get historical marketcap rankings for coins
    def get_historical_marketcap_rankings(self, start_timestamp: int = None, end_timestamp: int = None, interval: str = "1d", market: str = None, exchange_name: str = None) -> dict:
        """
        Get historical marketcap rankings and exchange availability for cryptocurrencies.
        
        Args:
            start_timestamp (int, optional): Start timestamp for the data range
            end_timestamp (int, optional): End timestamp for the data range
            interval (str, optional): Time interval between data points (e.g. "1d")
            market (str, optional): Market type (e.g. "futures")
            exchange_name (str, optional): Exchange name (e.g. "binance", "kucoin", "gate.io", "bybit", "bingx", "bitget")
            
        Returns:
            DataFrame: A pandas DataFrame containing the historical marketcap rankings
        """
        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/marketcap/symbols"), 
            timeout=None,
            params={
                "start_timestamp": start_timestamp, 
                "end_timestamp": end_timestamp, 
                "interval": interval,
                "market": market,
                "exchange": exchange_name
            }
        )
        
        data = response.json()
        # Process rankings data
        rankings_df = pd.DataFrame(response.json())
        rankings_df.rename(columns={rankings_df.columns[0]: 'timestamp'}, inplace=True)
        rankings_df['timestamp'] = pd.to_datetime(rankings_df['timestamp']).astype("int64") // 10 ** 9
        return rankings_df
    
    def get_historical_marketcap_values_for_rankings(self, start_timestamp: int = None, end_timestamp: int = None) -> DataFrame:
        """
        Get historical marketcap values for rankings
        """
        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/marketcap"), timeout=None, params={"start_timestamp": start_timestamp, "end_timestamp": end_timestamp}
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            df.rename(columns={df.columns[0]: 'timestamp'}, inplace=True)
            df['timestamp'] = pd.to_datetime(df['timestamp']).astype("int64") // 10 ** 9
            return df
        else:
            raise Exception(f"Failed to get historical marketcap values for rankings: {response.json()}")
    
    def get_marketcap_indicator_values(self, symbol: str,market: str, period: int, indicator_name: str, timestamp:int = None):
        """
        Get marketcap indicator values for a specific indicator name and timestamp
        Indicator names to be added as follows:
        ker, sma
        """
        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/{indicator_name}/{symbol}"), timeout=None, params={"market": market, "period": period, "timestamp": timestamp}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get marketcap indicator values: {response.json()}")
    
    def get_exchanges_for_mc_symbol(self, symbol: str, market: str, interval: str = '1d', start_timestamp: int = None, end_timestamp: int = None, status: str = 'ACTIVE', quote_currency: str = 'USDT') -> DataFrame:
        """
        status: 'ACTIVE', 'RETIRED'
        quote_currency: USDT, USDC (can be retrieved from get_unique_quote_currencies())
        """
        
        if start_timestamp is None:
            start_timestamp = int((datetime.now() - timedelta(days=7, hours=0, minutes=0, seconds=0)).timestamp())
        if end_timestamp is None:
            end_timestamp = int((datetime.now() - timedelta(days=0, hours=0, minutes=0, seconds=0)).timestamp())
            
        params = {
            "interval": interval,
            "start_timestamp": start_timestamp,
            "end_timestamp": end_timestamp,
            "status": status,
            "quote_currency": quote_currency
        }

        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/available_exchanges/{market}/{symbol}"), timeout=None, params=params
        )
        if response.status_code == 200:
            result = response.json()
            processed_results = []
            for row in result:
                data = {'timestamp': row['timestamp']}
                data.update(row['exchanges'])
                processed_results.append(data)
            df = pd.DataFrame(processed_results)
            cols = ['timestamp'] + sorted([col for col in df.columns if col != 'timestamp'])
            df = df[cols]
            df['timestamp'] = pd.to_datetime(df['timestamp']).astype("int64") // 10 ** 9
            df = df.astype(int)
            return df
        else:
            raise Exception(f"Failed to get exchanges for mc symbol: {response.json()}")
    
    def get_marketcap_ranking_with_ohlcv(self, market: str, timeframe: str, top_n: int, ohlcv_limit: int, timestamp: int = int((datetime.now() - timedelta(days=1, hours=0, minutes=0, seconds=0)).timestamp())) -> DataFrame:
        params = {"market": market, "timeframe": timeframe, "top_n": top_n, "ohlcv_limit": ohlcv_limit, "timestamp": timestamp}
        print(params)
        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/marketcap/symbols/ohlcv"), timeout=None, params=params
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get marketcap ranking with ohlcv: {response.json()}")
    
    def get_stable_or_wrapped_tokens(self, token_type: str = 'stable') -> DataFrame:
        """
        token_type: stable or wrapped
        """
        if token_type not in ['stable', 'wrapped']:
            raise ValueError("token_type must be either stable or wrapped")
        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/tokens/{token_type}"), timeout=None
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get stable or wrapped tokens: {response.json()}")
    
    def get_exchanges_mapping_for_specific_symbol(self, market: str, symbol: str) -> DataFrame:
        """
        Get the exchanges for a specific symbol and market
        """
        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/markets/{market}/{symbol}"), timeout=None
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get exchange mappings: {response.json()}")
    
    def get_exchange_mappings_for_specific_exchange(self,market: str, exchange_name: str) -> DataFrame:
        """
        Get the exchanges for a specific exchange and market
        exchange_name: binance, kucoin, gate.io, bybit, bingx, bitget (lowercase)
        market: spot, futures
        """
        params = {
            "exchange_name": exchange_name.lower()
        }
        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/exchange_mappings/{market}"), timeout=None, params=params
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get exchange mappings: {response.json()}")
    
    def get_unique_quote_currencies(self, market: str) -> DataFrame:
        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/quote_currencies/{market}"), timeout=None
        )
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            return df
        else:
            raise Exception(f"Failed to get unique quote currencies: {response.json()}")
    
    def get_exchanges_list_for_specific_market(self, market: str) -> List[str]:
        """
        Get the list of exchanges for a specific market
        """
        response = self.client.get(
            urljoin(self.base_url, f"/v1/metrics/exchange_list/{market}"), timeout=None
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get exchanges list: {response.json()}")
    
    # -------------------- END OF MARKETCAP METRICS SERVICE ------------------------ #
    
    def verify(self, token: Union[str, None] = None) -> bool:
        if token is None:
            token = self.jwt
        response = self.client.get(
            self.base_url + "/v1/auth/verify",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        try:
            res = response.json()
            return res['result']['data']['json']
        except:
            return None
