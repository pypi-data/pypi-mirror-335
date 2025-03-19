from api_client.python.public.crypticorn import Crypticorn

# reaad test_hive_client.py for more info

if __name__ == "__main__":
    client = Crypticorn(api_key="your_api_key_here")

    print("Testing create_model:")
    # print(client.create_model(coin_id=1, target="price"))

    print("Testing evaluate_model:")
    # data = pd.DataFrame(columns=["feature1"], data=[random.gauss(1, 0.02) for _ in range(500)])
    # data.to_parquet("data.parquet")
    # print(client.evaluate_model(model_id=1, data="data.parquet"))

    print("Testing download_data:")
    # print(client.download_data(model_id=1, feature_size="small"))

    print("Testing data_info:")
    # print(client.data_info())