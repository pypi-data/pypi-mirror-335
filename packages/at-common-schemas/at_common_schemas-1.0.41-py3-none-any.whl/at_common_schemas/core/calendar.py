from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class Dividends(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol")
	date: datetime = Field(..., description="Date when the dividend was issued")
	record_date: datetime | None = Field(..., description="Date by which investors must be on company records to receive the dividend")
	payment_date: datetime | None = Field(..., description="Date when the dividend payment is distributed to shareholders")
	declaration_date: datetime | None = Field(..., description="Date when the company's board announces the dividend")
	adj_dividend: float = Field(..., description="Dividend amount adjusted for stock splits and similar events")
	dividend: float = Field(..., description="Unadjusted dividend amount per share")
	yield_value: float = Field(..., alias="yield", description="Annual dividend expressed as a percentage of the stock price")
	frequency: str | None = Field(None, description="How often dividends are paid (e.g., quarterly, annually)")

class Earnings(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol")
	date: datetime = Field(..., description="Date of the earnings announcement")
	eps_actual: float | None = Field(None, description="Actual earnings per share reported")
	eps_estimated: float | None = Field(None, description="Analysts' consensus estimate for earnings per share")
	revenue_actual: float | None = Field(None, description="Actual revenue reported by the company")
	revenue_estimated: float | None = Field(None, description="Analysts' consensus estimate for company revenue")
	last_updated: datetime = Field(..., description="Timestamp of when this earnings data was last updated")

class Splits(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol")
	date: datetime = Field(..., description="Date when the stock split occurred")
	numerator: int | float = Field(..., description="Top number in the split ratio (e.g., 2 in a 2:1 split)")
	denominator: int | float = Field(..., description="Bottom number in the split ratio (e.g., 1 in a 2:1 split)")

class IPOs(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol for the IPO")
	date: datetime = Field(..., description="Date of the initial public offering")
	daa: datetime = Field(..., description="Date and time details of the IPO")
	company: str = Field(..., description="Name of the company going public")
	exchange: str = Field(..., description="Stock exchange where the IPO is listed")
	actions: str = Field(..., description="Actions related to the IPO process")
	shares: float | None = Field(None, description="Number of shares offered in the IPO")
	price_range: str | None = Field(None, description="Expected price range for the IPO shares")
	market_cap: float | None = Field(None, description="Estimated market capitalization at IPO")

class IPOsDisclosure(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol for the IPO")
	filing_date: datetime = Field(..., description="Date when IPO documents were filed with regulators")
	accepted_date: datetime = Field(..., description="Date when the IPO filing was accepted by regulators")
	effectiveness_date: datetime = Field(..., description="Date when the IPO registration became effective")
	cik: str = Field(..., description="Central Index Key identifier assigned by the SEC")
	form: str = Field(..., description="Type of regulatory form filed for the IPO")
	url: str = Field(..., description="Link to the IPO disclosure document")

class IPOsProspectus(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol for the IPO")
	accepted_date: datetime = Field(..., description="Date when the prospectus was accepted by regulators")
	filing_date: datetime = Field(..., description="Date when the prospectus was filed")
	ipo_date: datetime = Field(..., description="Official date of the initial public offering")
	cik: str = Field(..., description="Central Index Key identifier assigned by the SEC")
	price_public_per_share: float = Field(..., description="Offering price per share to the public")
	price_public_total: float = Field(..., description="Total value of shares offered to the public")
	discounts_and_commissions_per_share: float = Field(..., description="Underwriter fees and commissions per share")
	discounts_and_commissions_total: float = Field(..., description="Total underwriter fees and commissions")
	proceeds_before_expenses_per_share: float = Field(..., description="Net proceeds per share before other expenses")
	proceeds_before_expenses_total: float = Field(..., description="Total net proceeds before other expenses")
	form: str = Field(..., description="Type of regulatory form containing the prospectus")
	url: str = Field(..., description="Link to the prospectus document")