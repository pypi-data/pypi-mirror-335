from typing import TypedDict, List, Optional
import numpy as np
import requests

class AlgorithmResult(TypedDict):
    """Type definition for a single algorithm's result"""
    configuration: List[int]
    energy: float
    time: float

class SolveResult(TypedDict):
    """Type definition for the complete API response structure"""
    SimulatedBifurcation: AlgorithmResult
    TensorTrain: AlgorithmResult
    SimulatedAnnealer: AlgorithmResult

class QUBOSolver:
    def __init__(self) -> None:
        self.api_url: str = "http://localhost:3003/library/ask"
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

    def solve(self, matrix: np.ndarray) -> SolveResult:
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
            self.api_url,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        response.raise_for_status()
        return response.json() 
