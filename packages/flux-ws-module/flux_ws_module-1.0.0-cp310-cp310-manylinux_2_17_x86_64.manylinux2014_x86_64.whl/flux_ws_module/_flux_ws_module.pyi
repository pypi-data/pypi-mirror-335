
"""

        flux_ws_module
        -------------------
        A C++ library that provides WebSocket connections to different exchanges with same interface.

        This module allows connection to WebSocket servers, subscription to channels,
        placing and cancelling orders, and includes cryptographic functions for data encoding and hashing.
    
"""
from __future__ import annotations
from typing import Iterator

__all__ = ['BaseExchangeConnector', 'OkxConnector']
class BaseExchangeConnector:
    """
    
                BaseExchangeConnector
    
                A base class that provides common WebSocket connection functionality.
            
    """

class OkxConnector(BaseExchangeConnector):
    """
    
                WebSocket
    
                A specialized connector for OKX exchanges, inheriting from BaseExchangeConnector.
            
    """
    def __init__(self, arg0: str, arg1: str, arg2: str) -> None:
        """
                        Constructor for WebSocket.
        
                        Parameters:
                            param1 (str): Description for the first parameter.
                            param2 (str): Description for the second parameter.
                            param3 (str): Description for the third parameter.
        """
    def cancel_order(self, arg0: str, arg1: str, arg2: str) -> None:
        """
                        Cancel an existing order.
        
                        Returns:
                            Confirmation or status of the order cancellation.
        """
    def connect(self, url: str) -> None:
        """
                        Connect to the WebSocket server.
        
                        Parameters:
                            url (str): The URL of the WebSocket server.
        
                        Returns:
                            A status or result of the connection attempt.
        """
    def connect_private(self, arg0: str, arg1: str, arg2: str, arg3: str) -> None:
        """
                        Establish a private WebSocket connection.
        """
    def disconnect(self) -> None:
        """
                        Disconnect from the WebSocket server.
        """
    def place_order(self, arg0: str, arg1: str, arg2: str, arg3: str) -> None:
        """
                        Place an order.
        
                        Returns:
                            Confirmation or status of the order placement.
        """
    def subscribe(self, arg0: str, arg1: str) -> None:
        """
                        Subscribe to a channel and instrument.
        
                        Parameters:
                            channel (str): The channel to subscribe.
                            inst (str): The instrument identifier.
        """
    def subscribe_private(self, arg0: str) -> None:
        """
                        Subscribe to a private channel.
        
                        Parameters:
                            channel (str): The channel to subscribe.
                            inst (str): The instrument identifier.
        """
    def unsubscribe(self, arg0: str, arg1: str) -> None:
        """
                        Unsubscribe from a channel and instrument.
        
                        Parameters:
                            channel (str): The channel to unsubscribe.
                            inst (str): The instrument identifier.
        """

    def wsrun(self) -> Iterator[str]: ...