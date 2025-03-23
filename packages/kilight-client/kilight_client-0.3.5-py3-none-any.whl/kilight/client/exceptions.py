
class KiLightException(Exception):
    def __init__(self, message: str):
        self.message: str = message

    def __str__(self):
        return self.message


class NetworkTimeoutError(KiLightException):
    """
    Generic network timeout
    """
    def __init__(self, message: str):
        super().__init__(message)


class ConnectionTimeoutError(NetworkTimeoutError):
    """
    Connecting to the device timed out
    """

    def __init__(self, host: str, port: int, timeout: int):
        super().__init__(f"Connection to {host}:{port} timed out after {timeout} seconds.")


class RequestTimeoutError(NetworkTimeoutError):
    """
    Sending a request to the device timed out
    """

    def __init__(self, host: str, port: int, timeout: int):
        super().__init__(f"Request to {host}:{port} timed out after {timeout} seconds.")


class ResponseTimeoutError(NetworkTimeoutError):
    """
    Waiting for a response from the device timed out
    """

    def __init__(self, host: str, port: int, timeout: int):
        super().__init__(f"Timed out waiting for a response from {host}:{port} after {timeout} seconds.")