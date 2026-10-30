def process_payment(amount):
    """Process a customer payment."""

    if amount <= 0:
        raise ValueError("Payment amount must be positive")

    return f"Payment of {amount} processed successfully"