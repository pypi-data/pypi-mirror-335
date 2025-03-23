from typing import Dict, List, Optional, Union
from ..pool import mt5_pools
from ..exceptions import (
    MT5BaseException, MT5ConnectionError, MT5ArchiveError,
    MT5UserError, MT5AuthenticationError, MT5LimitError,
    MT5ValidationError, MT5ImportError, raise_mt5_error
)
import MT5Manager
import asyncio

def print_account_info(account):
    """Helper function to print account information"""
    # Get all attributes of the account object
    account_info = {
        name: getattr(account, name)
        for name in dir(account)
        if not name.startswith('_') and not callable(getattr(account, name))
    }
    
    # Print all available properties
    for name, value in account_info.items():
        print(f"   - {name}: {value}")

class MT5UserHelper:
  @staticmethod
  def get_connection(server_id=None, server_type=None):
    """Get MT5 connection based on server_id or server_type"""
    if server_id is not None:
      return mt5_pools.get_by_id(server_id)
    elif server_type is not None:
      return mt5_pools.get_by_type(server_type)
    raise ValueError("Either server_id or server_type must be provided")
  
  @staticmethod
  async def set_user_rights(login: int, rights_to_set=None, rights_to_remove=None, server_id=None, server_type=None):
    """
    Set or remove user rights
    
    Args:
        login: User login ID
        rights_to_set: List of rights to enable
        rights_to_remove: List of rights to disable
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        Updated user object
    """
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
            
    try:
        print(f"\n=== MT5 User Rights Debug ===")
        print(f"1. Processing user rights update:")
        print(f"   - Login: {login}")
        print(f"   - Rights to set: {rights_to_set}")
        print(f"   - Rights to remove: {rights_to_remove}")
        
        # Request current user
        user = connection.manager.UserRequest(login)
        if not user:
            error = MT5Manager.LastError()
            if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                raise_mt5_error("MT_RET_ERR_NOTFOUND", f"User {login} not found")
            else:
                raise_mt5_error(error[1], f"Failed to get user: {error}")
                
        current_rights = user.Rights
        
        # Set new rights if specified
        if rights_to_set:
            for right in rights_to_set:
                current_rights |= right
                
        # Remove rights if specified
        if rights_to_remove:
            for right in rights_to_remove:
                current_rights &= ~right
                
        # Update user rights
        user.Rights = current_rights
        
        # Update user on server
        if not connection.manager.UserUpdate(user):
            error = MT5Manager.LastError()
            if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_REQUEST_INVALID:
                raise_mt5_error("MT_RET_REQUEST_INVALID", "Invalid user rights update request")
            elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_AUTH_CLIENT_INVALID:
                raise_mt5_error("MT_RET_AUTH_CLIENT_INVALID", "Invalid user authentication")
            else:
                raise_mt5_error(error[1], f"Failed to update user rights: {error}")
                
        print(f"2. User rights update successful")
        print("=== End Debug ===\n")
        
        return user
            
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
        raise MT5ConnectionError(f"Failed to set user rights: {str(e)}")
            
  @staticmethod
  async def create(
      params: Dict,
      master_pass: str,
      investor_pass: str,
      server_id=None,
      server_type=None
  ):
    """
    Create a new MT5 account
    
    Args:
      params: Dictionary containing user details including:
        - Group: Trading group name (required)
        - Leverage: Account leverage (required)
        - FirstName: First name (required)
        - LastName: Last name (required)
        - Login: Optional, if 0 or not provided, server will auto-assign
        - enabled: Boolean to enable/disable account
      master_pass: Master password (must contain lowercase, uppercase, numbers, special chars)
      investor_pass: Investor password (must contain lowercase, uppercase, numbers, special chars)
      server_id: Optional server ID
      server_type: Optional server type ('demo' or 'live')
        
    Returns:
      Created user object
        
    Raises:
      MT5ConnectionError: If connection fails
      ValueError: If required parameters are missing or invalid
    """
    # Validate required parameters
    if not params.get('Group'):
        raise ValueError("Group is required in params")
    if not params.get('Leverage'):
        raise ValueError("Leverage is required in params")
    if not (params.get('FirstName') or params.get('LastName')):
        raise ValueError("FirstName or LastName is required in params")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
    
    # Validate group exists
    try:
        group = connection.manager.GroupGet(params['Group'])
        if not group:
            print(f"Group {params['Group']} not found. Available groups:")
            pos = 0
            while True:
                group = connection.manager.GroupNext(pos)
                if not group:
                    break
                print(f"- {group.Group}")
                pos += 1
            raise ValueError(f"Group {params['Group']} does not exist on the server")
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error checking group: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        raise MT5ConnectionError(f"Failed to validate group: {str(e)}")
    
    # Validate passwords
    if len(master_pass) < 8:
        raise ValueError("Master password must be at least 8 characters")
    if len(investor_pass) < 8:
        raise ValueError("Investor password must be at least 8 characters")

    try:
        print(f"\n=== MT5 Account Creation Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        
        # Create MTUser object properly with manager instance
        print("\n3. Creating MTUser object with manager instance")
        user = MT5Manager.MTUser(connection.manager)
        
        # Set user parameters
        print("4. Setting user parameters:")
        if params.get('Group'):
            user.Group = params['Group']
            print(f"   - Group: {user.Group}")
        if params.get('Leverage'):
            user.Leverage = params['Leverage']
            print(f"   - Leverage: {user.Leverage}")
        if params.get('FirstName'):
            user.FirstName = params.get('FirstName', '')
            print(f"   - FirstName: {user.FirstName}")
        if params.get('LastName'):
            user.LastName = params.get('LastName', '')
            print(f"   - LastName: {user.LastName}")
        if params.get('Email'):
            user.EMail = params.get('Email', '')
            print(f"   - Email: {user.EMail}")
        if params.get('Phone'):
            user.Phone = params.get('Phone', '')
            print(f"   - Phone: {user.Phone}")
        if params.get('MiddleName'):
            user.MiddleName = params.get('MiddleName', '')
            print(f"   - MiddleName: {user.MiddleName}")
        if params.get('Company'):
            user.Company = params.get('Company', '')
            print(f"   - Company: {user.Company}")
        if params.get('Account'):
            user.Account = params.get('Account', '')
            print(f"   - Account: {user.Account}")
        if params.get('Country'):
            user.Country = params.get('Country', '')
            print(f"   - Country: {user.Country}")
        if params.get('Language'):
            user.Language = params.get('Language', '')
            print(f"   - Language: {user.Language}")
        if params.get('City'):
            user.City = params.get('City', '')
            print(f"   - City: {user.City}")
        if params.get('Address'):
            user.Address = params.get('Address', '')
            print(f"   - Address: {user.Address}")
        if params.get('ZIPCode'):
            user.ZIPCode = params.get('ZIPCode', '')
            print(f"   - ZIPCode: {user.ZIPCode}")
        if params.get('State'):
            user.State = params.get('State', '')
            print(f"   - State: {user.State}")
        if params.get('MQID'):
            user.MQID = params.get('MQID', '')
            print(f"   - MQID: {user.MQID}")
        if params.get('ClientID'):
            user.ClientID = params.get('ClientID', '')
            print(f"   - ClientID: {user.ClientID}")
        if params.get('Comment'):
            user.Comment = params.get('Comment', '')
            print(f"   - Comment: {user.Comment}")
        if params.get('Agent'):
            user.Agent = params.get('Agent', '')
            print(f"   - Agent: {user.Agent}")
        
        if params.get('Login'):
            user.Login = int(params['Login'])
            print(f"   - Login: {user.Login}")

        # Set initial user rights
        initial_rights = (
            MT5Manager.MTUser.EnUsersRights.USER_RIGHT_ENABLED |  # Allow connection
            MT5Manager.MTUser.EnUsersRights.USER_RIGHT_PASSWORD |  # Allow password change
            MT5Manager.MTUser.EnUsersRights.USER_RIGHT_EXPERT |  # Allow Expert Advisors
            MT5Manager.MTUser.EnUsersRights.USER_RIGHT_TRAILING  # Allow trailing stops
        )
        user.Rights = initial_rights
        print(f"   - Group: {user.Group}")
        print(f"   - Leverage: {user.Leverage}")
        print(f"   - FirstName: {user.FirstName}")
        print(f"   - LastName: {user.LastName}")
        print(f"   - Email: {user.EMail}")
        print(f"   - Phone: {user.Phone}")
        print(f"   - Login: {user.Login if params.get('login') else 'Auto-assigned'}")
        print(f"   - Rights: {user.Rights}")
        
        print("\n5. Checking available groups:")
        pos = 0
        available_groups = []
        while True:
            group = connection.manager.GroupNext(pos)
            if not group:
                break
            available_groups.append(group.Group)
            pos += 1
        print(f"   Available groups: {available_groups}")
        
        if user.Group not in available_groups:
            raise ValueError(f"Group '{user.Group}' not found. Available groups: {available_groups}")
            
        print(f"\n6. Password lengths - Master: {len(master_pass)}, Investor: {len(investor_pass)}")
        
        print("\n7. Attempting UserAdd call...")
        # Try to get last error before UserAdd
        try:
            last_error = MT5Manager.LastError()
            print(f"   Last error before UserAdd: {last_error}")
        except Exception as err:
            print(f"   Could not get last error: {str(err)}")
            
        result = connection.manager.UserAdd(user, master_pass, investor_pass)
        print(f"8. UserAdd result: {result}")
        
        if result:
            print("9. Success! Account details:")
            print(f"   - Login: {user.Login}")
            print(f"   - Group: {user.Group}")
            print(f"   - Name: {user.Name}")
            return user
        else:
            print("9. Failed: UserAdd returned False")
            error = MT5Manager.LastError()
            print(f"   MT5 Error: {error}")
            
            # Check specific error codes
            if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_USR_LOGIN_EXHAUSTED:
                raise raise_mt5_error("MT_RET_USR_LOGIN_EXHAUSTED", "No free logins on server")
            elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_USR_LOGIN_PROHIBITED:
                raise raise_mt5_error("MT_RET_USR_LOGIN_PROHIBITED", "Can't add user for non current server")
            elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_USR_LOGIN_EXIST:
                raise raise_mt5_error("MT_RET_USR_LOGIN_EXIST", "User with same login already exists")
            else:
                raise_mt5_error(error[1], f"Failed to create user: {error}")
        
        print("6. User created successfully")
        print("=== End Debug ===\n")
        
        return user
        
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
        raise MT5ConnectionError(f"Failed to create user: {str(e)}")

  @staticmethod
  async def get(login: Union[int, List[int]], server_id=None, server_type=None) -> Union[MT5Manager.MTUser, Dict[int, MT5Manager.MTUser]]:
    """
    Get user information for one or multiple users
    
    Args:
        login: Single user login ID or list of login IDs
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        If single login: MTUser object if user exists, None if not found
        If multiple logins: Dictionary mapping each login to its MTUser object (or None if not found)
        
    Raises:
        ValueError: If login is invalid
        MT5ConnectionError: If connection fails or operation fails
    """
    # Validate single login first
    if login is None:
        raise ValueError("Login cannot be None")
        
    if isinstance(login, (str, bool, float)):
        raise ValueError("Login must be an integer")
        
    # Convert single login to list for uniform processing
    is_single = isinstance(login, int)
    logins = [login] if is_single else login
    
    # Validate all logins are positive integers
    if not all(isinstance(l, int) and l > 0 for l in logins):
        raise ValueError("All logins must be positive integers")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
            
    try:
        print(f"\n=== MT5 User Get Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        
        # For single login, use the original method
        if is_single:
            print(f"\n3. Getting single user for login: {login}")
            user = connection.manager.UserRequest(login)
            if user:
                print(f"4. User found:")
                print(f"   - Login: {user.Login}")
                print(f"   - Name: {user.Name}")
                print(f"   - Group: {user.Group}")
            else:
                print(f"4. User {login} not found")
            print("=== End Debug ===\n")
            return user
                
        # For multiple logins, use batch request
        print(f"\n3. Getting batch user details for {len(logins)} logins:")
        for l in logins:
            print(f"   - Login: {l}")
                
        # Get users in batch
        users = connection.manager.UserRequestByLogins(logins)
        users = users or []  # Convert None to empty list if no users found
        
        # Create dictionary mapping logins to user objects
        user_map = {login: None for login in logins}  # Initialize all to None
        for user in users:
            user_map[user.Login] = user
            print(f"\n4. User found for login {user.Login}:")
            print(f"   - Name: {user.Name}")
            print(f"   - Group: {user.Group}")
                
        # Log not found users
        not_found = [login for login, user in user_map.items() if user is None]
        if not_found:
            print("\nUsers not found:")
            for login in not_found:
                print(f"   - Login: {login}")
                
        print("=== End Debug ===\n")
        return user_map
            
    except ValueError:
        # Re-raise ValueError exceptions directly
        raise
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        raise MT5ConnectionError(f"Failed to get user information: {str(e)}")

  @staticmethod
  async def exists(login: Union[int, List[int]], server_id=None, server_type=None) -> Union[bool, Dict[int, bool]]:
    """
    Check if one or multiple users exist by login
    
    Args:
        login: Single user login ID or list of login IDs
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        If single login: bool - True if user exists, False otherwise
        If multiple logins: Dict[int, bool] - Dictionary mapping each login to its existence status
    """
    # Convert single login to list for uniform processing
    logins = [login] if isinstance(login, int) else login
    
    # Validate all logins
    if not all(isinstance(l, int) and l > 0 for l in logins):
        raise ValueError("All logins must be positive integers")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
            
    try:
        print(f"\n=== MT5 User Check Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        
        # For single login, use the original method
        if len(logins) == 1:
            print(f"\n3. Checking single user existence for login: {logins[0]}")
            user = connection.manager.UserRequest(logins[0])
            exists = user is not False
            
            print(f"4. User exists: {exists}")
            if exists:
                print(f"   - Login: {user.Login}")
                print(f"   - Name: {user.Name}")
                print(f"   - Group: {user.Group}")
                print(f"   - Balance: {user.Balance}")
                print(f"   - Credit: {user.Credit}")
                
            print("=== End Debug ===\n")
            return exists
                
        # For multiple logins, use batch request
        print(f"\n3. Checking batch user existence for {len(logins)} logins:")
        for l in logins:
            print(f"   - Login: {l}")
                
        # Get users in batch
        users = connection.manager.UserRequestByLogins(logins)
        
        # Create result dictionary mapping login to existence status
        existence_results = {login: False for login in logins}  # Initialize all as False
        
        if users:
            # Update existence status for found users
            for user in users:
                existence_results[user.Login] = True
                print(f"\n4. Found user:")
                print(f"   - Login: {user.Login}")
                print(f"   - Name: {user.Name}")
                print(f"   - Group: {user.Group}")
                print(f"   - Balance: {user.Balance}")
                print(f"   - Credit: {user.Credit}")
                    
        print("\n5. Batch check results:")
        for login, exists in existence_results.items():
            print(f"   - Login {login}: {'Exists' if exists else 'Does not exist'}")
        print("=== End Debug ===\n")
        
        return existence_results if len(logins) > 1 else existence_results[logins[0]]
            
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error checking user existence: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        return False if isinstance(login, int) else {l: False for l in logins}

  @staticmethod
  async def update(login: int, params: dict, server_id=None, server_type=None):
    """
    Update an existing user's information
    
    Args:
        login: User login ID
        params: Dictionary containing user details to update
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        Updated user object
        
    Raises:
        MT5ConnectionError: If connection fails or user doesn't exist
        ValueError: If required parameters are missing or invalid
    """
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
            
    try:
        print(f"\n=== MT5 User Update Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        
        # Check if user exists
        print(f"\n3. Checking if user {login} exists")
        user = connection.manager.UserRequest(login)
        if not user:
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"User {login} not found: {error}")
                
        print("4. User found, updating parameters:")
        
        # Update user parameters if provided
        if 'Group' in params:
            user.Group = str(params['Group'])
        if 'Leverage' in params:
            user.Leverage = int(params['Leverage'])
        if 'FirstName' in params:
            user.FirstName = str(params['FirstName'])
        if 'LastName' in params:
            user.LastName = str(params['LastName'])
        if 'Email' in params:
            user.EMail = str(params['Email'])
        if 'Phone' in params:
            user.Phone = str(params['Phone'])
        if 'MiddleName' in params:
            user.MiddleName = str(params['MiddleName'])
        if 'Company' in params:
            user.Company = str(params['Company'])
        if 'Account' in params:
            user.Account = str(params['Account'])
        if 'Country' in params:
            user.Country = str(params['Country'])
        if 'Language' in params:
            user.Language = str(params['Language'])
        if 'City' in params:
            user.City = str(params['City'])
        if 'Address' in params:
            user.Address = str(params['Address'])
        if 'ZIPCode' in params:
            user.ZIPCode = str(params['ZIPCode'])
        if 'State' in params:
            user.State = str(params['State'])
        if 'MQID' in params:
            user.MQID = str(params['MQID'])
        if 'ClientID' in params:
            user.ClientID = str(params['ClientID'])
        if 'Comment' in params:
            user.Comment = str(params['Comment'])
        if 'Agent' in params:
            user.Agent = str(params['Agent'])

        # Print updated parameters
        print(f"   - Group: {user.Group}")
        print(f"   - Leverage: {user.Leverage}")
        print(f"   - FirstName: {user.FirstName}")
        print(f"   - LastName: {user.LastName}")
        print(f"   - Email: {user.EMail}")
        print(f"   - Phone: {user.Phone}")
        
        print("\n5. Attempting UserUpdate call...")
        if not connection.manager.UserUpdate(user):
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"Failed to update user: {error}")
                
        print("6. User updated successfully")
        
        # Get updated user info
        updated_user = connection.manager.UserRequest(login)
        if not updated_user:
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"Failed to get updated user info: {error}")
                
        print("\n7. Updated user details:")
        print(f"   - Login: {updated_user.Login}")
        print(f"   - Group: {updated_user.Group}")
        print(f"   - Name: {updated_user.Name}")
        
        print("=== End Debug ===\n")
        return updated_user
            
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        raise MT5ConnectionError(f"Failed to update user: {str(e)}")

  @staticmethod
  async def change_password(
      login: int,
      password: str,
      password_type: str = 'main',
      server_id=None,
      server_type=None
  ):
      """
      Change a user's password
      
      Args:
          login: User login ID
          password: New password (must contain lowercase, uppercase, numbers, and special chars)
          password_type: Type of password to change ('main', 'investor', or 'api')
          server_id: Optional server ID
          server_type: Optional server type ('demo' or 'live')
          
      Returns:
          bool: True if password was changed successfully
          
      Raises:
          MT5ConnectionError: If connection fails or user doesn't exist
          ValueError: If password requirements are not met
      """
      # Validate password requirements
      if len(password) < 8:
          raise ValueError("Password must be at least 8 characters long")
      if len(password) > 16:
          raise ValueError("Password must not exceed 16 characters")
            
      # Check password complexity
      has_lower = any(c.islower() for c in password)
      has_upper = any(c.isupper() for c in password)
      has_digit = any(c.isdigit() for c in password)
      has_special = any(not c.isalnum() for c in password)
      
      if not all([has_lower, has_upper, has_digit, has_special]):
          raise ValueError(
              "Password must contain all of: lowercase letters, uppercase letters, "
              "numbers, and special characters"
          )
            
      # Get connection
      connection = MT5UserHelper.get_connection(server_id, server_type)
      if not connection or not connection.manager:
          raise MT5ConnectionError("MT5 connection or manager not available")
            
      try:
          print(f"\n=== MT5 Password Change Debug ===")
          print(f"1. Connection state: connected={connection._connected}")
          print(f"2. Manager instance available: {connection.manager is not None}")
          
          # Check if user exists
          print(f"\n3. Checking if user {login} exists")
          user = connection.manager.UserRequest(login)
          if not user:
              error = MT5Manager.LastError()
              raise MT5ConnectionError(f"User {login} not found: {error}")
              
          # Map password type to MT5Manager enum
          password_type = password_type.lower()
          if password_type == 'main':
              pass_type = MT5Manager.MTUser.EnUsersPasswords.USER_PASS_MAIN
          elif password_type == 'investor':
              pass_type = MT5Manager.MTUser.EnUsersPasswords.USER_PASS_INVESTOR
          elif password_type == 'api':
              pass_type = MT5Manager.MTUser.EnUsersPasswords.USER_PASS_API
          else:
              raise ValueError("Invalid password type. Must be 'main', 'investor', or 'api'")
              
          print(f"4. Attempting to change {password_type} password")
          
          # Change password
          if not connection.manager.UserPasswordChange(pass_type, login, password):
              error = MT5Manager.LastError()
              raise MT5ConnectionError(f"Failed to change password: {error}")
              
          print("5. Password changed successfully")
          print("=== End Debug ===\n")
          return True
            
      except Exception as e:
          print(f"\n=== MT5 Error Debug ===")
          print(f"Error type: {type(e).__name__}")
          print(f"Error message: {str(e)}")
          error = MT5Manager.LastError()
          print(f"MT5 Last Error: {error}")
          print("=== End Error Debug ===\n")
          if isinstance(e, ValueError):
              raise
          raise MT5ConnectionError(f"Failed to change password: {str(e)}")

  @staticmethod
  async def change_group(login: int, new_group: str, server_id=None, server_type=None):
    """
    Change a user's trading group
    
    Args:
        login: User login ID
        new_group: New trading group name
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        Updated user object
        
    Raises:
        MT5ConnectionError: If connection fails or user doesn't exist
        ValueError: If login is invalid or group doesn't exist
    """
    if not isinstance(login, int) or login <= 0:
        raise ValueError("Login must be a positive integer")
            
    if not new_group:
        raise ValueError("New group name is required")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
            
    try:
        print(f"\n=== MT5 Group Change Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        
        # Check if user exists first
        print(f"\n3. Checking if user {login} exists")
        user = connection.manager.UserRequest(login)
        if not user:
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"User {login} not found: {error}")
                
        # Validate group exists
        print(f"\n4. Validating group {new_group}")
        group = connection.manager.GroupGet(new_group)
        if not group:
            print(f"Group {new_group} not found. Available groups:")
            pos = 0
            available_groups = []
            while True:
                group = connection.manager.GroupNext(pos)
                if not group:
                    break
                available_groups.append(group.Group)
                print(f"- {group.Group}")
                pos += 1
            raise ValueError(f"Group {new_group} does not exist on the server. Available groups: {', '.join(available_groups)}")
                
        print(f"5. Changing group for user:")
        print(f"   - Login: {user.Login}")
        print(f"   - Name: {user.Name}")
        print(f"   - Current Group: {user.Group}")
        print(f"   - New Group: {new_group}")
        
        # Update group
        user.Group = new_group
        
        # Update user on server
        if not connection.manager.UserUpdate(user):
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"Failed to update user group: {error}")
                
        # Get updated user info
        updated_user = connection.manager.UserRequest(login)
        if not updated_user:
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"Failed to get updated user info: {error}")
                
        print("\n6. Group changed successfully:")
        print(f"   - Login: {updated_user.Login}")
        print(f"   - Name: {updated_user.Name}")
        print(f"   - New Group: {updated_user.Group}")
        print("=== End Debug ===\n")
        
        return updated_user
            
    except ValueError as e:
        # Re-raise ValueError exceptions directly
        raise
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        raise MT5ConnectionError(f"Failed to change group: {str(e)}")

  @staticmethod
  async def archive(login: Union[int, List[int]], server_id=None, server_type=None) -> Union[bool, Dict[int, bool]]:
    """
    Archive one or multiple users to the archive database.
    
    Args:
        login: Single user login ID or list of login IDs
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        If single login: True if archived successfully
        If multiple logins: Dictionary mapping each login to True if archived successfully, False otherwise
        
    Raises:
        ValueError: If login is invalid
        MT5ConnectionError: If connection fails or operation fails
    """
    # Convert single login to list for uniform processing
    is_single = isinstance(login, int)
    logins = [login] if is_single else login
    
    # Validate all logins
    if not all(isinstance(l, int) and l > 0 for l in logins):
        raise ValueError("All logins must be positive integers")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager or not connection.admin:
        raise MT5ConnectionError("MT5 connection or manager or admin not available")
            
    try:
        print(f"\n=== MT5 User Archive Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        print(f"3. Admin instance available: {connection.admin is not None}")
        print(f"4. Processing archive for {len(logins)} users")
        
        # Check if users exist in active database
        active_users = connection.manager.UserRequestByLogins(logins)
        if not active_users:
            raise ValueError(f"Users {logins} not found in active database")
        
        # Archive users using UserArchiveBatch
        result = connection.admin.UserArchiveBatch(logins)
        if result is None:
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"Failed to archive users: {error}")
        
        # Add a small delay to ensure MT5 has processed the archiving
        await asyncio.sleep(0.5)
        
        # Verify archiving by checking active database
        archive_results = {}
        active_users_after = connection.manager.UserRequestByLogins(logins)
        
        for login in logins:
            # User should no longer be in active database if archived successfully
            archive_results[login] = not any(u.Login == login for u in (active_users_after or []))
            print(f"   User {login} archive status: {'Success' if archive_results[login] else 'Failed'}")
        
        # Check for any failures
        failed = [l for l, success in archive_results.items() if not success]
        if failed:
            print(f"Warning: Failed to verify archiving for users: {failed}")
            if is_single:
                raise MT5ConnectionError(f"Failed to archive user {login}")
        
        print("=== End Debug ===\n")
        return archive_results[login] if is_single else archive_results
            
    except ValueError:
        # Re-raise ValueError exceptions directly
        raise
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        raise MT5ConnectionError(f"Failed to archive users: {str(e)}")

  @staticmethod
  async def delete(login: int, server_id=None, server_type=None):
    """
    Delete a user from MT5 server
    
    Args:
        login: User login ID
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        bool: True if user was deleted successfully
        
    Raises:
        MT5ConnectionError: If connection fails or user doesn't exist
        ValueError: If login is invalid
    """
    if not isinstance(login, int) or login <= 0:
        raise ValueError("Login must be a positive integer")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
            
    try:
        print(f"\n=== MT5 User Delete Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        
        # Check if user exists first
        print(f"\n3. Checking if user {login} exists")
        user = connection.manager.UserRequest(login)
        if not user:
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"User {login} not found: {error}")
                
        print(f"4. Found user:")
        print(f"   - Login: {user.Login}")
        print(f"   - Name: {user.Name}")
        print(f"   - Group: {user.Group}")
        
        print("\n5. Attempting to delete user...")
        if not connection.manager.UserDelete(login):
            error = MT5Manager.LastError()
            if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_NOTFOUND:
                raise MT5ConnectionError(
                    "User can only be deleted from the server where it was created"
                )
            raise MT5ConnectionError(f"Failed to delete user: {error}")
                
        print("6. User deleted successfully")
        print("=== End Debug ===\n")
        return True
            
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        if isinstance(e, ValueError):
            raise
        raise MT5ConnectionError(f"Failed to delete user: {str(e)}")

  @staticmethod
  async def change_status(login: int, enable: bool, server_id=None, server_type=None):
    """
    Enable or disable user's ability to connect
    
    Args:
        login: User login ID
        enable: True to enable user connection, False to disable
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        Updated user object
    """
    try:
        print(f"\n=== MT5 User Status Change Debug ===")
        print(f"1. {'Enabling' if enable else 'Disabling'} user connection for login: {login}")
        
        # Get current user and rights
        try:
            user = await MT5UserHelper.set_user_rights(
                login=login,
                rights_to_set=[MT5Manager.MTUser.EnUsersRights.USER_RIGHT_ENABLED] if enable else None,
                rights_to_remove=[MT5Manager.MTUser.EnUsersRights.USER_RIGHT_ENABLED] if not enable else None,
                server_id=server_id,
                server_type=server_type
            )
        except MT5ConnectionError as e:
            error = str(e)
            if "MT_RET_ERR_NOTFOUND" in error or "Not found" in error:
                raise MT5ConnectionError(f"User {login} not found")
            raise
        
        print(f"2. User status updated successfully")
        print(f"   - Login: {user.Login}")
        print(f"   - Name: {user.Name}")
        print(f"   - Can connect: {bool(user.Rights & MT5Manager.MTUser.EnUsersRights.USER_RIGHT_ENABLED)}")
        print("=== End Debug ===\n")
        
        return user
        
    except Exception as e:
        if isinstance(e, MT5ConnectionError):
            raise
        raise MT5ConnectionError(f"Failed to change user status: {str(e)}")
        
  @staticmethod
  async def change_trade_status(login: int, enable: bool, server_id=None, server_type=None):
    """
    Enable or disable user's ability to trade
    
    Args:
        login: User login ID
        enable: True to enable trading, False to disable
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        Updated user object
    """
    try:
        print(f"\n=== MT5 Trade Status Change Debug ===")
        print(f"1. {'Enabling' if enable else 'Disabling'} trading for login: {login}")
        
        # Note: USER_RIGHT_TRADE_DISABLED is inverse of enable parameter
        # If enable=True, we want to remove TRADE_DISABLED
        # If enable=False, we want to set TRADE_DISABLED
        user = await MT5UserHelper.set_user_rights(
            login=login,
            rights_to_set=[MT5Manager.MTUser.EnUsersRights.USER_RIGHT_TRADE_DISABLED] if not enable else None,
            rights_to_remove=[MT5Manager.MTUser.EnUsersRights.USER_RIGHT_TRADE_DISABLED] if enable else None,
            server_id=server_id,
            server_type=server_type
        )
        
        print(f"2. Trade status updated successfully")
        print(f"   - Login: {user.Login}")
        print(f"   - Name: {user.Name}")
        print(f"   - Can trade: {not bool(user.Rights & MT5Manager.MTUser.EnUsersRights.USER_RIGHT_TRADE_DISABLED)}")
        print("=== End Debug ===\n")
        
        return user
        
    except Exception as e:
        raise MT5ConnectionError(f"Failed to change trade status: {str(e)}")
        
  @staticmethod
  async def change_expert_status(login: int, enable: bool, server_id=None, server_type=None):
    """
    Enable or disable user's ability to use Expert Advisors
    
    Args:
        login: User login ID
        enable: True to enable Expert Advisors, False to disable
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        Updated user object
    """
    try:
        print(f"\n=== MT5 Expert Status Change Debug ===")
        print(f"1. {'Enabling' if enable else 'Disabling'} Expert Advisors for login: {login}")
        
        user = await MT5UserHelper.set_user_rights(
            login=login,
            rights_to_set=[MT5Manager.MTUser.EnUsersRights.USER_RIGHT_EXPERT] if enable else None,
            rights_to_remove=[MT5Manager.MTUser.EnUsersRights.USER_RIGHT_EXPERT] if not enable else None,
            server_id=server_id,
            server_type=server_type
        )
        
        print(f"2. Expert status updated successfully")
        print(f"   - Login: {user.Login}")
        print(f"   - Name: {user.Name}")
        print(f"   - Can use experts: {bool(user.Rights & MT5Manager.MTUser.EnUsersRights.USER_RIGHT_EXPERT)}")
        print("=== End Debug ===\n")
        
        return user
        
    except Exception as e:
        raise MT5ConnectionError(f"Failed to change expert status: {str(e)}")
        
  @staticmethod
  async def change_reports_status(login: int, enable: bool, server_id=None, server_type=None):
    """
    Enable or disable user's ability to receive daily reports
    
    Args:
        login: User login ID
        enable: True to enable daily reports, False to disable
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        Updated user object
    """
    try:
        print(f"\n=== MT5 Reports Status Change Debug ===")
        print(f"1. {'Enabling' if enable else 'Disabling'} daily reports for login: {login}")
        
        user = await MT5UserHelper.set_user_rights(
            login=login,
            rights_to_set=[MT5Manager.MTUser.EnUsersRights.USER_RIGHT_REPORTS] if enable else None,
            rights_to_remove=[MT5Manager.MTUser.EnUsersRights.USER_RIGHT_REPORTS] if not enable else None,
            server_id=server_id,
            server_type=server_type
        )
        
        print(f"2. Reports status updated successfully")
        print(f"   - Login: {user.Login}")
        print(f"   - Name: {user.Name}")
        print(f"   - Can receive reports: {bool(user.Rights & MT5Manager.MTUser.EnUsersRights.USER_RIGHT_REPORTS)}")
        print("=== End Debug ===\n")
        
        return user
        
    except Exception as e:
        raise MT5ConnectionError(f"Failed to change reports status: {str(e)}")

  @staticmethod
  async def get_account_details(login: Union[int, List[int]], server_id=None, server_type=None) -> Union[MT5Manager.MTUser, Dict[int, MT5Manager.MTUser]]:
    """
    Get trading account information for one or multiple users
    
    Args:
        login: Single user login ID or list of login IDs
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        If single login: Trading account object
        If multiple logins: Dictionary mapping each login to its trading account object
        
    Raises:
        ValueError: If login is invalid
        MT5ConnectionError: If connection fails or operation fails
    """
    # Validate single login first
    if login is None:
        raise ValueError("Login cannot be None")
        
    if isinstance(login, (str, bool, float)):
        raise ValueError("Login must be an integer")
        
    # Convert single login to list for uniform processing
    logins = [login] if isinstance(login, int) else login
    
    # Validate all logins are positive integers
    if not all(isinstance(l, int) and l > 0 for l in logins):
        raise ValueError("All logins must be positive integers")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
            
    try:
        print(f"\n=== MT5 Account Get Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        
        # For single login, use the original method
        if len(logins) == 1:
            print(f"\n3. Getting single account details for login: {logins[0]}")
            user = connection.manager.UserRequest(logins[0])
            if not user:
                error = MT5Manager.LastError()
                raise ValueError(f"User {logins[0]} not found: {error}")
                    
            account = connection.manager.UserAccountGet(logins[0])
            if not account:
                error = MT5Manager.LastError()
                raise ValueError(f"Failed to get account information: {error}")
                    
            print(f"4. Account information retrieved for login {logins[0]}")
            print_account_info(account)
            return account
                
        # For multiple logins, use batch request
        print(f"\n3. Getting batch account details for {len(logins)} logins:")
        for l in logins:
            print(f"   - Login: {l}")
                
        # Get users in batch
        users = connection.manager.UserRequestByLogins(logins)
        if not users:
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"Failed to get users: {error}")
                
        # Get account details for each user
        account_details = {}
        for login in logins:
            account = connection.manager.UserAccountGet(login)
            if account:
                account_details[login] = account
                print(f"\n4. Account information retrieved for login {login}")
                print_account_info(account)
            else:
                print(f"Warning: Could not get account details for login {login}")
                
        print("=== End Debug ===\n")
        return account_details if len(logins) > 1 else account_details[logins[0]]
            
    except ValueError:
        # Re-raise ValueError exceptions directly
        raise
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        raise MT5ConnectionError(f"Failed to get account information: {str(e)}")

  @staticmethod
  async def check_balance(login: int, server_id=None, server_type=None):
    """
    Check user's balance and credit funds without fixing discrepancies
    
    Args:
        login: User login ID
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        dict: Balance check results containing:
            - success: Whether check was successful
            - has_discrepancy: Whether there's a balance discrepancy
            - error: Error message if any
    """
    if not isinstance(login, int) or login <= 0:
        raise ValueError("Login must be a positive integer")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
            
    try:
        print(f"\n=== MT5 Balance Check Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        
        # Check if user exists first
        print(f"\n3. Checking if user {login} exists")
        user = connection.manager.UserRequest(login)
        if not user:
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"User {login} not found: {error}")
                
        print(f"4. Checking balance for user:")
        print(f"   - Login: {user.Login}")
        print(f"   - Name: {user.Name}")
        
        # Check balance without fixing (fixflag=0)
        result = connection.manager.UserBalanceCheck(login, 0)
        
        # Get last error to check if there's a discrepancy
        error = MT5Manager.LastError()
        has_discrepancy = error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_DATA
        
        print("\n5. Balance check results:")
        print(f"   - Check completed: {result is not False}")
        print(f"   - Has discrepancy: {has_discrepancy}")
        if has_discrepancy:
            print("   - Balance discrepancy detected!")
        print("=== End Debug ===\n")
        
        return {
            'success': result is not False,
            'has_discrepancy': has_discrepancy,
            'error': str(error) if error[1] != MT5Manager.EnMTAPIRetcode.MT_RET_OK else None
        }
            
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        if isinstance(e, ValueError):
            raise
        raise MT5ConnectionError(f"Failed to check balance: {str(e)}")
            
  @staticmethod
  async def fix_balance(login: int, server_id=None, server_type=None):
    """
    Check and fix user's balance and credit funds if discrepancies are found
    
    Args:
        login: User login ID
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        dict: Balance fix results containing:
            - success: Whether fix was successful
            - was_fixed: Whether any fixes were applied
            - error: Error message if any
    """
    if not isinstance(login, int) or login <= 0:
        raise ValueError("Login must be a positive integer")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager:
        raise MT5ConnectionError("MT5 connection or manager not available")
            
    try:
        print(f"\n=== MT5 Balance Fix Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        
        # Check if user exists first
        print(f"\n3. Checking if user {login} exists")
        user = connection.manager.UserRequest(login)
        if not user:
            error = MT5Manager.LastError()
            raise MT5ConnectionError(f"User {login} not found: {error}")
                
        print(f"4. Checking and fixing balance for user:")
        print(f"   - Login: {user.Login}")
        print(f"   - Name: {user.Name}")
        
        # First check if there's a discrepancy
        check_result = connection.manager.UserBalanceCheck(login, 0)
        error = MT5Manager.LastError()
        needs_fix = error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_ERR_DATA
        
        if needs_fix:
            print("\n5. Balance discrepancy found, attempting to fix...")
            # Fix balance (fixflag=1)
            fix_result = connection.manager.UserBalanceCheck(login, 1)
            if fix_result is False:
                error = MT5Manager.LastError()
                raise MT5ConnectionError(f"Failed to fix balance: {error}")
            print("6. Balance fixed successfully")
        else:
            print("\n5. No balance discrepancy found")
            fix_result = True
                
        print("=== End Debug ===\n")
        
        return {
            'success': True,
            'was_fixed': needs_fix,
            'error': None
        }
            
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        if isinstance(e, ValueError):
            raise
        raise MT5ConnectionError(f"Failed to fix balance: {str(e)}")

  @staticmethod
  async def restore(login: Union[int, List[int]], server_id=None, server_type=None) -> Union[MT5Manager.MTUser, Dict[int, MT5Manager.MTUser]]:
    """
    Restore one or multiple users from the archive database.
    First fetches the user data from archive, then restores them to active database.
    
    Args:
        login: Single user login ID or list of login IDs
        server_id: Optional server ID
        server_type: Optional server type ('demo' or 'live')
        
    Returns:
        If single login: Restored user object
        If multiple logins: Dictionary mapping each login to its restored user object or None if restoration failed
        
    Raises:
        ValueError: If login is invalid
        MT5UserError: For user-specific errors
        MT5ArchiveError: For archive-related errors
        MT5ConnectionError: For connection failures
    """
    # Convert single login to list for uniform processing
    is_single = isinstance(login, int)
    logins = [login] if is_single else login
    
    # Validate all logins
    if not all(isinstance(l, int) and l > 0 for l in logins):
        raise ValueError("All logins must be positive integers")
            
    connection = MT5UserHelper.get_connection(server_id, server_type)
    if not connection or not connection.manager or not connection.admin:
        raise MT5ConnectionError("MT5 connection or manager or admin not available")
            
    try:
        print(f"\n=== MT5 User Restore Debug ===")
        print(f"1. Connection state: connected={connection._connected}")
        print(f"2. Manager instance available: {connection.manager is not None}")
        print(f"3. Admin instance available: {connection.admin is not None}")
        
        if is_single:
            # Single user restore
            print(f"\n4. Processing single user restore for login: {login}")
            
            # Check if user exists in active database
            active_user = connection.manager.UserRequest(login)
            if active_user:
                raise_mt5_error("MT_RET_USR_ACCOUNT_EXIST", f"User {login} already exists in active database")
                    
            # Fetch user from archive
            archived_user = connection.admin.UserArchiveRequest(login)
            if not archived_user:
                raise MT5ArchiveError(f"User {login} not found in archive")
                    
            # Restore user
            if not connection.admin.UserRestore(archived_user):
                error = MT5Manager.LastError()
                if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_USR_LOGIN_EXIST:
                    raise_mt5_error("MT_RET_USR_LOGIN_EXIST")
                elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_USR_LOGIN_PROHIBITED:
                    raise_mt5_error("MT_RET_USR_LOGIN_PROHIBITED")
                else:
                    raise MT5ArchiveError(f"Failed to restore user: {error}")
                    
            # Verify restoration
            restored_user = connection.manager.UserRequest(login)
            if not restored_user:
                raise MT5ArchiveError(f"Failed to verify restored user")
                    
            print(f"5. User restored successfully:")
            print(f"   - Login: {restored_user.Login}")
            print(f"   - Name: {restored_user.Name}")
            print(f"   - Group: {restored_user.Group}")
            print("=== End Debug ===\n")
            return restored_user
                
        else:
            # Batch restore
            print(f"\n4. Processing batch restore for {len(logins)} users")
            
            # Check for existing users using UserRequestByLogins
            active_users = connection.manager.UserRequestByLogins(logins)
            if active_users:
                existing_logins = [user.Login for user in active_users]
                raise_mt5_error("MT_RET_USR_ACCOUNT_EXIST", f"Users {existing_logins} already exist in active database")
                    
            # Fetch archived users using UserArchiveBatch
            print(f"\n5. Fetching users from archive")
            archived_users = connection.admin.UserArchiveRequestByLogins(logins)
            if not archived_users:
                raise MT5ArchiveError(f"Users {logins} not found in archive")
                    
            # Restore users using UserRestoreBatch
            print(f"\n6. Attempting to restore users")
            try:
                result = connection.admin.UserRestoreBatch(archived_users)
                print(f"7. UserRestoreBatch result: {result}")
                if result is None:
                    error = MT5Manager.LastError()
                    if error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_USR_LOGIN_EXIST:
                        raise_mt5_error("MT_RET_USR_LOGIN_EXIST")
                    elif error[1] == MT5Manager.EnMTAPIRetcode.MT_RET_USR_LOGIN_PROHIBITED:
                        raise_mt5_error("MT_RET_USR_LOGIN_PROHIBITED")
                    else:
                        raise MT5ArchiveError(f"Failed to restore users: {error}")
            except Exception as e:
                error = MT5Manager.LastError()
                print(f"UserRestoreBatch failed with error: {error}")
                raise MT5ArchiveError(f"Failed to restore users: {error}")

            # Add a small delay to ensure MT5 has processed the restoration
            await asyncio.sleep(0.5)
                    
            # Verify restorations using UserRequestByLogins
            print("\n7. Verifying restored users")
            restore_results = {}  # Initialize empty dictionary
            
            # Try multiple times to get the restored users
            max_retries = 3
            for attempt in range(max_retries):
                restored_users = connection.manager.UserRequestByLogins(logins)
                if restored_users:
                    for user in restored_users:
                        restore_results[user.Login] = user
                        print(f"   User {user.Login} restored successfully:")
                        print(f"   - Name: {user.Name}")
                        print(f"   - Group: {user.Group}")
                    
                    # If we got all users, break out
                    if len(restore_results) == len(logins):
                        break
                        
                # If not all users found, wait and retry
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5)
                        
            # Check for any failures
            failed = [l for l in logins if l not in restore_results]
            if failed:
                print(f"Warning: Failed to verify restoration for users: {failed}")
                raise MT5ArchiveError(f"Failed to verify restoration for users: {failed}")
                    
            print("=== End Debug ===\n")
            return restore_results
                
    except ValueError:
        # Re-raise ValueError exceptions directly
        raise
    except (MT5UserError, MT5ArchiveError):
        # Re-raise specific MT5 exceptions
        raise
    except Exception as e:
        print(f"\n=== MT5 Error Debug ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        error = MT5Manager.LastError()
        print(f"MT5 Last Error: {error}")
        print("=== End Error Debug ===\n")
        raise MT5ConnectionError(f"Failed to restore users: {str(e)}")
