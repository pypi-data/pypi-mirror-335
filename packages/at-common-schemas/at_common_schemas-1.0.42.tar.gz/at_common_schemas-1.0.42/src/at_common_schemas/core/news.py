from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime
from typing import List

class News(BaseSchema):
	symbols: List[str] | None = Field(None, description="Stock symbol related to the news item, if applicable")
	published_date: datetime = Field(..., description="Date and time when the news was published")
	publisher: str = Field(..., description="Name of the news publisher or organization")
	headline: str = Field(..., description="Headline or title of the news item")
	summary: str = Field(..., description="Summary or full content of the news item")
	image: str | None = Field(None, description="URL or path to the news item's featured image, if available")
	original_site: str = Field(..., description="Source website or platform where the news was published")
	original_url: str = Field(..., description="Direct link to the original news article")