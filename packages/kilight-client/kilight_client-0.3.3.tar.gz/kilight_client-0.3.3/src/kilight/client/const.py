
from typing import Final

# Color temperature of the pure warm white LED's
MIN_COLOR_TEMP: Final[int] = 2700

# Color temperature of the pure cold white LED's
MAX_COLOR_TEMP: Final[int] = 6500

# Default port that KiLight should be listening on
DEFAULT_PORT: Final[int] = 10240

# Default connection timeout, in seconds
DEFAULT_CONNECTION_TIMEOUT: Final[int] = 15

# Default request timeout, in seconds
DEFAULT_REQUEST_TIMEOUT: Final[int] = 15

# Default response timeout, in seconds
DEFAULT_RESPONSE_TIMEOUT: Final[int] = 15

# Default zeroconf discovery wait time, in seconds
DEFAULT_DISCOVERY_TIME: Final[float] = 2.0

# Default zeroconf discovery service name
DEFAULT_DISCOVERY_SERVICE_NAME: Final[str] = "_kilight._tcp.local."