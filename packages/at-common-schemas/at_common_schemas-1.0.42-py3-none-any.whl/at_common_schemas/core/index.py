from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class Index(BaseSchema):
    symbol: str = Field(..., description="The ticker symbol of the index")
    name: str = Field(..., description="The full name of the index")
    exchange: str = Field(..., description="The exchange where the index is listed")
    currency: str = Field(..., description="The currency in which the index is denominated")

class IndexConstituent(BaseSchema):
    symbol: str = Field(..., description="The ticker symbol of the constituent")
    name: str = Field(..., description="The full name of the constituent company")
    sector: str = Field(..., description="The industry sector of the constituent")
    sub_sector: str = Field(..., description="The specific sub-sector or industry group of the constituent")
    head_quarter: str = Field(..., description="The location of the constituent company's headquarters")
    date_first_added: datetime | None = Field(None, description="The date when the constituent was first added to the index")
    cik: str = Field(..., description="The Central Index Key (CIK) identifier assigned by the SEC")
    founded: datetime | None = Field(None, description="The year or date when the constituent company was founded")