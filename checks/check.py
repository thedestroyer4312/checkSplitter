from typing import Iterable, Mapping


class Payer:
    """Represents a payer, which can be attached to different items and/or checks."""

    def __init__(self, name: str) -> None:
        """
        :param name: String
        """
        self.name = name


class Item:
    """ Represents an item of cost in a check."""

    def __init__(self, name: str, cost: float) -> None:
        """
        :param name: String
        :param cost: Number. Should be nonnegative.
        """
        self.name = name
        self.cost = cost


class Check:
    """
    Represents a check, which contains a list of items
    """

    def __init__(self, items: Iterable[Item] = []) -> None:
        """
        :param items: List of valid items. If omitted, creates an empty check.
        """
        self.items = set(items)

    def subtotal(self) -> float:
        """
        Returns the subtotal of the total check.
        :return: Sum of the item costs. Tax is excluded.
        """
        return sum([item.cost for item in self.items])

    def total(self, tax_rate: float, tip: float = 0.0) -> float:
        """
        Returns the post-tax and tip total of the total check. Tip is assumed to be $0.00 if not specified.
        :param tax_rate: Tax rate given as a number less than 1 i.e. 5% is specified as 0.05.
        :param tip: Tip given as a number (not a percentage). If omitted, a default tip of $0.00 is assumed
        :return: Sum of the item costs with tax applied and tip added at the end.
        """
        tax_multiplier = 1.0 + tax_rate
        return tip + self.tax_amount() + self.subtotal()

    def tax_amount(self, tax_rate: float) -> float:
        """
        Returns the amount of tax for this check given a tax rate
        :param tax_rate: Tax rate given as a number less than 1 i.e. 5% is specified as 0.05
        :return: Amount of tax for this check i.e. the difference between the total and subtotal
        """
        return tax_rate * self.subtotal()


class SplitCheck:
    """
    Represents a split check, which contains a check, a list of payers, and an assignment mapping i.e. who is
    paying for what.
    """

    def __init__(self,
                 check: Check,
                 payers: Iterable[Payer],
                 item_assignments: Mapping[Item, Iterable[Payer]] = {}
                 ) -> None:
        """
        :param check: Check object
        :param payers: List of payers
        :param item_assignments: Contains assignments of items to who is paying for that item, which is assumed to be
        uniform i.e. if an item has 3 payers listed, then those 3 will pay equally. The payers listed here must be a
        subset of payers, although the same restriction does not apply to the listed items. If an item is omitted,
        then it is assumed that all payers will split that item evenly. So, if this is omitted, then the whole
        check is split evenly.
        """
        self.check = check
        self.payers = set(payers)
        self.item_assignments = dict(item_assignments)

    def compute_proportions(self) -> dict[Payer, float]:
        """
        Computes the proportion of check owed for each payer. For example, if a check if split 2 ways evenly, then
        payer 1 owes a 0.5 proportion and payer 2 a 0.5 proportion.
        :return: Dictionary containing mappings for every payer to the proportion that they owe of the check
        """
        res: dict[Payer, float] = {}

        for payer in self.payers:
            # Loop over every item and check if they are paying. If so, increment their individual subtotal
            payer_subtotal = 0.0
            for item in self.check.items:
                # If the item is not found in the assignment or the item assignment is empty/null, split evenly across
                # all payers
                if (
                        item not in self.item_assignments
                        or self.item_assignments[item] is None
                        or len(self.item_assignments[item]) == 0
                ):
                    payer_subtotal += item.cost / len(self.payers)
                else:
                    # Otherwise, split evenly with the other people in the check
                    payer_subtotal += item.cost / len(self.item_assignments[item])

            # Now, compute the proportion by dividing their individual subtotal by the check subtotal
            proportion = payer_subtotal / self.check.subtotal()
            res[payer] = proportion
        return res

    def compute_amounts_owed(self, tax_rate: float, tip: float = 0.0) -> dict[Payer, tuple[float, float, float]]:
        """
        Computes and returns the monetary amount owed for each payer for the subtotal, total before tip, and total
        after tip.
        :param tax_rate: Tax rate given as a number less than 1 i.e. 5% is specified as 0.05
        :param tip: Tip given as a number (not a percentage). If omitted, a default tip of $0.00 is assumed
        :return: Dictionary mapping payer -> (amt_subtotal, amt_total, amt_total_and_tip)
        """
        proportions: dict[Payer, float] = self.compute_proportions()
        return {p: (proportions[p] * self.check.subtotal(),
                    proportions[p] * self.check.total(tax_rate),
                    proportions[p] * self.check.total(tax_rate, tip))
                for p in self.payers}
