from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class CompanyProfile(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    price: float = Field(..., description="Current stock price")
    market_cap: float = Field(..., description="Total market value of the company's outstanding shares")
    beta: float = Field(..., description="Measure of stock volatility relative to the market")
    last_dividend: float = Field(..., description="Most recent dividend payment per share")
    range: str = Field(..., description="Price range (high/low) for a specific period")
    change: float = Field(..., description="Absolute price change")
    change_percentage: float = Field(..., description="Percentage price change")
    volume: int = Field(..., description="Number of shares traded in the current period")
    average_volume: int = Field(..., description="Average number of shares traded over a specific period")
    company_name: str = Field(..., description="Full legal name of the company")
    currency: str = Field(..., description="Currency in which the stock is traded")
    cik: str = Field(..., description="Central Index Key assigned by the SEC")
    isin: str = Field(..., description="International Securities Identification Number")
    cusip: str = Field(..., description="Committee on Uniform Securities Identification Procedures number")
    exchange_full_name: str = Field(..., description="Full name of the stock exchange")
    exchange: str = Field(..., description="Abbreviated name of the stock exchange")
    industry: str = Field(..., description="Industry classification of the company")
    website: str = Field(..., description="Company's official website URL")
    description: str = Field(..., description="Brief overview of the company's business")
    ceo: str = Field(..., description="Name of the Chief Executive Officer")
    sector: str = Field(..., description="Broader market sector classification")
    country: str = Field(..., description="Country where the company is headquartered")
    full_time_employees: str | None = Field(None, description="Number of full-time employees")
    phone: str | None = Field(None, description="Company's contact phone number")
    address: str | None = Field(None, description="Company's headquarters street address")
    city: str | None = Field(None, description="City of company headquarters")
    state: str | None = Field(None, description="State or province of company headquarters")
    zip: str | None = Field(None, description="Postal code of company headquarters")
    image: str | None = Field(None, description="URL to company logo or image")
    ipo_date: datetime | None = Field(None, description="Date of initial public offering")
    default_image: bool | None = Field(None, description="Indicates if a default image is being used")
    is_etf: bool = Field(..., description="Indicates if the security is an Exchange Traded Fund")
    is_actively_trading: bool = Field(..., description="Indicates if the stock is currently being traded")
    is_adr: bool = Field(..., description="Indicates if the security is an American Depositary Receipt")
    is_fund: bool = Field(..., description="Indicates if the security is an investment fund")

class CompanyNote(BaseSchema):
    cik: str = Field(..., description="Central Index Key assigned by the SEC")
    symbol: str = Field(..., description="Stock ticker symbol")
    title: str = Field(..., description="Title of the company note or filing")
    exchange: str = Field(..., description="Exchange where the stock is traded")

class StockPeer(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Full legal name of the company")
    price: float = Field(..., description="Current stock price")
    market_cap: int | float = Field(..., description="Total market value of the company's outstanding shares")

class DelistedCompany(BaseSchema):
    symbol: str = Field(..., description="Former stock ticker symbol")
    company_name: str = Field(..., description="Full legal name of the company")
    exchange: str = Field(..., description="Exchange where the stock was traded")
    ipo_date: datetime = Field(..., description="Date of initial public offering")
    delisted_date: datetime = Field(..., description="Date when the stock was removed from the exchange")

class EmployeeCount(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    cik: str = Field(..., description="Central Index Key assigned by the SEC")
    acceptance_time: datetime = Field(..., description="Time when the filing was accepted by the SEC")
    period_of_report: str = Field(..., description="Reporting period covered by the filing")
    company_name: str = Field(..., description="Full legal name of the company")
    form_type: str = Field(..., description="Type of SEC form filed")
    filing_date: datetime = Field(..., description="Date when the form was filed")
    employee_count: int = Field(..., description="Total number of employees reported")
    source: str = Field(..., description="Source of the employee count data")

class MarketCapitalization(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    date: datetime = Field(..., description="Date of the market capitalization data")
    market_cap: float = Field(..., description="Total market value of the company's outstanding shares")

class SharesFloat(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    date: datetime | None = Field(None, description="Date of the shares float data")
    free_float: float | None = Field(None, description="Percentage of shares available for public trading")
    float_shares: int | float | None = Field(None, description="Number of shares available for public trading")
    outstanding_shares: int | float | None = Field(None, description="Total number of shares issued by the company")

class MergerAcquisition(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol of the acquiring company")
    company_name: str = Field(..., description="Name of the acquiring company")
    cik: str = Field(..., description="Central Index Key of the acquiring company")
    targeted_company_name: str = Field(..., description="Name of the company being acquired")
    targeted_cik: str | None = Field(None, description="Central Index Key of the targeted company")
    targeted_symbol: str | None = Field(None, description="Stock ticker symbol of the targeted company")
    transaction_date: datetime = Field(..., description="Date when the transaction was announced")
    accepted_date: datetime = Field(..., description="Date when the transaction was completed or accepted")
    link: str = Field(..., description="URL to the official filing or announcement")

class Executive(BaseSchema):
    title: str = Field(..., description="Job title or position of the executive")
    name: str = Field(..., description="Full name of the executive")
    pay: float | None = Field(None, description="Total compensation amount")
    currency_pay: str = Field(..., description="Currency of the compensation")
    gender: str = Field(..., description="Gender of the executive")
    year_born: int | None = Field(None, description="Birth year of the executive")
    active: bool | None = Field(None, description="Indicates if the executive is currently active")

class ExecutiveCompensation(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Full legal name of the company")
    filing_date: datetime = Field(..., description="Date when the compensation was filed")
    accepted_date: datetime = Field(..., description="Date when the filing was accepted")
    name_and_position: str = Field(..., description="Name and position of the executive")
    year: int = Field(..., description="Fiscal year of the compensation")
    salary: float = Field(..., description="Base salary amount")
    bonus: float = Field(..., description="Cash bonus amount")
    stock_award: float = Field(..., description="Value of stock-based compensation")
    option_award: float | None = Field(None, description="Value of stock options granted")
    incentive_plan_compensation: float = Field(..., description="Performance-based incentive compensation")
    all_other_compensation: float = Field(..., description="Additional compensation not in other categories")
    total: float = Field(..., description="Total compensation amount")
    link: str = Field(..., description="URL to the official filing document")

class ExecutiveCompensationBenchmark(BaseSchema):
    industry_title: str = Field(..., description="Industry sector or classification")
    year: int = Field(..., description="Year of the benchmark data")
    average_compensation: float = Field(..., description="Average executive compensation for the industry")