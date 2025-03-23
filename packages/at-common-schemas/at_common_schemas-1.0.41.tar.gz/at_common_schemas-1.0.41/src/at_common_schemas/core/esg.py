from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class ESGDisclosureItem(BaseSchema):
    date: datetime = Field(..., description="Date when the ESG disclosure was published")
    accepted_date: datetime = Field(..., description="Date when the ESG disclosure was officially accepted or processed")
    symbol: str = Field(..., description="Stock ticker symbol of the company")
    cik: str = Field(..., description="Central Index Key (CIK) identifier assigned by the SEC")
    company_name: str = Field(..., description="Full legal name of the company")
    form_type: str = Field(..., description="Type of regulatory form submitted (e.g., 10-K, 10-Q)")
    environmental_score: float = Field(..., description="Numerical score assessing the company's environmental performance")
    social_score: float = Field(..., description="Numerical score assessing the company's social responsibility performance")
    governance_score: float = Field(..., description="Numerical score assessing the company's governance practices")
    esg_score: float = Field(..., description="Composite score combining environmental, social, and governance metrics")
    url: str = Field(..., description="Web address where the ESG disclosure document can be accessed")

class ESGRatingItem(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol of the company")
    cik: str = Field(..., description="Central Index Key (CIK) identifier assigned by the SEC")
    company_name: str = Field(..., description="Full legal name of the company")
    industry: str = Field(..., description="Industry classification of the company")
    fiscal_year: int = Field(..., description="Fiscal year for which the ESG rating applies")
    esg_risk_rating: str = Field(..., description="Qualitative assessment of the company's ESG risk level")
    industry_rank: str = Field(..., description="Company's ESG performance ranking within its industry")

class ESGBenchmarkItem(BaseSchema):
    fiscal_year: int = Field(..., description="Fiscal year for which the benchmark data applies")
    sector: str = Field(..., description="Economic sector classification for the benchmark")
    environmental_score: float = Field(..., description="Average environmental score for companies in this sector")
    social_score: float = Field(..., description="Average social responsibility score for companies in this sector")
    governance_score: float = Field(..., description="Average governance score for companies in this sector")
    esg_score: float = Field(..., description="Average composite ESG score for companies in this sector")