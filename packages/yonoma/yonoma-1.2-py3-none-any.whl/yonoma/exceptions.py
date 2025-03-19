class YonomaAPIError(Exception):
    """Handles API errors."""
    def __init__(self, error_response):
        self.error_response = error_response
        super().__init__(str(error_response))
