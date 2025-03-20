from typing import Optional
import numpy as np
import requests

class QDeepHybridSolver:
    __API_URL: str = "https://api.qdeep.net/library/ask"
    
    def __init__(self) -> None:
        self._token: Optional[str] = None

    @property
    def token(self) -> Optional[str]:
        """Get the current authentication token"""
        return self._token

    @token.setter
    def token(self, value: str) -> None:
        """Set the authentication token with validation"""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Token must be a non-empty string")
        self._token = value

    def solve(self, matrix: np.ndarray):
        """
        Solve QUBO matrix and return typed results
        
        Returns:
            SolveResult: Dictionary with typed results from all algorithms
        """
        if not self.token:
            raise ValueError("Authentication token required. Set using .token = 'your_token'")

        # Matrix validation
        if not isinstance(matrix, np.ndarray):
            raise TypeError("Input must be a numpy array")
        if matrix.ndim != 2:
            raise ValueError("Matrix must be 2-dimensional")
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Matrix must be square")

        # Prepare and send request
        payload = {
            "question": matrix.tolist(),
            "token": self.token
        }

        response = requests.post(
            self.__API_URL,  # Using the private constant
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        response.raise_for_status()
        return response.json()