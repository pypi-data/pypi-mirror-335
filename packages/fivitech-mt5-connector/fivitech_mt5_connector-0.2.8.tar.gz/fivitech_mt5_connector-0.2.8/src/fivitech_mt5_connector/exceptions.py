from enum import Enum

class MT5ErrorCode(Enum):
    # Authentication errors
    AUTH_ACCOUNT_DISABLED = "MT_RET_AUTH_ACCOUNT_DISABLED"
    AUTH_ACCOUNT_INVALID = "MT_RET_AUTH_ACCOUNT_INVALID"
    AUTH_ACCOUNT_UNKNOWN = "MT_RET_AUTH_ACCOUNT_UNKNOWN"
    AUTH_INVALID_PASSWORD = "MT_RET_AUTH_INVALID_VERIFY"
    AUTH_CERTIFICATE_BAD = "MT_RET_AUTH_CERTIFICATE_BAD"
    AUTH_CLIENT_INVALID = "MT_RET_AUTH_CLIENT_INVALID"
    AUTH_SERVER_BUSY = "MT_RET_AUTH_SERVER_BUSY"
    AUTH_SERVER_CERT = "MT_RET_AUTH_SERVER_CERT"
    AUTH_SERVER_LIMIT = "MT_RET_AUTH_SERVER_LIMIT"

    # Configuration errors
    CFG_BIND_ADDR_EXIST = "MT_RET_CFG_BIND_ADDR_EXIST"
    CFG_INVALID_RANGE = "MT_RET_CFG_INVALID_RANGE"
    CFG_LIMIT_REACHED = "MT_RET_CFG_LIMIT_REACHED"
    CFG_NO_ACCESS_TO_MAIN = "MT_RET_CFG_NO_ACCESS_TO_MAIN"

    # General errors
    ERR_CANCEL = "MT_RET_ERR_CANCEL"
    ERR_CONNECTION = "MT_RET_ERR_CONNECTION"
    ERR_DATA = "MT_RET_ERR_DATA"
    ERR_DISK = "MT_RET_ERR_DISK"
    ERR_DUPLICATE = "MT_RET_ERR_DUPLICATE"
    ERR_FREQUENT = "MT_RET_ERR_FREQUENT"
    ERR_LOCKED = "MT_RET_ERR_LOCKED"
    ERR_NETWORK = "MT_RET_ERR_NETWORK"
    ERR_NOTFOUND = "MT_RET_ERR_NOTFOUND"
    ERR_NOTMAIN = "MT_RET_ERR_NOTMAIN"
    ERR_NOTSUPPORTED = "MT_RET_ERR_NOTSUPPORTED"
    ERR_PARAMS = "MT_RET_ERR_PARAMS"
    ERR_PERMISSIONS = "MT_RET_ERR_PERMISSIONS"
    ERR_TIMEOUT = "MT_RET_ERR_TIMEOUT"

    # Trade errors
    TRADE_DEAL_EXIST = "MT_RET_TRADE_DEAL_EXIST"
    TRADE_DEAL_PROHIBITED = "MT_RET_TRADE_DEAL_PROHIBITED"
    TRADE_LIMIT_REACHED = "MT_RET_TRADE_LIMIT_REACHED"
    TRADE_ORDER_EXIST = "MT_RET_TRADE_ORDER_EXIST"
    TRADE_ORDER_PROHIBITED = "MT_RET_TRADE_ORDER_PROHIBITED"

    # Request errors
    REQUEST_INVALID = "MT_RET_REQUEST_INVALID"
    REQUEST_INVALID_VOLUME = "MT_RET_REQUEST_INVALID_VOLUME"
    REQUEST_NO_MONEY = "MT_RET_REQUEST_NO_MONEY"
    REQUEST_PRICE_CHANGED = "MT_RET_REQUEST_PRICE_CHANGED"
    REQUEST_REJECT = "MT_RET_REQUEST_REJECT"
    REQUEST_TIMEOUT = "MT_RET_REQUEST_TIMEOUT"
    REQUEST_TRADE_DISABLED = "MT_RET_REQUEST_TRADE_DISABLED"

    # User errors
    USER_ACCOUNT_EXISTS = "MT_RET_USR_ACCOUNT_EXIST"
    USER_API_LIMIT_REACHED = "MT_RET_USR_API_LIMIT_REACHED"
    USER_DIFFERENT_CURRENCY = "MT_RET_USR_DIFFERENT_CURRENCY"
    USER_DIFFERENT_SERVERS = "MT_RET_USR_DIFFERENT_SERVERS"
    USER_HAS_TRADES = "MT_RET_USR_HAS_TRADES"
    USER_IMPORT_ACCOUNT = "MT_RET_USR_IMPORT_ACCOUNT"
    USER_IMPORT_BALANCE = "MT_RET_USR_IMPORT_BALANCE"
    USER_IMPORT_DEALS = "MT_RET_USR_IMPORT_DEALS"
    USER_IMPORT_GROUP = "MT_RET_USR_IMPORT_GROUP"
    USER_IMPORT_HISTORY = "MT_RET_USR_IMPORT_HISTORY"
    USER_IMPORT_ORDERS = "MT_RET_USR_IMPORT_ORDERS"
    USER_IMPORT_POSITIONS = "MT_RET_USR_IMPORT_POSITIONS"
    USER_INVALID_PASSWORD = "MT_RET_USR_INVALID_PASSWORD"
    USER_LAST_ADMIN = "MT_RET_USR_LAST_ADMIN"
    USER_LIMIT_REACHED = "MT_RET_USR_LIMIT_REACHED"
    USER_LOGIN_EXHAUSTED = "MT_RET_USR_LOGIN_EXHAUSTED"
    USER_LOGIN_EXISTS = "MT_RET_USR_LOGIN_EXIST"
    USER_LOGIN_PROHIBITED = "MT_RET_USR_LOGIN_PROHIBITED"
    USER_SUICIDE = "MT_RET_USR_SUICIDE"

class MT5BaseException(Exception):
    """Base exception for all MT5-related errors"""
    def __init__(self, message: str, error_code: MT5ErrorCode = None):
        self.error_code = error_code
        super().__init__(message)

class MT5ConnectionError(MT5BaseException):
    """Exception raised for MT5 connection and network errors"""
    pass

class MT5AuthenticationError(MT5BaseException):
    """Exception raised for authentication and permission errors"""
    pass

class MT5ConfigError(MT5BaseException):
    """Exception raised for configuration-related errors"""
    pass

class MT5TradeError(MT5BaseException):
    """Exception raised for trading-related errors"""
    pass

class MT5RequestError(MT5BaseException):
    """Exception raised for request-related errors"""
    pass

class MT5UserError(MT5BaseException):
    """Exception raised for user-related errors"""
    pass

class MT5ArchiveError(MT5BaseException):
    """Exception raised for archive-related errors"""
    pass

class MT5LimitError(MT5BaseException):
    """Exception raised when various limits are reached"""
    pass

class MT5ValidationError(MT5BaseException):
    """Exception raised for validation errors"""
    pass

class MT5ImportError(MT5UserError):
    """Exception raised for import-related errors"""
    pass

# Error code to exception mapping
ERROR_CODE_MAP = {
    # Authentication errors
    MT5ErrorCode.AUTH_ACCOUNT_DISABLED: (MT5AuthenticationError, "Account is disabled"),
    MT5ErrorCode.AUTH_ACCOUNT_INVALID: (MT5AuthenticationError, "Invalid account"),
    MT5ErrorCode.AUTH_ACCOUNT_UNKNOWN: (MT5AuthenticationError, "Account not found"),
    MT5ErrorCode.AUTH_INVALID_PASSWORD: (MT5AuthenticationError, "Invalid password"),
    MT5ErrorCode.AUTH_CERTIFICATE_BAD: (MT5AuthenticationError, "Invalid certificate"),
    MT5ErrorCode.AUTH_CLIENT_INVALID: (MT5AuthenticationError, "Invalid client"),
    MT5ErrorCode.AUTH_SERVER_BUSY: (MT5ConnectionError, "Server is busy"),
    MT5ErrorCode.AUTH_SERVER_CERT: (MT5AuthenticationError, "Invalid server certificate"),
    MT5ErrorCode.AUTH_SERVER_LIMIT: (MT5LimitError, "Server connection limit reached"),

    # Configuration errors
    MT5ErrorCode.CFG_BIND_ADDR_EXIST: (MT5ConfigError, "Address already in use"),
    MT5ErrorCode.CFG_INVALID_RANGE: (MT5ConfigError, "Invalid range"),
    MT5ErrorCode.CFG_LIMIT_REACHED: (MT5LimitError, "Configuration limit reached"),
    MT5ErrorCode.CFG_NO_ACCESS_TO_MAIN: (MT5ConfigError, "No access to main server"),

    # General errors
    MT5ErrorCode.ERR_CANCEL: (MT5RequestError, "Operation cancelled"),
    MT5ErrorCode.ERR_CONNECTION: (MT5ConnectionError, "Connection error"),
    MT5ErrorCode.ERR_DATA: (MT5ValidationError, "Invalid data"),
    MT5ErrorCode.ERR_DISK: (MT5ConnectionError, "Disk error"),
    MT5ErrorCode.ERR_DUPLICATE: (MT5ValidationError, "Duplicate entry"),
    MT5ErrorCode.ERR_FREQUENT: (MT5LimitError, "Too many requests"),
    MT5ErrorCode.ERR_LOCKED: (MT5ValidationError, "Operation locked"),
    MT5ErrorCode.ERR_NETWORK: (MT5ConnectionError, "Network error"),
    MT5ErrorCode.ERR_NOTFOUND: (MT5ValidationError, "Not found"),
    MT5ErrorCode.ERR_NOTMAIN: (MT5ValidationError, "Operation allowed only on main server"),
    MT5ErrorCode.ERR_NOTSUPPORTED: (MT5ValidationError, "Operation not supported"),
    MT5ErrorCode.ERR_PARAMS: (MT5ValidationError, "Invalid parameters"),
    MT5ErrorCode.ERR_PERMISSIONS: (MT5AuthenticationError, "Not enough permissions"),
    MT5ErrorCode.ERR_TIMEOUT: (MT5ConnectionError, "Operation timeout"),

    # Trade errors
    MT5ErrorCode.TRADE_DEAL_EXIST: (MT5TradeError, "Deal already exists"),
    MT5ErrorCode.TRADE_DEAL_PROHIBITED: (MT5TradeError, "Deal is prohibited"),
    MT5ErrorCode.TRADE_LIMIT_REACHED: (MT5LimitError, "Trade limit reached"),
    MT5ErrorCode.TRADE_ORDER_EXIST: (MT5TradeError, "Order already exists"),
    MT5ErrorCode.TRADE_ORDER_PROHIBITED: (MT5TradeError, "Order is prohibited"),

    # Request errors
    MT5ErrorCode.REQUEST_INVALID: (MT5RequestError, "Invalid request"),
    MT5ErrorCode.REQUEST_INVALID_VOLUME: (MT5RequestError, "Invalid volume"),
    MT5ErrorCode.REQUEST_NO_MONEY: (MT5RequestError, "Insufficient funds"),
    MT5ErrorCode.REQUEST_PRICE_CHANGED: (MT5RequestError, "Price changed"),
    MT5ErrorCode.REQUEST_REJECT: (MT5RequestError, "Request rejected"),
    MT5ErrorCode.REQUEST_TIMEOUT: (MT5RequestError, "Request timeout"),
    MT5ErrorCode.REQUEST_TRADE_DISABLED: (MT5RequestError, "Trading disabled"),

    # User errors
    MT5ErrorCode.USER_ACCOUNT_EXISTS: (MT5ValidationError, "Account already exists"),
    MT5ErrorCode.USER_API_LIMIT_REACHED: (MT5LimitError, "API request limit reached"),
    MT5ErrorCode.USER_DIFFERENT_CURRENCY: (MT5ValidationError, "Currency mismatch"),
    MT5ErrorCode.USER_DIFFERENT_SERVERS: (MT5ValidationError, "Server mismatch"),
    MT5ErrorCode.USER_HAS_TRADES: (MT5ValidationError, "User has active trades"),
    MT5ErrorCode.USER_IMPORT_ACCOUNT: (MT5ImportError, "Failed to import account"),
    MT5ErrorCode.USER_IMPORT_BALANCE: (MT5ImportError, "Failed to import balance"),
    MT5ErrorCode.USER_IMPORT_DEALS: (MT5ImportError, "Failed to import deals"),
    MT5ErrorCode.USER_IMPORT_GROUP: (MT5ImportError, "Failed to import group"),
    MT5ErrorCode.USER_IMPORT_HISTORY: (MT5ImportError, "Failed to import history"),
    MT5ErrorCode.USER_IMPORT_ORDERS: (MT5ImportError, "Failed to import orders"),
    MT5ErrorCode.USER_IMPORT_POSITIONS: (MT5ImportError, "Failed to import positions"),
    MT5ErrorCode.USER_INVALID_PASSWORD: (MT5AuthenticationError, "Invalid password"),
    MT5ErrorCode.USER_LAST_ADMIN: (MT5ValidationError, "Cannot modify last admin"),
    MT5ErrorCode.USER_LIMIT_REACHED: (MT5LimitError, "User limit reached"),
    MT5ErrorCode.USER_LOGIN_EXHAUSTED: (MT5LimitError, "No free logins available"),
    MT5ErrorCode.USER_LOGIN_EXISTS: (MT5ValidationError, "Login already exists"),
    MT5ErrorCode.USER_LOGIN_PROHIBITED: (MT5AuthenticationError, "Login prohibited"),
    MT5ErrorCode.USER_SUICIDE: (MT5ValidationError, "Cannot perform operation on own account"),
}

def raise_mt5_error(error_code: str, custom_message: str = None):
    """
    Helper function to raise appropriate exception based on MT5 error code
    
    Args:
        error_code: MT5 error code string
        custom_message: Optional custom error message
    """
    try:
        mt5_code = MT5ErrorCode(error_code)
        exception_class, default_message = ERROR_CODE_MAP.get(mt5_code, (MT5BaseException, "Unknown MT5 error"))
        message = custom_message or default_message
        raise exception_class(message, mt5_code)
    except ValueError:
        # If error_code is not in MT5ErrorCode enum
        raise MT5BaseException(custom_message or f"Unknown MT5 error: {error_code}")

def get_error_details(error_code: str) -> tuple:
    """
    Get exception class and default message for an error code without raising
    
    Args:
        error_code: MT5 error code string
        
    Returns:
        tuple: (exception_class, default_message)
    """
    try:
        mt5_code = MT5ErrorCode(error_code)
        return ERROR_CODE_MAP.get(mt5_code, (MT5BaseException, "Unknown MT5 error"))
    except ValueError:
        return MT5BaseException, f"Unknown MT5 error: {error_code}"
