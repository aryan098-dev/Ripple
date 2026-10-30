
from checkout import complete_checkout


def test_complete_checkout():
    result = complete_checkout(100)

    assert result == "Payment of 100 processed successfully"
