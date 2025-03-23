from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class Stock(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol used for identifying publicly traded companies")
    name: str = Field(..., description="Official name of the company")

class ETF(BaseSchema):
    symbol: str = Field(..., description="ETF ticker symbol used for identifying exchange-traded funds")
    name: str = Field(..., description="Official name of the ETF company")

class Exchange(BaseSchema):
    name: str = Field(..., description="Exchange code or identifier where securities are traded")

class Sector(BaseSchema):
    name: str = Field(..., description="Broad market sector classification for categorizing companies")

class Industry(BaseSchema):
    name: str = Field(..., description="Specific industry classification within a broader sector")

class Country(BaseSchema):
    name: str = Field(..., description="Country name")

class FinancialStatementSymbol(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol used for trading identification")
    company_name: str = Field(..., description="Official company or entity name")
    trading_currency: str | None = Field(None, description="Currency code used for stock trading transactions")
    reporting_currency: str | None = Field(None, description="Currency code used in the company's financial statements")

class CIK(BaseSchema):
    cik: str = Field(..., description="Central Index Key (CIK) unique identifier assigned by the SEC to entities that file disclosures")
    company_name: str = Field(..., description="Official company or entity name")

class SymbolChange(BaseSchema):
    date: datetime = Field(..., description="Date when the ticker symbol change occurred")
    company_name: str = Field(..., description="Official company or entity name")
    old_symbol: str = Field(..., description="Previous ticker symbol before the change")
    new_symbol: str = Field(..., description="Current ticker symbol after the change")

class EarningsTranscript(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol used for trading identification")
    company_name: str = Field(..., description="Official company or entity name")
    no_of_transcripts: int = Field(..., description="Total count of available earnings call transcripts")