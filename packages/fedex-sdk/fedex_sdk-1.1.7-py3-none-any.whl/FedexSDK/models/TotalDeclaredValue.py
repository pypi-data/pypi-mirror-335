

from pydantic import BaseModel


class TotalDeclaredValue(BaseModel):
    """
    Args:
        `amount` (`float`): Total Declared Value Amount. Example: 12.45
        `currency` (`str`): This is the currency code for the amount. Example: USD
    """
    amount: float
    currency: str