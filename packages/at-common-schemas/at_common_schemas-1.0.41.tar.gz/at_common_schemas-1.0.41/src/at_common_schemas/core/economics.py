from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class TreasuryRate(BaseSchema):
    date: datetime = Field(..., description="The date for which these U.S. Treasury yield rates are reported")
    month_1: float = Field(..., description="The yield rate for 1-month U.S. Treasury securities, expressed as a percentage")
    month_2: float = Field(..., description="The yield rate for 2-month U.S. Treasury securities, expressed as a percentage")
    month_3: float = Field(..., description="The yield rate for 3-month U.S. Treasury securities, expressed as a percentage")
    month_6: float = Field(..., description="The yield rate for 6-month U.S. Treasury securities, expressed as a percentage")
    year_1: float = Field(..., description="The yield rate for 1-year U.S. Treasury securities, expressed as a percentage")
    year_2: float = Field(..., description="The yield rate for 2-year U.S. Treasury securities, expressed as a percentage")
    year_3: float = Field(..., description="The yield rate for 3-year U.S. Treasury securities, expressed as a percentage")
    year_5: float = Field(..., description="The yield rate for 5-year U.S. Treasury securities, expressed as a percentage")
    year_7: float = Field(..., description="The yield rate for 7-year U.S. Treasury securities, expressed as a percentage")
    year_10: float = Field(..., description="The yield rate for 10-year U.S. Treasury securities, expressed as a percentage")
    year_20: float = Field(..., description="The yield rate for 20-year U.S. Treasury securities, expressed as a percentage")
    year_30: float = Field(..., description="The yield rate for 30-year U.S. Treasury securities, expressed as a percentage")

class EconomicIndicator(BaseSchema):
    name: str = Field(..., description="The identifier or name of the economic indicator")
    date: datetime = Field(..., description="The date associated with the economic indicator measurement")
    value: float = Field(..., description="The numerical value of the economic indicator")

class EconomicCalendarItem(BaseSchema):
    event: str = Field(..., description="The name or title of the economic event or data release")
    date: datetime = Field(..., description="The date when the economic event occurred or is scheduled")
    country: str = Field(..., description="The country or region to which this economic event pertains")
    actual: float | None = Field(None, description="The officially reported value of the economic indicator, if available")
    previous: float | None = Field(None, description="The previously reported value for this economic indicator")
    change: float | None = Field(None, description="The numerical difference between the actual and previous values")
    estimate: float | None = Field(None, description="The consensus forecast value prior to the official release")
    impact: str = Field(..., description="The assessed significance of the economic event's market impact")

class MarketRiskPremiumItem(BaseSchema):
    country: str = Field(..., description="The country or market identifier for this risk premium data")
    continent: str = Field(..., description="The continent where the specified country is located")
    country_risk_premium: float = Field(..., description="The country-specific risk premium component")
    total_equity_risk_premium: float = Field(..., description="The aggregate equity risk premium for this market")