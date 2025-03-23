from typing import List, Optional, Dict, Any, Union
from ..exceptions import (
    MT5BaseException, MT5ConnectionError, MT5TradeError,
    MT5ValidationError, MT5RequestError, raise_mt5_error
)
from ..pool import mt5_pools
import MT5Manager
import logging

logger = logging.getLogger(__name__)

class MT5PositionHelper:
    @staticmethod
    def get_connection(server_id=None, server_type=None):
        """Get MT5 connection based on server_id or server_type"""
        if server_id is not None:
            return mt5_pools.get_by_id(server_id)
        elif server_type is not None:
            return mt5_pools.get_by_type(server_type)
        raise ValueError("Either server_id or server_type must be provided")

    @staticmethod
    def get_positions(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all positions or positions for a specific symbol.
        
        Args:
            symbol: Optional symbol to filter positions
            
        Returns:
            List of position dictionaries
            
        Raises:
            MT5ConnectionError: If connection fails
            MT5ValidationError: If symbol is invalid
        """
        try:
            if symbol:
                positions = MT5Manager.positions_get(symbol=symbol)
            else:
                positions = MT5Manager.positions_get()
                
            if positions is None:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    return []
                raise_mt5_error(error[1], "Failed to get positions")
                
            return [position._asdict() for position in positions]
            
        except MT5BaseException:
            raise
        except Exception as e:
            logger.error(f"Failed to get positions: {str(e)}")
            raise MT5ConnectionError(f"Failed to get positions: {str(e)}")

    @staticmethod
    def get_position(ticket: int) -> Optional[Dict[str, Any]]:
        """
        Get position details by ticket number.
        
        Args:
            ticket: Position ticket number
            
        Returns:
            Position dictionary if found, None otherwise
            
        Raises:
            ValueError: If ticket is invalid
            MT5ConnectionError: If connection fails
            MT5ValidationError: If position not found
        """
        if not isinstance(ticket, int) or ticket <= 0:
            raise ValueError("Ticket must be a positive integer")
            
        try:
            positions = MT5Manager.positions_get(ticket=ticket)
            if positions is None:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    return None
                raise_mt5_error(error[1], f"Failed to get position {ticket}")
                
            return positions[0]._asdict() if positions else None
            
        except MT5BaseException:
            raise
        except Exception as e:
            logger.error(f"Failed to get position {ticket}: {str(e)}")
            raise MT5ConnectionError(f"Failed to get position {ticket}: {str(e)}")
        
    @staticmethod
    async def get_open(login: Union[int, List[int]], server_id=None, server_type=None) -> List[MT5Manager.MTOrder]:
        """
        Get open positions for one or multiple users
        
        Args:
            login: Single user login ID or list of login IDs
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            List of open positions as dictionaries
            
        Raises:
            ValueError: If login is invalid
            MT5ConnectionError: If connection fails
        """
        # Convert single login to list for uniform processing
        logins = [login] if isinstance(login, int) else login
        
        # Validate all logins
        if not all(isinstance(l, int) and l > 0 for l in logins):
            raise ValueError("All logins must be positive integers")
                
        connection = MT5PositionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
                
        try:
            print(f"\n=== MT5 Open Positions Request Debug ===")
            print(f"1. Connection state: connected={connection._connected}")
            print(f"2. Manager instance available: {connection.manager is not None}")
            print(f"3. Requesting open positions for {len(logins)} users")
            
            # For single login, use OrderGetOpen
            if len(logins) == 1:
                orders = connection.manager.PositionGet(logins[0])
                if orders is None:
                    error = MT5Manager.LastError()
                    if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                        print("4. No open positions found")
                        return []
                    raise_mt5_error(error[1], "Failed to get open positions")
                    
                print(f"4. Found {len(orders) if orders else 0} open positions")
                print("=== End Debug ===\n")
                return orders if orders else []
                
            # For multiple logins, use OrderGetByLogins
            orders = connection.manager.PositionGetByLogins(logins)
            if orders is None:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    print("4. No open positions found")
                    return []
                raise_mt5_error(error[1], "Failed to get open positions")
                
            print(f"4. Found {len(orders) if orders else 0} open positions")
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
            raise MT5ConnectionError(f"Failed to get open positions: {str(e)}")

    @staticmethod
    def close_position(ticket: int, volume: Optional[float] = None) -> bool:
        """
        Close a position by ticket number.
        
        Args:
            ticket: Position ticket number
            volume: Optional volume for partial close
            
        Returns:
            bool: True if position was closed successfully
            
        Raises:
            ValueError: If ticket is invalid or volume is invalid
            MT5ConnectionError: If connection fails
            MT5TradeError: If trade operation fails
            MT5ValidationError: If position not found
        """
        if not isinstance(ticket, int) or ticket <= 0:
            raise ValueError("Ticket must be a positive integer")
            
        if volume is not None and volume <= 0:
            raise ValueError("Volume must be positive")
            
        try:
            position = MT5PositionHelper.get_position(ticket)
            if not position:
                raise MT5ValidationError(f"Position {ticket} not found")

            request = {
                "action": MT5Manager.TRADE_ACTION_DEAL,
                "position": ticket,
                "symbol": position["symbol"],
                "volume": volume if volume else position["volume"],
                "type": MT5Manager.ORDER_TYPE_SELL if position["type"] == 0 else MT5Manager.ORDER_TYPE_BUY,
                "price": MT5Manager.symbol_info_tick(position["symbol"]).bid if position["type"] == 0 else MT5Manager.symbol_info_tick(position["symbol"]).ask,
                "deviation": 20,
                "type_time": MT5Manager.ORDER_TIME_GTC,
                "type_filling": MT5Manager.ORDER_FILLING_IOC,
            }

            result = MT5Manager.order_send(request)
            if not result or result.retcode != MT5Manager.TRADE_RETCODE_DONE:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error(error[1], "Invalid close position request")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID_VOLUME:
                    raise_mt5_error(error[1], "Invalid volume for position close")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_TRADE_DISABLED:
                    raise_mt5_error(error[1], "Trading is disabled")
                else:
                    raise_mt5_error(error[1], "Failed to close position")
                    
            return True
            
        except MT5BaseException:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to close position {ticket}: {str(e)}")
            raise MT5ConnectionError(f"Failed to close position {ticket}: {str(e)}")

    @staticmethod
    def modify_position(
        ticket: int,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> bool:
        """
        Modify stop loss and/or take profit of an existing position.
        
        Args:
            ticket: Position ticket number
            sl: New stop loss price
            tp: New take profit price
            
        Returns:
            bool: True if position was modified successfully
            
        Raises:
            ValueError: If ticket is invalid or sl/tp are invalid
            MT5ConnectionError: If connection fails
            MT5TradeError: If trade operation fails
            MT5ValidationError: If position not found
        """
        if not isinstance(ticket, int) or ticket <= 0:
            raise ValueError("Ticket must be a positive integer")
            
        if sl is not None and sl <= 0:
            raise ValueError("Stop loss must be positive")
            
        if tp is not None and tp <= 0:
            raise ValueError("Take profit must be positive")
            
        try:
            position = MT5PositionHelper.get_position(ticket)
            if not position:
                raise MT5ValidationError(f"Position {ticket} not found")

            request = {
                "action": MT5Manager.TRADE_ACTION_SLTP,
                "position": ticket,
                "symbol": position["symbol"],
            }
            
            if sl is not None:
                request["sl"] = sl
            if tp is not None:
                request["tp"] = tp

            result = MT5Manager.order_send(request)
            if not result or result.retcode != MT5Manager.TRADE_RETCODE_DONE:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error(error[1], "Invalid modify position request")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID_VOLUME:
                    raise_mt5_error(error[1], "Invalid stop loss or take profit values")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_TRADE_DISABLED:
                    raise_mt5_error(error[1], "Trading is disabled")
                else:
                    raise_mt5_error(error[1], "Failed to modify position")
                    
            return True
            
        except MT5BaseException:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to modify position {ticket}: {str(e)}")
            raise MT5ConnectionError(f"Failed to modify position {ticket}: {str(e)}") 