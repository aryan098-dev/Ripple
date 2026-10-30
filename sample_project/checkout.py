
from payment import process_payment


def complete_checkout(amount):
    """Complete customer checkout."""
    return process_payment(amount)
