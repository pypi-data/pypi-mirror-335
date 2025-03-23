from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class ETFHolding(BaseSchema):
    symbol: str = Field(..., description="Ticker symbol of the holding")
    asset: str = Field(..., description="Type of asset held in the ETF")
    name: str = Field(..., description="Full name of the holding")
    isin: str = Field(..., description="International Securities Identification Number")
    security_cusip: str = Field(..., description="CUSIP identifier for the security")
    shares_number: int | float = Field(..., description="Number of shares of this holding in the ETF")
    weight_percentage: float = Field(..., description="Percentage weight of this holding in the ETF portfolio")
    market_value: float = Field(..., description="Current market value of this holding")
    updated_at: datetime = Field(..., description="Date when this holding data was last updated")
    updated: datetime = Field(..., description="Date when this holding information was last refreshed")

class ETFInfoSector(BaseSchema):
    industry: str = Field(..., description="Name of the industry sector")
    exposure: float = Field(..., description="Percentage exposure to this industry sector")

class ETFInfo(BaseSchema):
    symbol: str = Field(..., description="Ticker symbol of the ETF")
    name: str = Field(..., description="Full name of the ETF")
    description: str = Field(..., description="Detailed description of the ETF's investment strategy and objectives")
    isin: str = Field(..., description="International Securities Identification Number")
    asset_class: str = Field(..., description="Primary asset class of the ETF (e.g., equity, fixed income)")
    security_cusip: str = Field(..., description="CUSIP identifier for the ETF")
    domicile: str = Field(..., description="Country where the ETF is legally domiciled")
    website: str = Field(..., description="Official website URL for the ETF")
    etf_company: str = Field(..., description="Name of the company managing the ETF")
    expense_ratio: float = Field(..., description="Annual management fee as a percentage of assets")
    assets_under_management: float = Field(..., description="Total value of assets managed by the ETF")
    avg_volume: float = Field(..., description="Average daily trading volume")
    inception_date: datetime = Field(..., description="Date when the ETF was first launched")
    nav: float = Field(..., description="Net Asset Value per share")
    nav_currency: str = Field(..., description="Currency in which the NAV is denominated")
    holdings_count: int = Field(..., description="Total number of individual holdings in the ETF")
    updated_at: datetime = Field(..., description="Date when this ETF data was last updated")
    sectors_list: list[ETFInfoSector] = Field(..., description="List of industry sectors and their allocations within the ETF")

class ETFCountryWeight(BaseSchema):
    country: str = Field(..., description="Name of the country")
    weight_percentage: str = Field(..., description="Percentage allocation to this country in the ETF")

class ETFAssetExposure(BaseSchema):
    symbol: str = Field(..., description="Ticker symbol of the asset")
    asset: str = Field(..., description="Type or name of the asset")
    shares_number: int = Field(..., description="Number of shares held of this asset")
    weight_percentage: float = Field(..., description="Percentage weight of this asset in the ETF")
    market_value: float = Field(..., description="Current market value of this asset holding")

class ETFSectorWeight(BaseSchema):
    symbol: str = Field(..., description="Ticker symbol of the ETF")
    sector: str = Field(..., description="Name of the industry sector")
    weight_percentage: float = Field(..., description="Percentage allocation to this sector in the ETF")