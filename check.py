from typing import Iterable, Mapping, Optional

class Payer:
    """Represents a payer, which can be attached to different items and/or checks."""

    def __init__(self, name: str):
        self.name = name


class Item:
    """ Represents an item of cost in a check."""

    def __init__(self, name: str, cost: float):
        self.name = name
        self.cost = cost


class Check:
    """
    Represents a check, which contains a list of items and a tax rate
    """

    def __init__(self, items: Iterable[Item], tax_rate: float = 0.0) -> None:
        """
        :param items: List of items
        :param tax_rate: Tax rate given as a number less than 1 i.e. 5% is specified as 0.05. If omitted,a default tax
        rate of 0.000% is assumed.
        """
        self.items = set(items)
        self.tax_rate = tax_rate

    def subtotal(self) -> float:
        """
        Returns the subtotal of the total check.
        :return: Sum of the item costs. Tax is excluded.
        """
        return sum([item.cost for item in self.items])

    def total(self, tip: float = 0.0) -> float:
        """
        Returns the post-tax and tip total of the total check. Tip is assumed to be $0.00 if not specified.
        :param tip: Tip given as a number (not a percentage). If omitted, a default tip of $0.00 is assumed
        :return: Sum of the item costs with tax applied and tip added at the end.
        """
        tax_multiplier = 1.0 + self.tax_rate
        return tip + (tax_multiplier * self.subtotal())
