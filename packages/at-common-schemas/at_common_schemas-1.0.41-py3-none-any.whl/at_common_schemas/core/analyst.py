from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class AnalystEstimates(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    date: datetime = Field(..., description="Date when the estimate was published")
    revenue_low: float = Field(..., description="Lowest revenue estimate among analysts")
    revenue_high: float = Field(..., description="Highest revenue estimate among analysts")
    revenue_avg: float = Field(..., description="Average of all analyst revenue estimates")
    ebitda_low: float = Field(..., description="Lowest EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization) estimate")
    ebitda_high: float = Field(..., description="Highest EBITDA estimate")
    ebitda_avg: float = Field(..., description="Average of all analyst EBITDA estimates")
    ebit_low: float = Field(..., description="Lowest EBIT (Earnings Before Interest and Taxes) estimate")
    ebit_high: float = Field(..., description="Highest EBIT estimate")
    ebit_avg: float = Field(..., description="Average of all analyst EBIT estimates")
    net_income_low: float = Field(..., description="Lowest net income estimate")
    net_income_high: float = Field(..., description="Highest net income estimate")
    net_income_avg: float = Field(..., description="Average of all analyst net income estimates")
    sga_expense_low: float = Field(..., description="Lowest SG&A (Selling, General & Administrative) expense estimate")
    sga_expense_high: float = Field(..., description="Highest SG&A expense estimate")
    sga_expense_avg: float = Field(..., description="Average of all analyst SG&A expense estimates")
    eps_avg: float = Field(..., description="Average of all analyst EPS (Earnings Per Share) estimates")
    eps_high: float = Field(..., description="Highest EPS estimate")
    eps_low: float = Field(..., description="Lowest EPS estimate")
    num_analysts_revenue: int = Field(..., description="Number of analysts contributing to revenue estimates")
    num_analysts_eps: int = Field(..., description="Number of analysts contributing to EPS estimates")

class RatingsSnapshot(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    rating: str = Field(..., description="Overall analyst rating classification")
    overall_score: int = Field(..., description="Composite score based on all rating factors")
    discounted_cash_flow_score: int = Field(..., description="Score based on discounted cash flow analysis")
    return_on_equity_score: int = Field(..., description="Score based on company's return on equity metrics")
    return_on_assets_score: int = Field(..., description="Score based on company's return on assets performance")
    debt_to_equity_score: int = Field(..., description="Score based on company's debt to equity ratio")
    price_to_earnings_score: int = Field(..., description="Score based on stock's price to earnings ratio")
    price_to_book_score: int = Field(..., description="Score based on stock's price to book ratio")

class RatingsHistorical(RatingsSnapshot):
    date: datetime = Field(..., description="Date when the rating was issued")

class PriceTargetSummary(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    last_month_count: int = Field(..., description="Number of price targets issued in the past month")
    last_month_avg_price_target: float = Field(..., description="Average of price targets from the past month")
    last_quarter_count: int = Field(..., description="Number of price targets issued in the past quarter")
    last_quarter_avg_price_target: float = Field(..., description="Average of price targets from the past quarter")
    last_year_count: int = Field(..., description="Number of price targets issued in the past year")
    last_year_avg_price_target: float = Field(..., description="Average of price targets from the past year")
    all_time_count: int = Field(..., description="Total number of price targets in the dataset")
    all_time_avg_price_target: float = Field(..., description="Average of all price targets in the dataset")
    publishers: str = Field(..., description="List of financial institutions that published these price targets")

class PriceTargetConsensus(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    target_high: float = Field(..., description="Highest analyst price target currently active")
    target_low: float = Field(..., description="Lowest analyst price target currently active")
    target_consensus: float = Field(..., description="Average of all current analyst price targets")
    target_median: float = Field(..., description="Median value of all current analyst price targets")

class PriceTargetNews(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    published_date: datetime = Field(..., description="Date when the price target was published")
    news_url: str = Field(..., description="Full URL to the news article containing the price target")
    news_title: str = Field(..., description="Title of the news article")
    analyst_name: str = Field(..., description="Name of the analyst who issued the price target")
    price_target: float = Field(..., description="Price target value issued by the analyst")
    adj_price_target: float = Field(..., description="Price target adjusted for stock splits or other events")
    price_when_posted: float = Field(..., description="Stock price at the time the price target was published")
    news_publisher: str = Field(..., description="Name of the media outlet that published the article")
    news_base_url: str = Field(..., description="Base domain of the news source")
    analyst_company: str = Field(..., description="Financial institution the analyst works for")    

class Grades(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    date: datetime = Field(..., description="Date when the grade was issued")
    grading_company: str = Field(..., description="Financial institution that issued the grade")
    previous_grade: str = Field(..., description="Previous rating assigned to the stock by this institution")
    new_grade: str = Field(..., description="New rating assigned to the stock by this institution")
    action: str = Field(..., description="Type of rating change (upgrade, downgrade, initiation, etc.)")

class GradesHistorical(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    date: datetime = Field(..., description="Date of the historical rating snapshot")
    analyst_ratings_buy: int = Field(..., description="Number of Buy ratings at this point in time")
    analyst_ratings_hold: int = Field(..., description="Number of Hold ratings at this point in time")
    analyst_ratings_sell: int = Field(..., description="Number of Sell ratings at this point in time")
    analyst_ratings_strong_sell: int = Field(..., description="Number of Strong Sell ratings at this point in time")

class GradesConsensus(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    strong_buy: int = Field(..., description="Current number of Strong Buy ratings")
    buy: int = Field(..., description="Current number of Buy ratings")
    hold: int = Field(..., description="Current number of Hold ratings")
    sell: int = Field(..., description="Current number of Sell ratings")
    strong_sell: int = Field(..., description="Current number of Strong Sell ratings")
    consensus: str = Field(..., description="Overall consensus rating based on all analyst ratings")

class GradesNews(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    published_date: datetime = Field(..., description="Date when the rating news was published")
    news_url: str = Field(..., description="Full URL to the news article about the rating")
    news_title: str = Field(..., description="Title of the news article")
    news_base_url: str = Field(..., description="Base domain of the news source")
    news_publisher: str = Field(..., description="Name of the media outlet that published the article")
    new_grade: str = Field(..., description="New rating assigned to the stock")
    previous_grade: str | None = Field(None, description="Previous rating assigned to the stock, if available")
    grading_company: str = Field(..., description="Financial institution that issued the rating")
    action: str = Field(..., description="Type of rating action (upgrade, downgrade, initiation, etc.)")
    price_when_posted: float = Field(..., description="Stock price at the time the rating was published")