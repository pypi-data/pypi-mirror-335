from typing import List
from datetime import datetime
from pydantic import Field
from at_common_schemas.base import BaseSchema
from at_common_schemas.core.news import News

# Latest General News
class NewsLatestGeneralNewsListRequest(BaseSchema):
    date_from: datetime = Field(..., description="The start date of the news articles to retrieve")
    date_to: datetime = Field(..., description="The end date of the news articles to retrieve")
    limit: int = Field(..., description="Maximum number of news articles to retrieve")

class NewsLatestGeneralNewsListResponse(BaseSchema):
    items: List[News] = Field(..., description="List of market news articles")

# Latest Stock News
class NewsLatestStockNewsListRequest(BaseSchema):
    date_from: datetime = Field(..., description="The start date of the news articles to retrieve")
    date_to: datetime = Field(..., description="The end date of the news articles to retrieve")
    limit: int = Field(..., description="Maximum number of news articles to retrieve")

class NewsLatestStockNewsListResponse(BaseSchema):
    items: List[News] = Field(..., description="List of stock-specific news articles")

# Latest Crypto News
class NewsLatestCryptoNewsListRequest(BaseSchema):
    date_from: datetime = Field(..., description="The start date of the news articles to retrieve")
    date_to: datetime = Field(..., description="The end date of the news articles to retrieve")
    limit: int = Field(..., description="Maximum number of news articles to retrieve")

class NewsLatestCryptoNewsListResponse(BaseSchema):
    items: List[News] = Field(..., description="List of crypto-specific news articles")

# Latest Forex News
class NewsLatestForexNewsListRequest(BaseSchema):
    date_from: datetime = Field(..., description="The start date of the news articles to retrieve")
    date_to: datetime = Field(..., description="The end date of the news articles to retrieve")
    limit: int = Field(..., description="Maximum number of news articles to retrieve")

class NewsLatestForexNewsListResponse(BaseSchema):
    items: List[News] = Field(..., description="List of forex-specific news articles")
    
# Search News by stock symbol
class NewsStockSearchRequest(BaseSchema):
    symbol: str = Field(..., description="The stock ticker symbol to search for")
    date_from: datetime = Field(..., description="The start date of the news articles to retrieve")
    date_to: datetime = Field(..., description="The end date of the news articles to retrieve")
    limit: int = Field(..., description="Maximum number of news articles to retrieve")

class NewsStockSearchResponse(BaseSchema):
    items: List[News] = Field(..., description="List of stock-specific news articles")