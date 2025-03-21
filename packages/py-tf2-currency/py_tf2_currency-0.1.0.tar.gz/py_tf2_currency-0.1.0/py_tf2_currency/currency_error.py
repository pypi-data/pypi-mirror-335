class CurrencyError(Exception):
    """Custom exception for currency-related errors."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
