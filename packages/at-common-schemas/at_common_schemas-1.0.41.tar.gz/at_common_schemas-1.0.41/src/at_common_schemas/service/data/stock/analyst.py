from typing import List
from pydantic import Field
from at_common_schemas.base import BaseSchema
from at_common_schemas.core.analyst import (
    RatingsSnapshot, RatingsHistorical,
    PriceTargetSummary, PriceTargetConsensus,PriceTargetNews, 
    Grades, GradesHistorical, GradesConsensus, GradesNews
)

# Rating Snapshot
class AnalystRatingSnapshotGetRequest(BaseSchema):
    """Request for analyst rating snapshot."""
    symbol: str = Field(..., description="The stock symbol for the request.")

class AnalystRatingSnapshotGetResponse(RatingsSnapshot):
    """Response containing analyst rating snapshot."""
    pass

# Rating Historical
class AnalystRatingHistoricalListRequest(BaseSchema):
    """Request for analyst rating historical data."""
    symbol: str = Field(..., description="The stock symbol for the request.")
    limit: int = Field(..., description="The number of results to return.")

class AnalystRatingHistoricalListResponse(BaseSchema):
    """Response containing analyst rating historical data."""
    items: List[RatingsHistorical] = Field(..., description="List of analyst rating historical data.")

# Price Target Summary
class AnalystPriceTargetSummaryGetRequest(BaseSchema):
    """Request for analyst price target summary."""
    symbol: str = Field(..., description="The stock symbol for the request.")

class AnalystPriceTargetSummaryGetResponse(PriceTargetSummary):
    """Response containing analyst price target summary."""
    pass

# Price Target Consensus
class AnalystPriceTargetConsensusGetRequest(BaseSchema):
    """Request for analyst price target consensus."""
    symbol: str = Field(..., description="The stock symbol for the request.")

class AnalystPriceTargetConsensusGetResponse(PriceTargetConsensus):
    """Response containing analyst price target consensus."""
    pass

# Price Target News
class AnalystPriceTargetNewsListRequest(BaseSchema):
    """Request for analyst price target news."""
    symbol: str = Field(..., description="The stock symbol for the request.")
    limit: int = Field(..., description="The number of results to return.")

class AnalystPriceTargetNewsListResponse(BaseSchema):
    """Response containing analyst price target news."""
    items: List[PriceTargetNews] = Field(..., description="List of analyst price target news.")

# Grades
class AnalystGradesListRequest(BaseSchema):
    """Request for analyst grades."""
    symbol: str = Field(..., description="The stock symbol for the request.")
    
class AnalystGradesListResponse(BaseSchema):
    """Response containing analyst grades."""
    items: List[Grades] = Field(..., description="List of analyst grades.")

# Grades Historical
class AnalystGradesHistoricalListRequest(BaseSchema):
    """Request for analyst grades historical data."""
    symbol: str = Field(..., description="The stock symbol for the request.")
    limit: int = Field(..., description="The number of results to return.")

class AnalystGradesHistoricalListResponse(BaseSchema):
    """Response containing analyst grades historical data."""
    items: List[GradesHistorical] = Field(..., description="List of analyst grades historical data.")

# Grades Consensus
class AnalystGradesConsensusGetRequest(BaseSchema):
    """Request for analyst grades consensus."""
    symbol: str = Field(..., description="The stock symbol for the request.")

class AnalystGradesConsensusGetResponse(GradesConsensus):
    """Response containing analyst grades consensus."""
    pass

# Grades News
class AnalystGradesNewsListRequest(BaseSchema):
    """Request for analyst grades news."""
    symbol: str = Field(..., description="The stock symbol for the request.")
    limit: int = Field(..., description="The number of results to return.")

class AnalystGradesNewsListResponse(BaseSchema):
    """Response containing analyst grades news."""
    items: List[GradesNews] = Field(..., description="List of analyst grades news.")