from typing import Optional, Union
from datetime import datetime
from ..pool import mt5_pools
from ..exceptions import (
    MT5BaseException, MT5ConnectionError, MT5AuthenticationError,
    MT5ConfigError, MT5ValidationError, raise_mt5_error
)
import MT5Manager
import logging

logger = logging.getLogger(__name__)

class MT5BaseHelper:
    """Base helper class with common MT5 functionality and error handling"""
    
    @staticmethod
    def get_connection(server_id=None, server_type=None):
        """
        Get MT5 connection based on server_id or server_type
        
        Args:
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            MT5 connection object
            
        Raises:
            ValueError: If neither server_id nor server_type is provided
            MT5ConnectionError: If connection cannot be established
            MT5ConfigError: If server configuration is invalid
        """
        try:
            if server_id is not None:
                connection = mt5_pools.get_by_id(server_id)
            elif server_type is not None:
                connection = mt5_pools.get_by_type(server_type)
            else:
                raise ValueError("Either server_id or server_type must be provided")
                
            if not connection:
                raise MT5ConnectionError("Failed to get MT5 connection")
                
            if not connection.manager:
                error = MT5Manager.LastError()
                raise_mt5_error(error[1], "MT5 manager not available")
                
            return connection
            
        except MT5BaseException:
            # Re-raise MT5 specific exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to get MT5 connection: {str(e)}")
            raise MT5ConnectionError(f"Failed to get MT5 connection: {str(e)}")

    @classmethod
    def get_server_time(cls, server_id=None, server_type=None) -> int:
        """
        Get MT5 server time as Unix timestamp
        
        Args:
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            int: Server time as Unix timestamp
            
        Raises:
            MT5ConnectionError: If server time cannot be retrieved
        """
        try:
            connection = cls.get_connection(server_id, server_type)
            server_time = connection.manager.TimeServer()
            
            if not server_time:
                error = MT5Manager.LastError()
                raise_mt5_error(error[1], "Failed to get server time")
                
            return server_time
            
        except MT5BaseException:
            raise
        except Exception as e:
            logger.error(f"Failed to get server time: {str(e)}")
            raise MT5ConnectionError(f"Failed to get server time: {str(e)}")

    @classmethod
    def convert_to_server_time(
        cls,
        dt: Union[datetime, int],
        server_id: Optional[int] = None,
        server_type: Optional[str] = None
    ) -> int:
        """
        Convert datetime or timestamp to server time
        
        Args:
            dt: Datetime object or Unix timestamp
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            int: Server-adjusted timestamp
            
        Raises:
            ValueError: If dt is invalid
            MT5ConnectionError: If server time cannot be retrieved
        """
        try:
            # Validate and convert input to timestamp
            if isinstance(dt, datetime):
                local_ts = int(dt.timestamp())
            elif isinstance(dt, (int, float)):
                local_ts = int(dt)
            else:
                raise ValueError("dt must be datetime or timestamp")
                
            # Get time difference between local and server
            server_time = cls.get_server_time(server_id, server_type)
            time_diff = server_time - int(datetime.now().timestamp())
            
            return local_ts + time_diff
            
        except MT5BaseException:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to convert to server time: {str(e)}")
            raise MT5ConnectionError(f"Failed to convert to server time: {str(e)}")

    @staticmethod
    def validate_connection(connection) -> None:
        """
        Validate MT5 connection and manager availability
        
        Args:
            connection: MT5 connection object to validate
            
        Raises:
            MT5ConnectionError: If connection is invalid
            MT5ConfigError: If manager is not available
        """
        if not connection:
            raise MT5ConnectionError("MT5 connection not available")
            
        if not connection.manager:
            error = MT5Manager.LastError()
            if error and error[1]:
                raise_mt5_error(error[1], "MT5 manager not available")
            raise MT5ConfigError("MT5 manager not available")

    @staticmethod
    def handle_mt5_result(
        result,
        error_prefix: str,
        success_value=False
    ) -> None:
        """
        Handle MT5 operation result and raise appropriate exception if needed
        
        Args:
            result: Result from MT5 operation
            error_prefix: Prefix for error message
            success_value: Value indicating success (usually False or None)
            
        Raises:
            MT5BaseException: With appropriate subclass based on error code
        """
        if result == success_value:
            error = MT5Manager.LastError()
            if error and error[1]:
                raise_mt5_error(error[1], f"{error_prefix}: {error}")
            raise MT5ConnectionError(f"{error_prefix}: Unknown error")

    @staticmethod
    def log_operation(operation_name: str, **kwargs) -> None:
        """
        Log MT5 operation with relevant details
        
        Args:
            operation_name: Name of the operation
            **kwargs: Additional details to log
        """
        details = " ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.info(f"MT5 {operation_name}: {details}")

    @staticmethod
    def common_error_handler(operation_name: str):
        """
        Decorator for common MT5 error handling
        
        Args:
            operation_name: Name of the operation for logging
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except MT5ConnectionError as e:
                    logger.error(f"{operation_name} failed due to connection: {e}")
                    raise
                except MT5AuthenticationError as e:
                    logger.error(f"{operation_name} failed due to authentication: {e}")
                    raise
                except MT5ValidationError as e:
                    logger.error(f"{operation_name} failed due to validation: {e}")
                    raise
                except MT5BaseException as e:
                    logger.error(f"{operation_name} failed: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error in {operation_name}: {e}")
                    raise MT5ConnectionError(f"{operation_name} failed: {str(e)}")
            return wrapper
        return decorator 