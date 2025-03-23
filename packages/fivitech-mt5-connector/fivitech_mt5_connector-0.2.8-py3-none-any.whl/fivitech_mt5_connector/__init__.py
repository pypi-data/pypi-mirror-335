from .constants import MT5ServerConfig
from .pool import MT5ConnectionPools
from .interface import MT5Interface
import MT5Manager

# Expose MT5Pool as an alias for MT5ConnectionPools
MT5Pool = MT5ConnectionPools

__version__ = "0.2.8"
__all__ = ['MT5Pool', 'MT5ServerConfig', 'MT5Interface', 'MT5Manager']
