from typing import Callable, Dict, Any, Optional, NamedTuple
from dataclasses import dataclass
import logging
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ServerInfo:
    """Server information passed to callbacks"""
    id: int
    name: str
    type: str  # 'demo' or 'live'

class MTEvent:
    """
    Event object that encapsulates all event-related data.
    
    Attributes:
        type (str): The type of event (e.g., 'tick', 'book', 'tick_stat')
        data (tuple): Tuple containing the event data arguments
        server_info (ServerInfo): Information about the MT5 server
    """
    def __init__(self, event_type: str, data: tuple, server_info) -> None:
        """
        Initialize a new MT5 event.

        Args:
            event_type (str): The type of event
            data (tuple): Tuple containing the event data arguments
            server_info: Server information object
        """
        self.type = event_type
        self.data = data
        self.server_info = server_info

    def __str__(self) -> str:
        """Return a string representation of the event."""
        return f"MTEvent(type={self.type}, data={self.data}, server={self.server_info.name})"

class BaseMT5Sink:
    """Base class for MT5 event sinks"""
    def __init__(self, server_info: ServerInfo):
        self._callbacks: Dict[str, dict[str, Callable]] = {}
        self._server_info = server_info
    
    def set_server_info(self, server_info):
        """Set server information for this sink"""
        self._server_info = server_info
    
    def add_callback(self, event: str, callback_name: str, callback: Callable):
        """
        Add callback for specific event
        
        Args:
            event (str): Event type (e.g., 'deal_add', 'position_update')
            callback_name (str): Unique name for the callback
            callback (Callable): The callback function
        """
        if event not in self._callbacks:
            self._callbacks[event] = {}
        self._callbacks[event][callback_name] = callback
    
    def _trigger_callbacks(self, event: str, *args):
        """
        Trigger all callbacks registered for an event with a structured event object.
        
        This method creates an MTEvent object that encapsulates all event-related data
        and passes it to each callback. This provides a more structured approach to
        event handling and ensures consistent data access patterns.
        
        Args:
            event (str): Event name/type (e.g., 'tick', 'book', 'tick_stat')
            *args: Variable positional arguments containing the event data

        Example:
            For a tick event, the callback would receive:
            callback(MTEvent(
                type='tick',
                data=(symbol, tick),
                server_info=self._server_info
            ))
        """
        event_data = MTEvent(event, args, self._server_info)
        for callback in self._callbacks.get(event, {}).values():
            try:
                # Check if the callback is a coroutine function (async def)
                if asyncio.iscoroutinefunction(callback):
                    # For async callbacks, we need to run them in an event loop
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        # If no event loop exists in this thread, create one
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Schedule the coroutine to run
                    if loop.is_running():
                        # If the loop is already running, use run_coroutine_threadsafe
                        future = asyncio.run_coroutine_threadsafe(callback(event_data), loop)
                        
                        # Add a callback to handle any exceptions
                        def handle_result(future):
                            try:
                                future.result()  # This will raise any exceptions from the coroutine
                            except Exception as e:
                                logger.error(f"Error in async callback for {event}: {e}", exc_info=True)
                        
                        future.add_done_callback(handle_result)
                    else:
                        # If the loop is not running, run the coroutine directly
                        # This ensures the coroutine runs to completion
                        try:
                            loop.run_until_complete(callback(event_data))
                        except Exception as e:
                            logger.error(f"Error running async callback for {event}: {e}", exc_info=True)
                else:
                    # For regular callbacks, just call them directly
                    callback(event_data)
            except Exception as e:
                logger.error(
                    f"Error in {event} callback for server {self._server_info.name}: {str(e)}",
                    exc_info=True
                )
    
    def remove_callback(self, event_type, callback_name):
        """
        Remove a callback for a specific event type
        
        Args:
            event_type: The type of event (e.g., 'deal_add')
            callback_name: Name of the callback to remove
        """
        if event_type in self._callbacks and callback_name in self._callbacks[event_type]:
            del self._callbacks[event_type][callback_name]

class MT5UserSink(BaseMT5Sink):
    """Sink for user-related events"""
    def OnUserAdd(self, user) -> None:
        self._trigger_callbacks('user_add', user)
        
    def OnUserUpdate(self, user) -> None:
        self._trigger_callbacks('user_update', user)

    def OnUserDelete(self, user) -> None:
        self._trigger_callbacks('user_delete', user)
        
    def OnUserLogin(self, user) -> None:
        self._trigger_callbacks('user_login', user)
    
    def OnUserLogout(self, user) -> None:
        self._trigger_callbacks('user_logout', user)

    def OnUserArchive(self, user) -> None:
        self._trigger_callbacks('user_archive', user)

    def OnUserRestore(self, user) -> None:
        self._trigger_callbacks('user_restore', user)

class MT5DealSink(BaseMT5Sink):
    """Sink for deal-related events"""
    def OnDealAdd(self, deal) -> None:
        self._trigger_callbacks('deal_add', deal)
    
    def OnDealUpdate(self, deal) -> None:
        self._trigger_callbacks('deal_update', deal)
    
    def OnDealDelete(self, deal) -> None:
        self._trigger_callbacks('deal_delete', deal)

class MT5PositionSink(BaseMT5Sink):
    """Sink for position-related events"""
    def OnPositionAdd(self, position) -> None:
        self._trigger_callbacks('position_add', position)
    
    def OnPositionUpdate(self, position) -> None:
        self._trigger_callbacks('position_update', position)
    
    def OnPositionDelete(self, position) -> None:
        self._trigger_callbacks('position_delete', position)

class MT5OrderSink(BaseMT5Sink):
    """Sink for order-related events"""
    def OnOrderAdd(self, order) -> None:
        self._trigger_callbacks('order_add', order)
    
    def OnOrderUpdate(self, order) -> None:
        self._trigger_callbacks('order_update', order)
    
    def OnOrderDelete(self, order) -> None:
        self._trigger_callbacks('order_delete', order)

class MT5SummarySink(BaseMT5Sink):
    """Sink for summary-related events"""
    def OnSummaryUpdate(self, summary) -> None:
        self._trigger_callbacks('summary_update', summary)

class MT5TickSink(BaseMT5Sink):
    """Sink for tick-related events"""
    def OnTick(self, symbol, tick) -> None:
        self._trigger_callbacks('tick', symbol, tick)

    def OnTickStat(self, tick_stat) -> None:
        self._trigger_callbacks('tick_stat', tick_stat)

class MT5BookSink(BaseMT5Sink):
    """Sink for book-related events"""
    def OnBook(self, symbol, book) -> None:
        self._trigger_callbacks('book', symbol, book)

    
