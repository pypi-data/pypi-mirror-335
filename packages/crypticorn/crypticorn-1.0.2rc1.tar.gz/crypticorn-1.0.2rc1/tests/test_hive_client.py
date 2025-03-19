from api_client.python.client import HiveClient
import random
import pandas as pd

### Local Testing
# Run app.py locally and use the token from the browser cookies to test the client
# Set Crypticorn base URL to localhost
# Use the following code to test within the hive-service repo for better workflow

if __name__ == "__main__":
    client = HiveClient(token="")
    
    print("Testing create_account:")
    #print(client.create_account())
    
    print("\nTesting create_model:")
    #print(client.create_model(1, "Hoth"))

    print("\nTesting evaluate_model:")
    # data = pd.DataFrame(columns=["feature1"], data=[random.gauss(1,0.02) for _ in range(4986)])
    # data.to_json("data.parquet")
    #print(client.evaluate_model(35, data))

    print("\nTesting get_specific_model:")
    # print(client.get_model(model_id=2))
    
    print("\nTesting get_all_models:")
    #print(client.get_model())
    
    print("\nTesting delete_model:")
    #print(client.delete_model(model_id=1))

    print("\nTesting get_leaderboard:")
    #print(client.get_leaderboard())

    print("\nTesting generate_api_key:")
    #print(client.generate_api_key())

    print("\nTesting delete_api_key:")
    #print(client.delete_api_key())

    print("\nTesting data_info:")
    #print(client.data_info())

    print("\nTesting update_username")
    #print(client.update_username("Mister Y"))

    print("\nTesting download_data:")
    #print(client.download_data(model_id=1, feature_size="small"))

    print("\nTesting get_account_info by model_id:")
    #print(client.get_account_info(user_id="nbZ05EjKfjXjWt0S07o9"))
    
    print("\nTesting get_account_info by username:")
    #print(client.get_account_info(user_id="mateh"))
    
    print("\nTesting get_account_info (current user):")
    #print(client.get_account_info())
