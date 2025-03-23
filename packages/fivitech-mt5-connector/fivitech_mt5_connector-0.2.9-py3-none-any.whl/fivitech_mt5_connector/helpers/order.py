from typing import Dict, List, Optional, Union
from datetime import datetime
from .base import MT5BaseHelper
from ..pool import mt5_pools
from ..exceptions import (
    MT5BaseException, MT5ConnectionError, MT5TradeError,
    MT5ValidationError, MT5RequestError, raise_mt5_error
)
import MT5Manager
import asyncio
import logging

logger = logging.getLogger(__name__)

class MT5OrderHelper(MT5BaseHelper):
    """Helper class for MT5 order operations"""

    @staticmethod
    def get_connection(server_id=None, server_type=None):
        """Get MT5 connection based on server_id or server_type"""
        if server_id is not None:
            return mt5_pools.get_by_id(server_id)
        elif server_type is not None:
            return mt5_pools.get_by_type(server_type)
        raise ValueError("Either server_id or server_type must be provided")

    @staticmethod
    async def get_open(login: Union[int, List[int]], server_id=None, server_type=None) -> List[MT5Manager.MTOrder]:
        """
        Get open orders for one or multiple users
        
        Args:
            login: Single user login ID or list of login IDs
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            List of open orders as dictionaries
            
        Raises:
            ValueError: If login is invalid
            MT5ConnectionError: If connection fails
        """
        # Convert single login to list for uniform processing
        logins = [login] if isinstance(login, int) else login
        
        # Validate all logins
        if not all(isinstance(l, int) and l > 0 for l in logins):
            raise ValueError("All logins must be positive integers")
                
        connection = MT5OrderHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
                
        try:
            print(f"\n=== MT5 Open Orders Request Debug ===")
            print(f"1. Connection state: connected={connection._connected}")
            print(f"2. Manager instance available: {connection.manager is not None}")
            print(f"3. Requesting open orders for {len(logins)} users")
            
            # For single login, use OrderGetOpen
            if len(logins) == 1:
                orders = connection.manager.OrderGetOpen(logins[0])
                if orders is None:
                    error = MT5Manager.LastError()
                    if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                        print("4. No open orders found")
                        return []
                    raise_mt5_error(error[1], "Failed to get open orders")
                    
                print(f"4. Found {len(orders) if orders else 0} open orders")
                print("=== End Debug ===\n")
                return orders if orders else []
                
            # For multiple logins, use OrderGetByLogins
            orders = connection.manager.OrderGetByLogins(logins)
            if orders is None:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    print("4. No open orders found")
                    return []
                raise_mt5_error(error[1], "Failed to get open orders")
                
            print(f"4. Found {len(orders) if orders else 0} open orders")
            print("=== End Debug ===\n")
            return orders if orders else []
                
        except MT5BaseException:
            raise
        except Exception as e:
            print(f"\n=== MT5 Error Debug ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            error = MT5Manager.LastError()
            print(f"MT5 Last Error: {error}")
            print("=== End Error Debug ===\n")
            raise MT5ConnectionError(f"Failed to get open orders: {str(e)}")
        
    @staticmethod
    async def get_closed(
        login: int,
        from_date: Union[datetime, int],
        to_date: Union[datetime, int],
        offset: int = 0,
        limit: int = 100,
        server_id=None,
        server_type=None
    ) -> List[MT5Manager.MTOrder]:
        """
        Get client closed orders (history) with paged output
        
        Args:
            login: Client login ID
            from_date: Start date (datetime or unix timestamp)
            to_date: End date (datetime or unix timestamp)
            offset: Order index to start from (default: 0)
            limit: Number of orders to retrieve (default: 100)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            List of closed order objects
            
        Raises:
            ValueError: If parameters are invalid
            MT5ConnectionError: If connection fails
            MT5ValidationError: If parameters are invalid
            MT5RequestError: If request fails
        """
        connection = MT5OrderHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")

        try:
            print(f"\n=== MT5 Closed Orders Request Debug ===")
            print(f"1. Connection state: connected={connection._connected}")
            print(f"2. Manager instance available: {connection.manager is not None}")
            
            # Convert datetime to timestamp if needed
            from_ts = MT5OrderHelper.convert_to_server_time(from_date, server_id, server_type)
            to_ts = MT5OrderHelper.convert_to_server_time(to_date, server_id, server_type)
            
            print(f"3. Requesting closed orders for login {login}")
            print(f"   From: {datetime.fromtimestamp(from_ts)} ({from_ts})")
            print(f"   To: {datetime.fromtimestamp(to_ts)} ({to_ts})")
            print(f"   Offset: {offset}")
            print(f"   Limit: {limit}")
            
            # Request closed orders history
            orders = connection.manager.HistoryRequestPage(
                login=login,
                from_date=from_ts,
                to_date=to_ts,
                offset=offset,
                total=limit
            )
            
            if not orders:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    print("4. No closed orders found")
                    return []
                raise_mt5_error(error[1], "Failed to get closed orders")
                
            print(f"4. Found {len(orders)} closed orders")
            print("=== End Debug ===\n")
            
            return orders if orders else []
            
        except MT5BaseException:
            raise
        except Exception as e:
            print(f"\n=== MT5 Error Debug ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            error = MT5Manager.LastError()
            print(f"MT5 Last Error: {error}")
            print("=== End Error Debug ===\n")
            raise MT5ConnectionError(f"Failed to get closed orders: {str(e)}")

    @staticmethod
    async def add(params: Dict, server_id=None, server_type=None) -> MT5Manager.MTOrder:
        """
        Add an open order to the server database
        
        Args:
            params: Dictionary containing order details including:
                - Login: Client login (required)
                - Symbol: Trading instrument (required)
                - Type: Order type (required)
                - Digits: Number of decimal places for the symbol (required)
                - DigitsCurrency: Number of decimal places for the currency (required)
                - ContractSize: Contract size (required)
                - VolumeInitial: Initial volume (required)
                - VolumeCurrent: Current volume (required, must not exceed initial)
                - PriceOrder: Order price (required)
                - State: Order state (required, must be valid open state)
                - Ticket: Optional, if 0 or not provided, server will auto-assign
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            Added order object as dictionary
            
        Raises:
            ValueError: If required parameters are missing or invalid
            MT5ConnectionError: If connection fails
        """
        # Validate required parameters
        required_fields = ['Login', 'Symbol', 'Type', 'Digits', 'DigitsCurrency', 'ContractSize', 'VolumeInitial', 'VolumeCurrent', 'PriceOrder', 'State']
        for field in required_fields:
            if field not in params:
                raise ValueError(f"{field} is required in params")
                
        connection = MT5OrderHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
                
        try:
            print(f"\n=== MT5 Order Add Debug ===")
            print(f"1. Connection state: connected={connection._connected}")
            print(f"2. Manager instance available: {connection.manager is not None}")
            
            # Create new order object with manager instance
            print("\n3. Creating order object")
            order = MT5Manager.MTOrder(connection.manager)
            if not order:
                error = MT5Manager.LastError()
                raise_mt5_error(error[1], "Failed to create order object")
            
            # Set order parameters with proper type conversion
            print("4. Setting order parameters:")
            if 'Login' in params:
                order.Login = int(params['Login'])
                print(f"   - Login: {order.Login}")
            if 'Symbol' in params:
                order.Symbol = str(params['Symbol'])
                print(f"   - Symbol: {order.Symbol}")
            if 'Type' in params:
                try:
                    order.Type = int(params['Type'])
                    print(f"   - Type: {order.Type}")
                except Exception as e:
                    raise ValueError(f"Invalid order type: {params['Type']}")
            if 'Digits' in params:
                order.Digits = int(params['Digits'])
                print(f"   - Digits: {order.Digits}")
            if 'DigitsCurrency' in params:
                order.DigitsCurrency = int(params['DigitsCurrency'])
                print(f"   - DigitsCurrency: {order.DigitsCurrency}")
            if 'ContractSize' in params:
                order.ContractSize = int(params['ContractSize'])
                print(f"   - ContractSize: {order.ContractSize}")
            if 'VolumeInitial' in params:
                try:
                    volume = int(params['VolumeInitial'])
                    if volume <= 0:
                        raise ValueError("Volume must be positive")
                    order.VolumeInitial = volume
                    print(f"   - VolumeInitial: {order.VolumeInitial}")
                except (ValueError, OverflowError, TypeError):
                    raise ValueError("Volume must be positive")
            if 'VolumeCurrent' in params:
                try:
                    volume = int(params['VolumeCurrent'])
                    if volume <= 0:
                        raise ValueError("Volume must be positive")
                    order.VolumeCurrent = volume
                    print(f"   - VolumeCurrent: {order.VolumeCurrent}")
                except (ValueError, OverflowError, TypeError):
                    raise ValueError("Volume must be positive")
            if 'PriceOrder' in params:
                order.PriceOrder = float(params['PriceOrder'])
                print(f"   - PriceOrder: {order.PriceOrder}")
            if 'State' in params:
                order.State = int(params['State'])
                print(f"   - State: {order.State}")
            
            # get current timestamp
            time = datetime.now()
            order.TimeSetupMsc = MT5OrderHelper.convert_to_server_time(time, server_id, server_type) * 1000

            # Add order to server
            print("\n5. Adding order to server")
            result = connection.manager.OrderAdd(order)
            if not result:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error(error[1], "Invalid order parameters")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID_VOLUME:
                    raise_mt5_error(error[1], "Invalid order volume")
                else:
                    raise_mt5_error(error[1], "Failed to add order")
            
            print("6. Order added successfully")
            print("=== End Debug ===\n")
            
            return order
            
        except MT5BaseException:
            raise
        except ValueError:
            raise
        except Exception as e:
            print(f"\n=== MT5 Error Debug ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            error = MT5Manager.LastError()
            print(f"MT5 Last Error: {error}")
            print("=== End Error Debug ===\n")
            raise MT5ConnectionError(f"Failed to add order: {str(e)}")

    @staticmethod
    async def get_paged(
        login: int,
        from_date: Union[datetime, int],
        to_date: Union[datetime, int],
        offset: int = 0,
        total: int = 100,
        server_id=None,
        server_type=None
    ) -> List[MT5Manager.MTOrder]:
        """
        Get client orders with paged output
        
        Args:
            login: Client login ID
            from_date: Start date (datetime or unix timestamp)
            to_date: End date (datetime or unix timestamp)
            offset: Order index to start from (default: 0)
            total: Number of orders to retrieve (default: 100)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            List of order objects
            
        Raises:
            ValueError: If parameters are invalid
            MT5ConnectionError: If connection fails
            MT5ValidationError: If parameters are invalid
            MT5RequestError: If request fails
        """
        connection = MT5OrderHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")

        try:
            print(f"\n=== MT5 Order Request Debug ===")
            print(f"1. Connection state: connected={connection._connected}")
            print(f"2. Manager instance available: {connection.manager is not None}")
            
            # Convert datetime to timestamp if needed
            from_ts = MT5OrderHelper.convert_to_server_time(from_date, server_id, server_type)
            to_ts = MT5OrderHelper.convert_to_server_time(to_date, server_id, server_type)
            
            print(f"3. Requesting orders for login {login}")
            print(f"   From: {datetime.fromtimestamp(from_ts)} ({from_ts})")
            print(f"   To: {datetime.fromtimestamp(to_ts)} ({to_ts})")
            print(f"   Offset: {offset}")
            print(f"   Total: {total}")
            
            # Request orders
            orders = connection.manager.OrderRequestPage(
                login=login,
                from_date=from_ts,
                to_date=to_ts,
                offset=offset,
                total=total
            )
            
            if not orders:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    print("4. No orders found")
                    return []
                raise_mt5_error(error[1], "Failed to get orders")
                
            print(f"4. Found {len(orders)} orders")
            print("=== End Debug ===\n")
            
            return orders if orders else []
            
        except MT5BaseException:
            raise
        except Exception as e:
            print(f"\n=== MT5 Error Debug ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            error = MT5Manager.LastError()
            print(f"MT5 Last Error: {error}")
            print("=== End Error Debug ===\n")
            raise MT5ConnectionError(f"Failed to get orders: {str(e)}")

    @staticmethod
    async def update(
        order_id: int,
        params: Dict,
        server_id=None,
        server_type=None
    ) -> MT5Manager.MTOrder:
        """
        Update an order in the server database
        
        Args:
            order_id: Order ID to update
            params: Dictionary containing order details to update, which may include:
                - ExternalID: Order ID in external trading systems
                - Login: Client login
                - Dealer: Dealer login who processed the order
                - Symbol: Trading instrument
                - Digits: Decimal places in price
                - DigitsCurrency: Decimal places in deposit currency
                - ContractSize: Contract size of the symbol
                - State: Order state
                - Reason: Order reason
                - TimeSetup: Order setup time
                - TimeExpiration: Order expiration time
                - TimeDone: Order execution time
                - TimeSetupMsc: Order setup time in milliseconds
                - TimeDoneMsc: Order execution time in milliseconds
                - ModifyFlags: Modification flags
                - Type: Order type
                - TypeFill: Order filling type
                - TypeTime: Order lifetime type
                - PriceOrder: Order price
                - PriceTrigger: Stop limit order activation price
                - PriceSL: Stop Loss level
                - PriceTP: Take Profit level
                - Volume: Requested volume
                - VolumeExt: Extended accuracy volume
                - ExpertID: Expert Advisor ID
                - PositionID: Position ticket
                - Comment: Order comment
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            Updated MT5Manager.MTOrder object
            
        Raises:
            ValueError: If order_id is invalid
            MT5ConnectionError: If connection fails or order update fails
            MT5TradeError: If trade operation fails
            
        Note:
            - Order can only be updated from applications connected to the trade server
              where the order was created
            - Requires RIGHT_TRADE_MANAGER permission
        """
        if not isinstance(order_id, int) or order_id <= 0:
            raise ValueError("Order ID must be a positive integer")
            
        connection = MT5OrderHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Order Update Debug ===")
            print(f"1. Connection state: connected={connection._connected}")
            print(f"2. Manager instance available: {connection.manager is not None}")
            
            # Create order object with manager instance
            print("\n3. Creating order object")
            order = MT5Manager.MTOrder(connection.manager)
            if not order:
                error = MT5Manager.LastError()
                raise_mt5_error(error[1], "Failed to create order object")
            
            # Set order parameters with proper type conversion
            print("4. Setting order parameters:")
            
            # Set order ID
            order.Order = order_id
            
            # Integer parameters
            int_params = {
                'ExternalID': 'ExternalID',
                'Login': 'Login',
                'Dealer': 'Dealer',
                'Digits': 'Digits',
                'DigitsCurrency': 'DigitsCurrency',
                'State': 'State',
                'Reason': 'Reason',
                'TimeSetup': 'TimeSetup',
                'TimeExpiration': 'TimeExpiration',
                'TimeDone': 'TimeDone',
                'TimeSetupMsc': 'TimeSetupMsc',
                'TimeDoneMsc': 'TimeDoneMsc',
                'ModifyFlags': 'ModifyFlags',
                'Type': 'Type',
                'TypeFill': 'TypeFill',
                'TypeTime': 'TypeTime',
                'ExpertID': 'ExpertID',
                'PositionID': 'PositionID'
            }
            
            for param_name, attr_name in int_params.items():
                if param_name in params:
                    try:
                        value = int(params[param_name])
                        setattr(order, attr_name, value)
                        print(f"   - {param_name}: {getattr(order, attr_name)}")
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid {param_name}: must be an integer")
            
            # Float parameters
            float_params = {
                'ContractSize': 'ContractSize',
                'PriceOrder': 'PriceOrder',
                'PriceTrigger': 'PriceTrigger',
                'PriceSL': 'PriceSL',
                'PriceTP': 'PriceTP'
            }
            
            for param_name, attr_name in float_params.items():
                if param_name in params:
                    try:
                        value = float(params[param_name])
                        setattr(order, attr_name, value)
                        print(f"   - {param_name}: {getattr(order, attr_name)}")
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid {param_name}: must be a number")
            
            # Volume parameters with validation
            volume_params = {
                'Volume': 'Volume',
                'VolumeExt': 'VolumeExt'
            }
            
            for param_name, attr_name in volume_params.items():
                if param_name in params:
                    try:
                        volume = int(params[param_name])
                        if volume <= 0:
                            raise ValueError(f"{param_name} must be positive")
                        setattr(order, attr_name, volume)
                        print(f"   - {param_name}: {getattr(order, attr_name)}")
                    except (ValueError, OverflowError, TypeError):
                        raise ValueError(f"{param_name} must be a positive integer")
            
            # String parameters
            if 'Symbol' in params:
                order.Symbol = str(params['Symbol'])
                print(f"   - Symbol: {order.Symbol}")
            
            if 'Comment' in params:
                order.Comment = str(params['Comment'])
                print(f"   - Comment: {order.Comment}")
            
            # Update order on server
            print("\n5. Updating order on server")
            result = connection.manager.OrderUpdate(order)
            if not result:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTMAIN:
                    raise_mt5_error(error[1], "Order can only be updated from the server where it was created")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error(error[1], f"Order {order_id} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error(error[1], "Invalid order parameters")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID_VOLUME:
                    raise_mt5_error(error[1], "Invalid order volume")
                else:
                    raise_mt5_error(error[1], "Failed to update order")
            
            print("6. Order updated successfully")
            print("=== End Debug ===\n")
            
            return order
            
        except MT5BaseException:
            raise
        except ValueError:
            raise
        except Exception as e:
            print(f"\n=== MT5 Error Debug ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            error = MT5Manager.LastError()
            print(f"MT5 Last Error: {error}")
            print("=== End Error Debug ===\n")
            raise MT5ConnectionError(f"Failed to update order: {str(e)}")

    @staticmethod
    async def delete(
        order_id: int,
        server_id=None,
        server_type=None
    ) -> bool:
        """
        Delete an order from the server database
        
        Args:
            order_id: Order ID to delete
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            bool: True if order was deleted successfully
            
        Raises:
            ValueError: If order_id is invalid
            MT5ConnectionError: If connection fails
            MT5TradeError: If trade operation fails
        """
        if not isinstance(order_id, int) or order_id <= 0:
            raise ValueError("Order ID must be a positive integer")
            
        connection = MT5OrderHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Order Delete Debug ===")
            print(f"1. Connection state: connected={connection._connected}")
            print(f"2. Manager instance available: {connection.manager is not None}")
            
            print(f"\n3. Attempting to delete order {order_id}")
            result = connection.manager.OrderDelete(order_id)
            
            if not result:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTMAIN:
                    raise_mt5_error(error[1], "Order can only be deleted from the server where it was created")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error(error[1], f"Order {order_id} not found")
                else:
                    raise_mt5_error(error[1], "Failed to delete order")
            
            print("4. Order deleted successfully")
            print("=== End Debug ===\n")
            
            return True
            
        except MT5BaseException:
            raise
        except Exception as e:
            print(f"\n=== MT5 Error Debug ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            error = MT5Manager.LastError()
            print(f"MT5 Last Error: {error}")
            print("=== End Error Debug ===\n")
            raise MT5ConnectionError(f"Failed to delete order: {str(e)}")