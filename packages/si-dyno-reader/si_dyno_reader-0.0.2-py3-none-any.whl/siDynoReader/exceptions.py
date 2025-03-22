class ChannelNotFoundError(KeyError):
    """Raised when a requested channel does not exist."""
    pass

class TestChannelNotFoundError(KeyError):
    """Raised when the test channel does not exist."""
    pass

