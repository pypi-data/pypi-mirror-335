class DNSQueryError(Exception):
    """Exception raised for errors occurring during a DNS query."""

    def __init__(self, message: str):
        super().__init__(f"DNSQueryError: {message}")
