# Kupala Val

Kupala Val is a Python package that serves as an API wrapper around [Kupala-Nich.com](https://kupala-nich.com). It provides easy-to-use interfaces for obtaining valuations, cashflows, and bucketed DV01 (dollar value of a basis point) for portfolios of both listed and derivative financial products.

## Features

- Portfolio valuation for listed and derivative products
- Cashflow analysis and projections
- Bucketed DV01 sensitivity analysis
- Support for both CSV files and pandas DataFrames


## Supported Instruments

As of this release, only OIS Swaps referencing SOFR, ESTR, SONIA, CORRA, TONA, TIIE ON, SARON, and SORA, along with listed instruments available via the YFinance API, are supported. This list will expand over time. Since all valuations are performed through a remote API, updates to supported instruments will be seamless. Users do not need to modify their `kupala_val` installations to access new products as they become available.

To see full list of supported products, please refer to valuations Page on [Kupala-Nich.com](https://kupala-nich.com).  To inquire about specific instrument support, please contact me at maksim.kozyarchuk@gmail.com

## Valuation Methodology

Kupala-Nich values OIS Swaps and other OTC products using QuantLib. The valuation curves are constructed from trade data reported via DTCC GTR feeds and overnight rates (OR) retrieved from relevant central banks. Curve data has been maintained since January 2025, while overnight rates have been backfilled to April 2024.

Listed instruments are valued using data provided by the YFinance API.  


## Installation

```bash
pip install kupala_val
```

## Getting Started

### Prerequisites

To use this library, you need:

1. A free account on [Kupala-Nich.com](https://kupala-nich.com)
2. An API key (available in the settings menu in the top right corner after login)

## Usage Examples

### Working with CSV files

```python
from kupala_val import KupalaVal, ValuationStatus

# Create an instance of KupalaVal object with an API Key
val = KupalaVal(API_KEY, vebose=True)

# Upload portfolio.csv to kupala-nich valuation service, 
# will return portfolio valuation, cashflows and dv01_buckets data
pa = val.analyze( csv_file_path=r"/path/to/portfolio.csv")

# Save recieved data to csv files in specified folder
if pa.status in [ValuationStatus.SUCCESS, ValuationStatus.PARTIAL_SUCCESS]:
    pa.save_all_to_csv(folder=r"kupala_val")

```

### Working with SampleFiles and pandas DataFrames

```python
from kupala_val import KupalaVal, SampleData

# List available sample files. i.e. ois_sample.csv, multi_asset_sample.csv
print(SampleData.get_available_samples())

# Load multi_asset_sample.csv into a DataFrame
df = SampleData.get_sample_data('multi_asset_sample.csv')

# Get valuations for positions in dataframe
val = KupalaVal(API_KEY)
pa = val.analyze(df=df)

# Print returned dataframes 
print(pa.positions)
print(pa.cashflows)
print(pa.dv01_buckets)

```

## API Documentation

To obtain valuations for a portfolio of positions, please provide the following information in the CSV file or DataFrame format. For upto date API documentation, please visit valuations section [Kupala-Nich.com](https://kupala-nich.com):

| Field                | Required / Optional                | Description                                                                                                             |
|----------------------|------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| `product`            | **Required**                       | Product type (`OISSwap`; `Listed`; `Cash` are supported)                                                                |
| `position_id`        | Optional                           | Unique identifier for the position                                                                                      |
| `symbol`             | **Required** *(for Listed and Cash)* | Currency code or ticker recognized by Yahoo Finance                                                                     |
| `quantity`           | **Required** *(for Listed and Cash)* | Number of shares or cash amount. Treated as absolute value; use `direction` to indicate sign                            |
| `cost`               | Optional *(for Listed)*            | Cost prices to subtract from market price when calculating NPV                                                          |
| `template`           | **Required** *(for Swaps)*               | Can be `curve_name`, `upi`, `upi_underlier`, or `upi_fsin`. Refer to the template list for available templates          |
| `direction`          | **Required**                       | One of `Receive Fixed`, `Pay Fixed`, `Buy`, `Sell`                                                                       |
| `notional`           | **Required**  *(for Swaps)*         | Principal amount                                                                                                        |
| `effective_date`     | Optional                           | If not provided, defaults to current day plus settlement day offset for the curve; format `YYYY-MM-DD`                  |
| `maturity_date`      | **Required**   *(for Swaps)*         | Maturity date; can be expressed as tenor (e.g., `10Y`) or date (`YYYY-MM-DD`)                                           |
| `roll_period`        | Optional                           | Defaults from template if not provided                                                                                  |
| `fixed_rate`         | **Required**  *(for Swaps)*        | Fixed rate as a percentage (0 to 100%); e.g., `4.06%`                                                                   |
| `price_date`         | Optional                           | Valuation date in `YYYY-MM-DD` format                                                                                   |
| `roll_type`          | Optional                           | Roll type; valid options: `Standard`, `IMM`, `EOM`                                                                      |
| `stub_type`          | Optional                           | Stub type; valid options: `ShortInitial`, `ShortFinal`, `LongInitial`, `LongFinal`                                      |
| `roll_conv`          | Optional                           | Roll convention; valid options: `Following`, `ModifiedFollowing`, `Preceding`, `ModifiedPreceding`, `Unadjusted`        |
| `term_roll_conv`     | Optional                           | Term roll convention; same valid options as `roll_conv`                                                                 |
| `payment_lag`        | Optional                           | Payment lag in days                                                                                                     |
| `averaging_method`   | Optional                           | Averaging method; valid options: `Simple`, `Compounded`                                                                 |
| `lookback_days`      | Optional                           | Lookback days for fixings                                                                                               |


## License

This project is licensed under the MIT License - see the LICENSE file for details.

