# at-common-schemas

Common schema definitions used by Apex Trader services, built with Pydantic.

## Installation
```bash
pip install at-common-schemas
```

## Features

- Standardized data models for financial market data
- Built with Pydantic for robust data validation
- Comprehensive type hints and documentation
- Automatic serialization of datetime and enum values

## Available Schemas

### Stock Data
- Profile information
- Real-time quotes
- Daily candlestick data
- Technical indicators
- Financial statements
  - Balance Sheet
  - Income Statement
  - Cash Flow
- Financial analysis
  - Key metrics
  - Financial ratios
  - TTM (Trailing Twelve Months) metrics
- Earnings call transcripts

### Market Data
- Stock symbols by exchange
- Market news
- Company-specific news
- Calendar events
  - Earnings announcements
  - Dividend declarations
  - Stock splits

## Usage Examples

### Fetching Stock Quote Data
```python
from at_common_schemas.service.data.stock.quote import StockQuoteRequest, StockQuoteResponse

# Single stock quote request
request = StockQuoteRequest(symbol="AAPL")

# Batch quote request
batch_request = StockQuoteBatchRequest(symbols=["AAPL", "MSFT", "GOOGL"])
```

### Working with Financial Statements
```python
from at_common_schemas.service.data.stock.financial import StockFinancialStatementBatchRequest
from at_common_schemas.common.stock import StockFinancialPeriod

request = StockFinancialStatementBatchRequest(
    symbol="AAPL",
    period=StockFinancialPeriod.QUARTERLY,
    limit=4
)
```

## Development

Requirements:
- Python 3.11+
- pydantic 2.10.6+
- annotated-types 0.7.0+
- typing_extensions 4.12.2+

## License
This project is licensed for private use and internal purposes only. Redistribution or modification is not permitted without prior consent.

## Contributing
Contributions are welcome for internal use only. Please ensure that any changes adhere to the project's coding standards and are reviewed before submission.
