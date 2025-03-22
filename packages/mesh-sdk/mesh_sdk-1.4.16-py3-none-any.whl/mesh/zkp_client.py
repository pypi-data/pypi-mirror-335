"""
Mesh ZKP Client

This module provides a specialized client for interacting with the
Zero-Knowledge Proof (ZKP) functionality of the Mesh API.
"""

import hashlib
import json
import logging
import requests
from typing import Dict, Any, Optional

from .client import MeshClient
from .config import get_config

# Set up logging
logger = logging.getLogger("mesh_zkp")

class MeshZKPClient(MeshClient):
    """
    Specialized client for the Mesh API's Zero-Knowledge Proof (ZKP) functionality.
    
    This client extends the base MeshClient to provide specialized methods for:
    1. Storing keys with ZKP
    2. Getting commitments
    3. Getting challenges
    4. Verifying proofs
    
    The ZKP functionality allows secure verification of key ownership without
    revealing the actual key content.
    """
    
    def __init__(self, zkp_server_url=None, **kwargs):
        """
        Initialize the Mesh ZKP client.
        
        Args:
            zkp_server_url: URL of the ZKP microservice (defaults to API URL)
            **kwargs: Additional arguments to pass to MeshClient constructor
        """
        super().__init__(**kwargs)
        
        # Set the ZKP server URL (default to same as API URL)
        self.zkp_server_url = zkp_server_url or self.api_url
        
        # Store the last nullifier and commitment for testing
        self.last_nullifier = None
        self.last_commitment = None
    
    def _get_zkp_url(self, endpoint: str) -> str:
        """
        Get the full URL for a ZKP endpoint
        
        Args:
            endpoint: The endpoint path (e.g., '/v1/storeKeyZKP')
            
        Returns:
            str: The full URL
        """
        # Ensure endpoint starts with a slash
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        # Handle endpoint normalization
        if endpoint.startswith('/v1/mesh/'):
            # Keep legacy endpoint as-is
            pass
        
        return f"{self.zkp_server_url}{endpoint}"
    
    def _generate_nullifier(self, key_name: str, key_value: str) -> str:
        """
        Generate a nullifier based on the key name and value
        
        Args:
            key_name: Key name
            key_value: Key value
            
        Returns:
            str: Nullifier hash
        """
        # Combine key name and value to create nullifier
        combined = f"{key_name}:{key_value}"
        nullifier = hashlib.sha256(combined.encode()).hexdigest()
        self.last_nullifier = nullifier  # Store for testing
        return nullifier
    
    def _generate_commitment(self, key_value: str, nullifier: str) -> str:
        """
        Generate a commitment for a key value
        
        Args:
            key_value: The secret key value
            nullifier: A nullifier to prevent replay attacks
            
        Returns:
            str: A commitment hash
        """
        # Combine the key and nullifier to create a commitment
        combined = f"{key_value}:{nullifier}"
        commitment = hashlib.sha256(combined.encode()).hexdigest()
        self.last_commitment = commitment  # Store for testing
        return commitment
    
    def _generate_proof(self, nullifier: str, challenge: str, commitment: str) -> str:
        """
        Generate a proof from nullifier, challenge, and commitment
        
        This MUST match the server's proof generation algorithm.
        The server's calculateProof function concatenates the strings and hashes them using SHA-256.
        
        Args:
            nullifier: The nullifier value
            challenge: The challenge from the server
            commitment: The commitment value
            
        Returns:
            str: The generated proof as a hex string
        """
        # Debug output
        logger.debug("Client-side proof calculation:")
        logger.debug(f"Nullifier: {nullifier}")
        logger.debug(f"Challenge: {challenge}")
        logger.debug(f"Commitment: {commitment}")
        
        # Concatenate data and generate proof
        # IMPORTANT: This must match the server's algorithm exactly
        # Server does: nullifier + challenge + commitment (direct string concatenation)
        data = nullifier + challenge + commitment
        logger.debug(f"Concatenated data: {data}")
        
        # Create SHA-256 hash
        # In Node.js, crypto.createHash('sha256').update(data) automatically converts strings to UTF-8
        # We'll do the same with encode() in Python
        proof = hashlib.sha256(data.encode('utf-8')).hexdigest()
        
        return proof
    
    def store_key_zkp(self, key_name: str, key_value: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Store a key using Zero-Knowledge Proofs
        
        This method:
        1. Generates a nullifier based on key name and value
        2. Generates a commitment based on key value and nullifier
        3. Stores the commitment on the server
        
        Args:
            key_name: Name of the key
            key_value: Value of the key
            user_id: Optional User ID to associate with the key
            
        Returns:
            dict: Result of the operation
        """
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            return {
                "success": False,
                "error": "Authentication failed"
            }
        
        # Get user profile to extract user ID if not provided
        if not user_id:
            if not self._user_profile:
                self._ensure_user_registered()
            
            if self._user_profile and 'id' in self._user_profile:
                user_id = self._user_profile.get('id')
                logger.info(f"Using user ID from profile: {user_id}")
            else:
                return {
                    "success": False,
                    "error": "User ID not provided and could not be extracted from authentication token"
                }
        
        # Create the storage path: {userId}_{key_name}
        storage_path = f"{user_id}_{key_name}"
        
        # Generate nullifier and commitment
        nullifier = self._generate_nullifier(storage_path, key_value)
        commitment = self._generate_commitment(key_value, nullifier)
        
        # Make the request to store the commitment
        url = self._get_zkp_url("/api/v1/storeKeyZKP")
        headers = self._get_headers()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json={
                    "userId": user_id,
                    "keyName": storage_path,
                    "commitment": commitment
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                # Add our parameters to the response for verification
                result.update({
                    "storagePath": storage_path,
                    "originalKeyName": key_name,
                    "nullifier": nullifier,
                    "commitment": commitment
                })
                return result
            else:
                return {
                    "success": False,
                    "error": f"Failed to store key: {response.status_code}",
                    "details": response.text
                }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
    
    def get_commitment(self, key_name: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a commitment for a key
        
        Args:
            key_name: Name of the key
            user_id: Optional User ID associated with the key
            
        Returns:
            dict: The commitment data
        """
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            return {
                "success": False,
                "error": "Authentication failed"
            }
        
        # Get user profile to extract user ID if not provided
        if not user_id:
            if not self._user_profile:
                self._ensure_user_registered()
            
            if self._user_profile and 'id' in self._user_profile:
                user_id = self._user_profile.get('id')
                logger.info(f"Using user ID from profile: {user_id}")
            else:
                return {
                    "success": False,
                    "error": "User ID not provided and could not be extracted from authentication token"
                }
        
        # Create the storage path: {userId}_{key_name}
        storage_path = f"{user_id}_{key_name}"
        
        # Make the request
        url = self._get_zkp_url("/api/v1/getCommitment")
        headers = self._get_headers()
        
        try:
            response = requests.get(
                url,
                headers=headers,
                params={
                    "userId": user_id,
                    "keyName": storage_path
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                # Add our parameters to the response for verification
                result.update({
                    "storagePath": storage_path,
                    "originalKeyName": key_name
                })
                return result
            else:
                return {
                    "success": False,
                    "error": f"Failed to get commitment: {response.status_code}",
                    "details": response.text
                }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
    
    def get_challenge(self, user_id: str, key_name: str) -> Dict[str, Any]:
        """
        Get a challenge from the server for key verification
        
        Args:
            user_id: User ID associated with the key
            key_name: Name of the key
            
        Returns:
            dict: The challenge response
        """
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            return {
                "success": False,
                "error": "Authentication failed"
            }
        
        # Create the storage path: {userId}_{key_name}
        storage_path = f"{user_id}_{key_name}"
        
        # Make the request
        url = self._get_zkp_url("/api/v1/getChallenge")
        headers = self._get_headers()
        
        try:
            response = requests.get(
                url,
                headers=headers,
                params={
                    "userId": user_id,
                    "keyName": storage_path
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                # Add our parameters to the response for verification
                result.update({
                    "storagePath": storage_path,
                    "originalKeyName": key_name
                })
                return result
            else:
                return {
                    "success": False,
                    "error": f"Failed to get challenge: {response.status_code}",
                    "details": response.text
                }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }
    
    def verify_key(self, key_name: str, key_value: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify a key using Zero-Knowledge Proofs
        
        This method:
        1. Gets a challenge from the server
        2. Generates a nullifier and commitment
        3. Generates a proof using the challenge, nullifier, and commitment
        4. Submits the proof to the server for verification
        
        Args:
            key_name: Name of the key
            key_value: Value of the key to verify
            user_id: Optional User ID associated with the key
            
        Returns:
            dict: Verification result
        """
        # Ensure we're authenticated
        if not self._ensure_authenticated():
            return {
                "success": False,
                "error": "Authentication failed"
            }
        
        # Get user profile to extract user ID if not provided
        if not user_id:
            if not self._user_profile:
                self._ensure_user_registered()
            
            if self._user_profile and 'id' in self._user_profile:
                user_id = self._user_profile.get('id')
                logger.info(f"Using user ID from profile: {user_id}")
            else:
                return {
                    "success": False,
                    "error": "User ID not provided and could not be extracted from authentication token"
                }
        
        # Create the storage path: {userId}_{key_name}
        storage_path = f"{user_id}_{key_name}"
        
        # Generate the nullifier
        nullifier = self._generate_nullifier(storage_path, key_value)
        
        # Get a challenge from the server
        challenge_result = self.get_challenge(user_id, storage_path)
        if not challenge_result.get("success", False):
            return challenge_result
        
        challenge = challenge_result.get("challenge")
        if not challenge:
            return {
                "success": False,
                "error": "No challenge received from server"
            }
        
        # Get the commitment
        commitment_result = self.get_commitment(key_name, user_id)
        if not commitment_result.get("success", False):
            return commitment_result
        
        commitment = commitment_result.get("commitment")
        if not commitment:
            return {
                "success": False,
                "error": "No commitment found for key"
            }
        
        # Generate the proof
        proof = self._generate_proof(nullifier, challenge, commitment)
        
        # Submit the proof for verification
        url = self._get_zkp_url("/api/v1/verifyProof")
        headers = self._get_headers()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json={
                    "userId": user_id,
                    "keyName": storage_path,
                    "proof": proof,
                    "challenge": challenge
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                # Add our parameters to the response for verification
                result.update({
                    "storagePath": storage_path,
                    "originalKeyName": key_name,
                    "nullifier": nullifier,
                    "commitment": commitment,
                    "proof": proof
                })
                return result
            else:
                return {
                    "success": False,
                    "error": f"Failed to verify proof: {response.status_code}",
                    "details": response.text
                }
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Request failed: {str(e)}"
            }