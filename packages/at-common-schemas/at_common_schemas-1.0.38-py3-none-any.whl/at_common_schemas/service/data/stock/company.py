from at_common_schemas.base import BaseSchema
from at_common_schemas.core.company import CompanyProfile
from pydantic import Field

class CompanyProfileGetRequest(BaseSchema):
    """Request for a company profile."""
    symbol: str = Field(..., description="The stock symbol for which the profile is requested.")

class CompanyProfileGetResponse(CompanyProfile):
    """Response containing stock profile information."""
    pass