#!/usr/bin/env python3
"""
Enhanced Mesh Client with automatic token refresh capability.

This module provides an enhanced version of the MeshClient that automatically
refreshes expired access tokens and handles token persistence.
"""

import os
import time
import json
import logging
import threading
from typing import Dict, Any, Optional, List, Union

# Import from the Mesh SDK
from .client import MeshClient
from .auth import authenticate, refresh_auth_token
from .token_manager import get_token, store_token, is_token_valid
from .config import get_config, is_auto_refresh_enabled

class AutoRefreshMeshClient:
    """
    Enhanced Mesh Client with automatic token refresh capability.
    
    This client wraps the standard MeshClient and adds:
    1. Automatic token refresh when tokens expire
    2. Token persistence between sessions
    3. Background refresh thread to keep tokens valid
    
    Note: For automatic refresh to work properly, the Auth0 application must be
    configured correctly:
    - Refresh Token grant type must be enabled in the application settings
    - "Allow Offline Access" must be enabled on the API
    - The offline_access scope must be requested during authentication
    """
    
    def __init__(self, auto_refresh: bool = True, auth_on_init: bool = True):
        """
        Initialize the AutoRefreshMeshClient.
        
        Args:
            auto_refresh: Whether to automatically refresh tokens in background
            auth_on_init: Whether to authenticate on initialization if needed
        """
        # Configure logging
        self.logger = logging.getLogger("AutoRefreshMeshClient")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Override auto_refresh setting from config if needed
        self.auto_refresh = auto_refresh
        if not self.auto_refresh and is_auto_refresh_enabled():
            self.logger.info("Auto-refresh enabled in config, overriding constructor setting")
            self.auto_refresh = True
        
        # Initialize properties
        self.client = None
        self.token_data = None
        self.refresh_thread = None
        self.refresh_thread_stop = threading.Event()
        
        # Load existing token or authenticate
        if auth_on_init:
            self.authenticate()
        
        # Start background refresh if enabled
        if auto_refresh and self.has_refresh_token():
            self.start_background_refresh()
    
    def authenticate(self) -> bool:
        """
        Authenticate the client using the backend-managed authentication flow.
        
        This method follows the recommended authentication approach:
        1. Check for a valid token in secure storage
        2. If token exists but is expired, try to refresh it via the backend
        3. If no valid token exists or refresh fails, create a client that will
           automatically trigger browser-based authentication when needed
        
        Returns:
            bool: True if authentication was successful or client created successfully
        """
        # Try to get stored token
        self.token_data = get_token()
        
        # Check if token is still valid
        if is_token_valid(self.token_data):
            self.logger.info("Using existing valid token")
            self.create_client()
            return True
        
        # Token invalid or missing, try refreshing or let MeshClient handle auth
        self.logger.info("No valid token found, checking for refresh...")
        
        try:
            # Try to refresh the token if we have a refresh token
            if self.token_data and "refresh_token" in self.token_data:
                self.logger.info("Attempting to refresh token")
                refreshed_token = refresh_auth_token(refresh_token=self.token_data.get("refresh_token"))
                if refreshed_token:
                    self.token_data = refreshed_token
                    self.create_client()
                    self.logger.info("Token refreshed successfully")
                    return True
            
            # Try browser-based authentication
            self.logger.info("Attempting browser-based authentication")
            token_data = authenticate()
            if token_data:
                self.token_data = token_data
                self.create_client()
                self.logger.info("Authentication successful")
                return True
            
            # Create a client that will handle authentication when needed
            self.logger.info("Creating client with on-demand authentication")
            self.client = MeshClient()  # Will use backend-managed auth when needed
            return True
        except Exception as e:
            self.logger.error(f"Error during authentication setup: {str(e)}")
            return False
    
    def create_client(self) -> None:
        """
        Create a MeshClient with the current token.
        """
        if self.token_data and "access_token" in self.token_data:
            # Create a new MeshClient with the access token
            self.client = MeshClient(auth_token=self.token_data["access_token"])
            self.logger.debug("Created new MeshClient instance")
        else:
            # Create a client that will authenticate when needed
            self.logger.info("Creating client with on-demand authentication")
            self.client = MeshClient()  # Will use backend-managed auth when needed
    
    def refresh_token(self) -> bool:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            bool: True if token was refreshed successfully
        """
        if not self.has_refresh_token():
            self.logger.warning("No refresh token available - automatic refresh disabled")
            return False
        
        try:
            refresh_token = self.token_data.get("refresh_token")
            
            # Use the SDK's refresh_auth_token function
            self.logger.info("Refreshing token using refresh_token grant...")
            
            # This uses our backend-driven approach internally
            new_token_data = refresh_auth_token(refresh_token=refresh_token)
            
            if new_token_data:
                self.token_data = new_token_data
                self.create_client()
                self.logger.info("Token refreshed successfully")
                return True
            else:
                self.logger.error("Token refresh failed using refresh token")
                
                # Fall back to re-authentication
                self.logger.warning("Falling back to re-authentication...")
                
                # Re-authenticate using our approach
                new_token_data = authenticate()
                
                if new_token_data:
                    self.token_data = new_token_data
                    store_token(self.token_data)
                    self.create_client()
                    self.logger.info("Token refreshed through re-authentication")
                    return True
                else:
                    self.logger.error("Re-authentication failed")
                    return False
        except Exception as e:
            self.logger.error(f"Error during token refresh: {str(e)}")
            return False
    
    def start_background_refresh(self) -> None:
        """Start background thread to refresh token periodically"""
        if self.refresh_thread and self.refresh_thread.is_alive():
            self.logger.debug("Background refresh thread already running")
            return
        
        self.logger.info("Starting background token refresh thread")
        self.refresh_thread_stop.clear()
        self.refresh_thread = threading.Thread(target=self._refresh_worker)
        self.refresh_thread.daemon = True
        self.refresh_thread.start()
    
    def stop_background_refresh(self) -> None:
        """Stop the background refresh thread"""
        if self.refresh_thread and self.refresh_thread.is_alive():
            self.logger.info("Stopping background token refresh thread")
            self.refresh_thread_stop.set()
            self.refresh_thread.join(timeout=2.0)
            self.refresh_thread = None
    
    def _refresh_worker(self):
        """Worker function for the background refresh thread"""
        while not self.refresh_thread_stop.is_set():
            # Check if token needs refresh (refresh when 80% of lifetime has passed)
            if self.token_data and "expires_at" in self.token_data:
                expires_at = self.token_data["expires_at"]
                now = time.time()
                
                # Calculate time until expiration
                time_until_expiry = expires_at - now
                if time_until_expiry <= 0:
                    # Token already expired, refresh now
                    self.refresh_token()
                elif time_until_expiry < (self.token_data.get("expires_in", 3600) * 0.2):
                    # Less than 20% of lifetime left, refresh now
                    self.refresh_token()
            
            # Sleep for a while before checking again
            # Use wait with timeout to allow for clean shutdown
            self.refresh_thread_stop.wait(60)  # Check every minute
    
    def has_refresh_token(self) -> bool:
        """Check if a refresh token is available"""
        return (
            self.token_data is not None and 
            "refresh_token" in self.token_data and 
            self.token_data["refresh_token"] is not None
        )
    
    def is_authenticated(self) -> bool:
        """Check if the client is authenticated with a valid token"""
        return (
            self.client is not None and
            self.token_data is not None and
            "access_token" in self.token_data and
            is_token_valid(self.token_data)
        )
    
    def __getattr__(self, name):
        """
        Proxy attribute access to the underlying MeshClient.
        
        This allows calling MeshClient methods directly on this wrapper.
        It also checks token validity before making calls.
        """
        if self.client is None:
            raise AttributeError("Client not initialized. Call authenticate() first.")
        
        # Get the attribute from the client
        attr = getattr(self.client, name)
        
        # If it's a callable, wrap it to check token validity
        if callable(attr):
            def wrapped_method(*args, **kwargs):
                # Check token validity before call
                if not is_token_valid(self.token_data):
                    # Token expired, try to refresh
                    if self.auto_refresh:
                        self.logger.info("Token expired, refreshing...")
                        if not self.refresh_token():
                            # Refresh failed, re-authenticate
                            self.logger.info("Refresh failed, re-authenticating...")
                            if not self.authenticate():
                                raise Exception("Authentication failed")
                    else:
                        raise Exception("Token expired and auto-refresh is disabled")
                
                # Call the method on the client
                return attr(*args, **kwargs)
            
            return wrapped_method
        else:
            # Not a callable, just return the attribute
            return attr