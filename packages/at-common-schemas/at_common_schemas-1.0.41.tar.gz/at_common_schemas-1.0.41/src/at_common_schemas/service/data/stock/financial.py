from typing import List
from pydantic import Field
from at_common_schemas.base import BaseSchema
from at_common_schemas.core.financial import (
    FinancialPeriod, FinancialCashFlowStatement, FinancialBalanceSheetStatement, FinancialIncomeStatement, 
    FinancialIncomeStatementGrowth, FinancialBalanceSheetStatementGrowth, FinancialCashFlowStatementGrowth, FinancialGrowth,
    FinancialKeyMetrics, FinancialKeyMetricsTTM, FinancialRatios, FinancialRatiosTTM
)

# Batch request and response for financial income statements
class FinancialIncomeStatementListRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the request.")
    period: FinancialPeriod = Field(..., description="The financial period for the request.")
    limit: int = Field(..., description="The limit on the number of results returned.")

class FinancialIncomeStatementListResponse(BaseSchema):
    items: List[FinancialIncomeStatement] = Field(..., description="List of financial income statements.")

# Batch request and response for financial balance sheets statements
class FinancialBalanceSheetStatementListRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the request.")
    period: FinancialPeriod = Field(..., description="The financial period for the request.")
    limit: int = Field(..., description="The limit on the number of results returned.")

class FinancialBalanceSheetStatementListResponse(BaseSchema):
    items: List[FinancialBalanceSheetStatement] = Field(..., description="List of financial balance sheets statements.")

# Batch request and response for financial cash flows statements
class FinancialCashFlowStatementListRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the request.")
    period: FinancialPeriod = Field(..., description="The financial period for the request.")
    limit: int = Field(..., description="The limit on the number of results returned.")

class FinancialCashFlowStatementListResponse(BaseSchema):
    items: List[FinancialCashFlowStatement] = Field(..., description="List of financial cash flows statements.")

# Batch request and response for financial income statement growths
class FinancialIncomeStatementGrowthListRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the request.")
    period: FinancialPeriod = Field(..., description="The financial period for the request.")
    limit: int = Field(..., description="The limit on the number of results returned.")

class FinancialIncomeStatementGrowthListResponse(BaseSchema):
    items: List[FinancialIncomeStatementGrowth] = Field(..., description="List of financial income statement growths.")

# Batch request and response for financial balance sheet statement growths
class FinancialBalanceSheetStatementGrowthListRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the request.")
    period: FinancialPeriod = Field(..., description="The financial period for the request.")
    limit: int = Field(..., description="The limit on the number of results returned.")

class FinancialBalanceSheetStatementGrowthListResponse(BaseSchema):
    items: List[FinancialBalanceSheetStatementGrowth] = Field(..., description="List of financial balance sheet statement growths.")

# Batch request and response for financial cash flow statement growths
class FinancialCashFlowStatementGrowthListRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the request.")
    period: FinancialPeriod = Field(..., description="The financial period for the request.")
    limit: int = Field(..., description="The limit on the number of results returned.")

class FinancialCashFlowStatementGrowthListResponse(BaseSchema):
    items: List[FinancialCashFlowStatementGrowth] = Field(..., description="List of financial cash flow statement growths.")

# request and response for financial growths
class FinancialGrowthGetRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the request.")

class FinancialGrowthGetResponse(FinancialGrowth):
    pass

# Batch request and response for financial key metrics
class FinancialAnalysisKeyMetricListRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the request.")
    period: FinancialPeriod = Field(..., description="The financial period for the request.")
    limit: int = Field(..., description="The limit for the number of results.")

class FinancialAnalysisKeyMetricListResponse(BaseSchema):
    items: List[FinancialKeyMetrics] = Field(..., description="List of key metrics for the stock.")

class FinancialAnalysisKeyMetricTTMGetRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the TTM request.")

class FinancialAnalysisKeyMetricTTMGetResponse(FinancialKeyMetricsTTM):
    pass

# Batch request and response for financial ratios
class FinancialAnalysisRatioListRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the request.")
    period: FinancialPeriod = Field(..., description="The financial period for the request.")
    limit: int = Field(..., description="The limit for the number of results.")

class FinancialAnalysisRatioListResponse(BaseSchema):
    items: List[FinancialRatios] = Field(..., description="List of financial ratios for the stock.")

class FinancialAnalysisRatioTTMGetRequest(BaseSchema):
    symbol: str = Field(..., description="The stock symbol for the TTM request.")

class FinancialAnalysisRatioTTMGetResponse(FinancialRatiosTTM):
    pass