import pandas as pd
import os
def get_data(input_data):
    df = pd.read_csv(input_data)
    return df

# print(os.getcwd())


