from typing import Any
import pandas as pd
import requests
import os
from crypticorn.hive.utils import download_file, SingleModel, ModelEvaluation, DataInfo


class HiveClient:
    """
    A client for interacting with the Crypticorn Hive API, offering functionality to create and evaluate models,
    download data, and retrieve information about available coins, targets, and features.
    """

    def __init__(self, base_url='https://api.crypticorn.com', api_key: str = None, jwt: str = None):
        """@private
        Initializes the Crypticorn Hive API client with an API key.

        :param api_key: The API key required for authenticating requests.
        """
        self._base_url = base_url + "/v1/hive"
        self._headers = {"Authorization": f"ApiKey {api_key}"}

    def create_model(self, coin_id: int, target: str) -> SingleModel:
        """
        Creates a new model based on the specified coin_id and target.

        :param coin_id: The id of the coin to be used for the model.
        :param target: The target variable for the model.
        """
        endpoint = "/model/creation"
        response = requests.post(
            url=self._base_url + endpoint,
            params={"coin_id": coin_id, "target": target},
            headers=self._headers
        )
        return response.json()

    def evaluate_model(self, model_id: int, data: Any, version: float = None) -> ModelEvaluation:
        """
        Evaluates an existing model using the provided data.

        :param model_id: The id of the model to evaluate.
        :param data: The data to use for evaluation, which can be a pandas DataFrame or a file path with
                 extensions `.feather` or `.parquet`.
        :param version: (optional) Specifies the data version for evaluation. Defaults to the latest version.
                If a different version than the latest is specified, the evaluation will not be stored
                or counted on the leaderboard. This is useful for testing your model with different versions.
                Ensure to specify a `version` if your model was trained on older data versions; otherwise,
                it will be evaluated against the latest data, potentially affecting the results.
        """
        if isinstance(data, pd.DataFrame):
            json_data = data.to_json(orient='records')
        elif isinstance(data, str):
            if data.endswith('.feather'):
                json_data = pd.read_feather(data).to_json(orient="records")
            elif data.endswith('.parquet'):
                json_data = pd.read_parquet(data).to_json(orient="records")
            else:
                raise ValueError("Unsupported file format. Use .feather, .parquet, or pd.Dataframe.")
        else:
            raise ValueError("Unsupported data format. Pass a pd.DataFrame or a valid file path.")

        endpoint = "/model/evaluation"
        response = requests.post(
            url=self._base_url + endpoint,
            params={"model_id": model_id, "version": version},
            json=json_data,
            headers=self._headers
        )
        return response.json()

    def download_data(self, model_id: int, version: float = None,
                      feature_size: str = None) -> int:
        """
        Downloads training data for models.
        Either pass a model_id or coin_id. For more details about available data, use `data_info()`.

        :param model_id: id of the model to download data for.
        :param version: (optional) Data version to download. Defaults to the latest version if not specified.
        :param feature_size: (optional) Size of the feature set to download. Default is "large".
        """
        endpoint = "/data"
        response = requests.get(
            url=self._base_url + endpoint,
            params={"feature_size": feature_size, "version": version, "model_id": model_id},
            headers=self._headers
        )
        if response.status_code != 200:
            return response.json()
        data = response.json()
        base_path = f"v{data['version']}/coin_{data['coin']}/"
        os.makedirs(base_path, exist_ok=True)
        download_file(url=data["y_train"], dest_path=f"{base_path}y_train_{data['target']}.feather")
        download_file(url=data["X_test"], dest_path=f"{base_path}X_test_{data['feature_size']}.feather")
        download_file(url=data["X_train"], dest_path=f"{base_path}X_train_{data['feature_size']}.feather")
        return 200

    def data_info(self) -> DataInfo:
        """
        Returns information about the training data.
        Useful in combination with `download_data()` and `create_model()`.
        """
        endpoint = "/data/info"
        response = requests.get(
            url=self._base_url + endpoint,
            headers=self._headers)
        return response.json()
