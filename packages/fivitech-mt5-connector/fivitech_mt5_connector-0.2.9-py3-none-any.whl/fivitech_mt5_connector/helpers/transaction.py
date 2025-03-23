from typing import Dict, Optional
from ..pool import mt5_pools
from ..exceptions import (
    MT5BaseException, MT5ConnectionError, MT5TradeError,
    MT5ValidationError, MT5RequestError, raise_mt5_error
)
import MT5Manager
import logging

logger = logging.getLogger(__name__)

class MT5TransactionHelper:
    """Helper class for MT5 transaction operations"""
    
    @staticmethod
    def get_connection(server_id=None, server_type=None):
        """Get MT5 connection based on server_id or server_type"""
        if server_id is not None:
            return mt5_pools.get_by_id(server_id)
        elif server_type is not None:
            return mt5_pools.get_by_type(server_type)
        raise ValueError("Either server_id or server_type must be provided")
    
    @staticmethod
    async def deposit(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Deposit funds to user account
        
        Args:
            login: User login ID
            amount: Amount to deposit (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Deposit Debug ===")
            print(f"1. Processing deposit:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                amount,
                MT5Manager.MTDeal.EnDealAction.DEAL_BALANCE,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_TRADE_MAX_MONEY:
                    raise_mt5_error("MT_RET_TRADE_MAX_MONEY", "Amount exceeds maximum allowed")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_NO_MONEY:
                    raise_mt5_error("MT_RET_REQUEST_NO_MONEY", "Insufficient funds")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid deposit request")
                else:
                    raise_mt5_error(error[1], f"Deposit failed: {error}")
                
            print(f"2. Deposit successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to process deposit: {str(e)}")
    
    @staticmethod
    async def withdraw(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Withdraw funds from user account
        
        Args:
            login: User login ID
            amount: Amount to withdraw (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Withdrawal Debug ===")
            print(f"1. Processing withdrawal:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                -amount,  # Negative for withdrawal
                MT5Manager.MTDeal.EnDealAction.DEAL_BALANCE,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_TRADE_MAX_MONEY:
                    raise_mt5_error("MT_RET_TRADE_MAX_MONEY", "Amount exceeds maximum allowed")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_NO_MONEY:
                    raise_mt5_error("MT_RET_REQUEST_NO_MONEY", "Insufficient funds")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid withdrawal request")
                else:
                    raise_mt5_error(error[1], f"Withdrawal failed: {error}")
                
            print(f"2. Withdrawal successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to process withdrawal: {str(e)}")
    
    @staticmethod
    async def credit_in(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Add credit to user account
        
        Args:
            login: User login ID
            amount: Amount of credit to add (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Credit In Debug ===")
            print(f"1. Processing credit addition:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                amount,
                MT5Manager.MTDeal.EnDealAction.DEAL_CREDIT,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_TRADE_MAX_MONEY:
                    raise_mt5_error("MT_RET_TRADE_MAX_MONEY", "Amount exceeds maximum allowed")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid credit request")
                else:
                    raise_mt5_error(error[1], f"Credit addition failed: {error}")
                
            print(f"2. Credit addition successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to add credit: {str(e)}")
    
    @staticmethod
    async def credit_out(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Remove credit from user account
        
        Args:
            login: User login ID
            amount: Amount of credit to remove (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Credit Out Debug ===")
            print(f"1. Processing credit removal:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                -amount,  # Negative for removal
                MT5Manager.MTDeal.EnDealAction.DEAL_CREDIT,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_NO_MONEY:
                    raise_mt5_error("MT_RET_REQUEST_NO_MONEY", "Insufficient credit funds")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid credit removal request")
                else:
                    raise_mt5_error(error[1], f"Credit removal failed: {error}")
                
            print(f"2. Credit removal successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to remove credit: {str(e)}")
    
    @staticmethod
    async def charge_in(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Add charge to user account
        
        Args:
            login: User login ID
            amount: Amount to charge (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Charge amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Charge In Debug ===")
            print(f"1. Processing charge addition:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                amount,
                MT5Manager.MTDeal.EnDealAction.DEAL_CHARGE,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid charge request")
                else:
                    raise_mt5_error(error[1], f"Charge addition failed: {error}")
                
            print(f"2. Charge addition successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to add charge: {str(e)}")
    
    @staticmethod
    async def charge_out(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Remove charge from user account
        
        Args:
            login: User login ID
            amount: Amount of charge to remove (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Charge amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Charge Out Debug ===")
            print(f"1. Processing charge removal:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                -amount,  # Negative for removal
                MT5Manager.MTDeal.EnDealAction.DEAL_CHARGE,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid charge removal request")
                else:
                    raise_mt5_error(error[1], f"Charge removal failed: {error}")
                
            print(f"2. Charge removal successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to remove charge: {str(e)}")
    
    @staticmethod
    async def correction(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Make a correction to user account balance
        
        Args:
            login: User login ID
            amount: Amount to correct (positive or negative)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount == 0:
            raise ValueError("Correction amount cannot be zero")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Correction Debug ===")
            print(f"1. Processing correction:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                amount,
                MT5Manager.MTDeal.EnDealAction.DEAL_CORRECTION,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid correction request")
                else:
                    raise_mt5_error(error[1], f"Correction failed: {error}")
                
            print(f"2. Correction successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
        except MT5BaseException:
            raise
        except ValueError:
            raise
        except Exception as e:
            print(f"\n=== MT5 Error Debug ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Error details: {repr(e)}")  # This will give more details about the error
            print(f"Error attributes: {dir(e)}")  # This will show all attributes of the error
            error = MT5Manager.LastError()
            print(f"MT5 Last Error: {error}")
            print("=== End Error Debug ===\n")
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to make correction: {str(e)}")
    
    @staticmethod
    async def bonus_in(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Add bonus to user account
        
        Args:
            login: User login ID
            amount: Bonus amount to add (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Bonus amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Bonus In Debug ===")
            print(f"1. Processing bonus addition:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                amount,
                MT5Manager.MTDeal.EnDealAction.DEAL_BONUS,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid bonus request")
                else:
                    raise_mt5_error(error[1], f"Bonus addition failed: {error}")
                
            print(f"2. Bonus addition successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to add bonus: {str(e)}")
    
    @staticmethod
    async def bonus_out(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Remove bonus from user account
        
        Args:
            login: User login ID
            amount: Bonus amount to remove (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Bonus amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Bonus Out Debug ===")
            print(f"1. Processing bonus removal:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                -amount,  # Negative for removal
                MT5Manager.MTDeal.EnDealAction.DEAL_BONUS,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid bonus removal request")
                else:
                    raise_mt5_error(error[1], f"Bonus removal failed: {error}")
                
            print(f"2. Bonus removal successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to remove bonus: {str(e)}")
    
    @staticmethod
    async def add_commission(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Add commission to user account
        
        Args:
            login: User login ID
            amount: Commission amount (positive or negative)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount == 0:
            raise ValueError("Commission amount cannot be zero")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Commission Debug ===")
            print(f"1. Processing commission:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                amount,
                MT5Manager.MTDeal.EnDealAction.DEAL_AGENT,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid commission request")
                else:
                    raise_mt5_error(error[1], f"Commission addition failed: {error}")
                
            print(f"2. Commission addition successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to add commission: {str(e)}")
    
    @staticmethod
    async def remove_commission(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        remove commission from user account
        
        Args:
            login: User login ID
            amount: Commission amount (positive or negative)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount == 0:
            raise ValueError("Commission amount cannot be zero")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Commission Debug ===")
            print(f"1. Processing commission:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            # make sure the amount is turned to negative and not positive
            amount = -abs(amount)
            result = connection.manager.DealerBalance(
                login,
                amount,
                MT5Manager.MTDeal.EnDealAction.DEAL_COMMISSION,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid commission request")
                else:
                    raise_mt5_error(error[1], f"Commission addition failed: {error}")
                
            print(f"2. Commission addition successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to add commission: {str(e)}")

    @staticmethod
    async def add_rebate(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Add rebate to user account
        
        Args:
            login: User login ID
            amount: Rebate amount (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Rebate amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Rebate Debug ===")
            print(f"1. Processing rebate:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                amount,
                MT5Manager.MTDeal.EnDealAction.DEAL_AGENT,  # Action 18 for rebate
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid rebate request")
                else:
                    raise_mt5_error(error[1], f"Rebate addition failed: {error}")
                
            print(f"2. Rebate addition successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to add rebate: {str(e)}")
    
    @staticmethod
    async def compensation(
        login: int,
        amount: float,
        comment: str,
        server_id=None,
        server_type=None
    ) -> Dict:
        """
        Add compensation to user account
        
        Args:
            login: User login ID
            amount: Compensation amount (positive value)
            comment: Transaction comment (max 32 chars)
            server_id: Optional server ID
            server_type: Optional server type ('demo' or 'live')
            
        Returns:
            dict: Transaction result containing success status and deal ID
        """
        if amount <= 0:
            raise ValueError("Compensation amount must be positive")
            
        connection = MT5TransactionHelper.get_connection(server_id, server_type)
        if not connection or not connection.manager:
            raise MT5ConnectionError("MT5 connection or manager not available")
            
        try:
            print(f"\n=== MT5 Compensation Debug ===")
            print(f"1. Processing compensation:")
            print(f"   - Login: {login}")
            print(f"   - Amount: {amount}")
            print(f"   - Comment: {comment}")
            
            result = connection.manager.DealerBalance(
                login,
                amount,
                MT5Manager.MTDeal.EnDealAction.DEAL_SO_COMPENSATION,
                comment
            )
            
            if result is False:
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                    raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                    raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid compensation request")
                else:
                    raise_mt5_error(error[1], f"Compensation addition failed: {error}")
                
            print(f"2. Compensation addition successful")
            print("=== End Debug ===\n")
            
            return {
                'success': True,
                'deal_id': result
            }
            
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
            if isinstance(e, ValueError):
                raise
            raise MT5ConnectionError(f"Failed to add compensation: {str(e)}") 