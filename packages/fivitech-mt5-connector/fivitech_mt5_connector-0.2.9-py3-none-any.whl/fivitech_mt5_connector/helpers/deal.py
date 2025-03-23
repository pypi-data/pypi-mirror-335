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

class MT5DealHelper(MT5BaseHelper):
    """Helper class for MT5 deal operations"""

    @staticmethod
    def get_connection(server_id=None, server_type=None):
        """Get MT5 connection based on server_id or server_type"""
        if server_id is not None:
            return mt5_pools.get_by_id(server_id)
        elif server_type is not None:
            return mt5_pools.get_by_type(server_type)
        raise ValueError("Either server_id or server_type must be provided")

    @staticmethod
    async def get_paged(
        login: int,
        from_date: Union[datetime, int],
        to_date: Union[datetime, int],
        offset: int = 0,
        limit: int = 100,
        server_id=None,
        server_type=None
    ) -> List[MT5Manager.MTDeal]:
        """
        Get client deals with paged output
        
        Args:
            login: Client login ID
            from_date: Start date (datetime or unix timestamp)
            to_date: End date (datetime or unix timestamp)
            offset: Deal index to start from (default: 0)
            limit: Number of deals to retrieve (default: 100)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            List of deal dictionaries
        """
        connection = MT5DealHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")

        try:
            print(f"\n=== MT5 Deal Request Debug ===")
            print(f"1. Connection state: connected={connection._connected}")
            print(f"2. Manager instance available: {connection.manager is not None}")
            
            # Convert datetime to timestamp if needed
            from_ts = MT5DealHelper.convert_to_server_time(from_date, server_id, server_type)
            to_ts = MT5DealHelper.convert_to_server_time(to_date, server_id, server_type)
            
            print(f"3. Requesting deals for login {login}")
            print(f"   From: {datetime.fromtimestamp(from_ts)} ({from_ts})")
            print(f"   To: {datetime.fromtimestamp(to_ts)} ({to_ts})")
            print(f"   Offset: {offset}")
            print(f"   Total: {limit}")
            
            # Request deals
            deals = connection.manager.DealRequestPage(
                login=login,
                from_date=from_ts,
                to_date=to_ts,
                offset=offset,
                total=limit
            )
            
            if not deals:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    print("4. No deals found")
                    return []
                raise_mt5_error(error[1], "Failed to get deals")
                
            print(f"4. Found {len(deals)} deals")
            print("=== End Debug ===\n")
            
            return deals if deals else []
            
        except MT5BaseException:
            raise
        except Exception as e:
            print(f"\n=== MT5 Error Debug ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            error = MT5Manager.LastError()
            print(f"MT5 Last Error: {error}")
            print("=== End Error Debug ===\n")
            raise MT5ConnectionError(f"Failed to get deals: {str(e)}")

    @staticmethod
    async def update(
        deal_id: int,
        params: Dict,
        server_id=None,
        server_type=None
    ) -> MT5Manager.MTDeal:
        """
        Update a deal in the server database
        
        Args:
            deal_id: Deal ID to update
            params: Dictionary containing deal details to update, which may include:
                - ExternalID: Deal ID in external trading systems
                - Login: Client login
                - Dealer: Dealer login who processed the deal
                - Order: Ticket of the order that resulted in this deal
                - Action: Type of action performed
                - Entry: Deal direction
                - Digits: Decimal places in price
                - DigitsCurrency: Decimal places in deposit currency
                - ContractSize: Contract size of the symbol
                - Time: Deal execution time
                - Symbol: Trading instrument
                - Price: Deal price
                - PriceSL: Stop Loss level
                - PriceTP: Take Profit level
                - Volume: Deal volume
                - VolumeExt: Extended accuracy volume
                - VolumeClosed: Closed position volume
                - VolumeClosedExt: Extended accuracy closed volume
                - Profit: Deal profit
                - Value: Deal value in deposit currency
                - Storage: Swap value
                - Commission: Commission amount
                - Fee: Fee amount
                - RateProfit: Profit currency exchange rate
                - RateMargin: Margin currency exchange rate
                - ExpertID: Expert Advisor ID
                - PositionID: Position ticket
                - Comment: Deal comment
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            Updated MT5Manager.MTDeal object
            
        Raises:
            ValueError: If deal_id is invalid
            MT5ConnectionError: If connection fails or deal update fails
            
        Note:
            - Deal can only be updated from applications connected to the trade server
              where the deal was created
            - Requires RIGHT_TRADE_MANAGER permission
            - Changes to profit, commission, or fees will affect the user's balance, need to be fixed manually
        """
        if not isinstance(deal_id, int) or deal_id <= 0:
            raise ValueError("Deal ID must be a positive integer")
            
        connection = MT5DealHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Deal Update Debug ===")
            print(f"1. Connection state: connected={connection._connected}")
            print(f"2. Manager instance available: {connection.manager is not None}")
            
            # Create deal object with manager instance
            print("\n3. Creating deal object")
            deal = MT5Manager.MTDeal(connection.manager)
            if not deal:
                error = MT5Manager.LastError()
                raise_mt5_error(error[1], "Failed to create deal object")
            
            # Set deal parameters with proper type conversion
            print("4. Setting deal parameters:")
            
            # Set deal ID
            deal.Deal = deal_id
            
            # Integer parameters
            int_params = {
                'ExternalID': 'ExternalID',
                'Login': 'Login',
                'Dealer': 'Dealer',
                'Order': 'Order',
                'Action': 'Action',
                'Entry': 'Entry',
                'Digits': 'Digits',
                'DigitsCurrency': 'DigitsCurrency',
                'ExpertID': 'ExpertID',
                'PositionID': 'PositionID'
            }
            
            for param_name, attr_name in int_params.items():
                if param_name in params:
                    try:
                        value = int(params[param_name])
                        setattr(deal, attr_name, value)
                        print(f"   - {param_name}: {getattr(deal, attr_name)}")
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid {param_name}: must be an integer")
            
            # Float parameters
            float_params = {
                'ContractSize': 'ContractSize',
                'Price': 'Price',
                'PriceSL': 'PriceSL',
                'PriceTP': 'PriceTP',
                'Profit': 'Profit',
                'Value': 'Value',
                'Storage': 'Storage',
                'Commission': 'Commission',
                'Fee': 'Fee',
                'RateProfit': 'RateProfit',
                'RateMargin': 'RateMargin'
            }
            
            for param_name, attr_name in float_params.items():
                if param_name in params:
                    try:
                        value = float(params[param_name])
                        setattr(deal, attr_name, value)
                        print(f"   - {param_name}: {getattr(deal, attr_name)}")
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid {param_name}: must be a number")
            
            # Volume parameters with validation
            volume_params = {
                'Volume': 'Volume',
                'VolumeExt': 'VolumeExt',
                'VolumeClosed': 'VolumeClosed',
                'VolumeClosedExt': 'VolumeClosedExt'
            }
            
            for param_name, attr_name in volume_params.items():
                if param_name in params:
                    try:
                        volume = int(params[param_name])
                        if volume <= 0:
                            raise ValueError(f"{param_name} must be positive")
                        setattr(deal, attr_name, volume)
                        print(f"   - {param_name}: {getattr(deal, attr_name)}")
                    except (ValueError, OverflowError, TypeError):
                        raise ValueError(f"{param_name} must be a positive integer")
            
            # String parameters
            if 'Symbol' in params:
                deal.Symbol = str(params['Symbol'])
                print(f"   - Symbol: {deal.Symbol}")
            
            if 'Comment' in params:
                deal.Comment = str(params['Comment'])
                print(f"   - Comment: {deal.Comment}")
            
            # Time parameter
            if 'Time' in params:
                if isinstance(params['Time'], datetime):
                    deal.Time = int(params['Time'].timestamp())
                else:
                    deal.Time = int(params['Time'])
                print(f"   - Time: {deal.Time}")
            
            # Update deal on server
            print("\n5. Updating deal on server")
            result = connection.manager.DealUpdate(deal)
            if not result:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTMAIN:
                    raise_mt5_error(error[1], "Deal can only be updated from the server where it was created")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error(error[1], f"Deal {deal_id} not found")
                else:
                    raise_mt5_error(error[1], "Failed to update deal")
            
            print("6. Deal updated successfully")
            print("=== End Debug ===\n")
            
            return deal
            
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
            raise MT5ConnectionError(f"Failed to update deal: {str(e)}")