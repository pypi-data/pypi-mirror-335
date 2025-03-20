import os 
import pandas as pd
from typing import Optional


class ValuationStatus:
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"


class PortfolioAnalysis:

    def __init__(self, data: dict, verbose: bool = False):
        self.data = data
        self._verbose = verbose
        if self.data:
            self._message = self.data.get("message", "No status message available")
            if 'errors' in self.data:
                self._status = ValuationStatus.PARTIAL_SUCCESS
            else:
                self._status = ValuationStatus.SUCCESS
            self._positions = self._convert_to_dataframe(self.data.get("positions", []), columns_to_drop=["calc_time"])
            self._cashflows = self._convert_to_dataframe(self.data.get("cashflows", []), columns_to_drop=["id"])
            self._dv01_buckets = self._convert_to_dataframe(self.data.get("dv01_buckets", []), columns_to_drop=["id"])
        else:
            self._status = ValuationStatus.FAILED
            self._message = "No data returned from the API."
            self._positions = pd.DataFrame()
            self._cashflows = pd.DataFrame()
            self._dv01_buckets = pd.DataFrame()
        if self._verbose:
            print(self.summary)

    def _convert_to_dataframe(self, data: list, columns_to_drop: Optional[list] = None) -> pd.DataFrame:
        """
        Converts a list of dictionaries to a pandas DataFrame.
        """
        df = pd.DataFrame(data)
        if columns_to_drop:
            df = df.drop(columns=columns_to_drop, errors='ignore')
        return df

    @property
    def status(self) -> str:
        """
        Returns the overall processing status message.
        """
        return self._status

    @property
    def positions(self) -> pd.DataFrame:
        """
        Returns positions as a pandas DataFrame.
        """
        return self._positions

    @property
    def cashflows(self) -> pd.DataFrame:
        """
        Returns cashflows as a pandas DataFrame.
        """
        return self._cashflows

    @property
    def dv01_buckets(self) -> pd.DataFrame:
        """
        Returns DV01 bucket data as a pandas DataFrame.
        """
        return self._dv01_buckets
    
    @property
    def summary(self) -> str:
        """
        Returns a summary of the analysis.
        """
        return (
            f"Status: {self._status}\n"
            f"Message: {self._message}\n"
            f"Total Positions: {len(self._positions)}\n"
            f"Positions with Errors: {len(self.data.get('errors', [])) if self.data else 0}\n"
            f"Total Cashflows: {len(self._cashflows)}\n"
            f"Total DV01 Buckets: {len(self._dv01_buckets)}\n"
        )

    def save_all_to_csv(self, folder: str ="kupala_val", prefix: str="portfolio_analysis") -> None:
        """
        Saves all key dataframes to CSV files.
        """
        self.save_to_csv(self.positions, os.path.join(folder, f"{prefix}_positions.csv"))
        self.save_to_csv(self.cashflows, os.path.join(folder,f"{prefix}_cashflows.csv"))
        self.save_to_csv(self.dv01_buckets, os.path.join(folder,f"{prefix}_dv01.csv"))

    def save_to_csv(self, df: pd.DataFrame, file_path: str) -> None:
        """
        Saves a DataFrame to a CSV file.
        """
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        df.to_csv(file_path, index=False)
        if self._verbose:
            print(f"Saved {file_path} with {len(df)} rows.")
