import unittest
from kupala_val import KupalaVal, ValuationStatus, SampleData
import pandas as pd

class KupalaValUnderTest(KupalaVal):
    def __init__(self, api_key: str, verbose: bool = False, 
                 positions: list = [], cashflows: list = [], dv01_buckets: list = []):
        super().__init__(api_key, verbose)
        self._called_with = None
        self._positions = positions
        self._cashflows = cashflows
        self._dv01_buckets = dv01_buckets

    def _call_api(self, msg: list ) -> dict:
        self._called_with = msg
        return  {
            'positions':self._positions,
            'cashflows':self._cashflows,
            'dv01_buckets':self._dv01_buckets,
        }


def get_test_dataframe():
    data = {
        'product': ['oisswap', 'listed'],
        'template': ['USD-SOFR-OIS', ''],
        'direction': ['pay fixed', 'sell'],
        'quantity': ['', 200_000],
        'notional': [1_000_000,'' ],
        'maturity_date': ['2025-01-01', ''],
        'fixed_rate': ["5%", ''],
        'price_date': ['LATEST', 'LATEST']
    }
    return pd.DataFrame(data)

class TestKupalaVal(unittest.TestCase):
    
    def test_happy_path(self):
        api = KupalaValUnderTest('test_key'
                                 , positions=[{'product': 'oisswap',},
                                             {'product': 'listed', }],)
        df = get_test_dataframe()
        res = api.analyze(df=df)
        called_with_positions = api._called_with['positions']
        self.assertEqual(len(called_with_positions), 2)
        self.assertEqual(called_with_positions[0]['product'], 'oisswap')
        self.assertEqual(called_with_positions[1]['product'], 'listed')
        self.assertEqual(res.status, ValuationStatus.SUCCESS)
        self.assertEqual(res.positions.shape[0], 2)
        self.assertEqual(res.cashflows.shape[0], 0)
        self.assertEqual(res.dv01_buckets.shape[0], 0)
    
    def test_invalid_csv(self):
        api = KupalaValUnderTest('test_key')
        with self.assertRaises(ValueError):
            api.analyze(csv_file_path='invalid.csv')
    
    def test_invalid_dataframe(self):
        api = KupalaValUnderTest('test_key')
        df = pd.DataFrame({'invalid_column': [1, 2, 3]})
        with self.assertRaises(ValueError):
            api.analyze(df=df)
    
    def test_invalid_fixed_rate(self):
        api = KupalaValUnderTest('test_key')
        df = pd.DataFrame({'product': ['lisited','oisswap','oisswap'],
                           'direction': ['sell','pay fixed','pay fixed'],
                           'fixed_rate': ['invalid', "invalid", "5%"],
        })
        with self.assertRaises(ValueError):
            api.analyze(df=df)



if __name__ == "__main__":
    unittest.main()