import os
import pandas as pd

class SampleData:
    @classmethod
    def get_available_samples(cls) -> list:
        folder_path = os.path.dirname(__file__)
        return [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    @classmethod
    def get_sample_data(cls, sample_name:str ) -> pd.DataFrame:
        folder_path = os.path.dirname(__file__)
        file_path = os.path.join(folder_path, sample_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Sample data file '{sample_name}' not found.")

        df = pd.read_csv(file_path)
        return df
