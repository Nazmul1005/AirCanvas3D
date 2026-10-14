"""
One Euro filter and exponential moving average for smoothing landmark positions.

The One Euro filter adapts its cutoff frequency based on signal velocity,
providing smooth tracking with low lag.
"""

import math
from typing import Optional


class OneEuroFilter:
    """
    One Euro filter for smoothing noisy signals with adaptive cutoff.
    
    Reference: http://cristal.univ-lille.fr/~casiez/1euro/
    """
    
    def __init__(
        self,
        min_cutoff: float = 1.0,
        beta: float = 0.007,
        derivate_cutoff: float = 1.0
    ):
        """
        Initialize the One Euro filter.
        
        Args:
            min_cutoff: Minimum cutoff frequency (lower = smoother, more lag)
            beta: Speed coefficient (higher = reacts faster to velocity)
            derivate_cutoff: Cutoff frequency for derivative
        """
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.derivate_cutoff = derivate_cutoff
        
        self.x_prev: Optional[float] = None
        self.dx_prev: float = 0.0
        self.t_prev: Optional[float] = None
    
    def __call__(self, x: float, t: float) -> float:
        """
        Filter a single value.
        
        Args:
            x: Current value
            t: Current timestamp (seconds)
        
        Returns:
            Filtered value
        """
        if self.x_prev is None:
            self.x_prev = x
            self.t_prev = t
            return x
        
        # Time delta
        dt = t - self.t_prev
        if dt <= 0:
            dt = 1e-6  # Prevent division by zero
        
        # Estimate velocity
        dx = (x - self.x_prev) / dt
        
        # Smooth the derivative
        dx_hat = self._lowpass(dx, self.dx_prev, self._alpha(dt, self.derivate_cutoff))
        
        # Adaptive cutoff frequency
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        
        # Filter the signal
        x_hat = self._lowpass(x, self.x_prev, self._alpha(dt, cutoff))
        
        # Update state
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        
        return x_hat
    
    @staticmethod
    def _alpha(dt: float, cutoff: float) -> float:
        """Calculate smoothing factor from cutoff frequency."""
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)
    
    @staticmethod
    def _lowpass(x: float, x_prev: float, alpha: float) -> float:
        """Simple low-pass filter."""
        return alpha * x + (1.0 - alpha) * x_prev
    
    def reset(self) -> None:
        """Reset filter state."""
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None


class LandmarkFilter:
    """Filter for 2D or 3D landmark coordinates using One Euro filters per axis."""
    
    def __init__(self, dimensions: int = 3, **filter_params):
        """
        Initialize filters for each dimension.
        
        Args:
            dimensions: Number of dimensions (2 for x,y or 3 for x,y,z)
            **filter_params: Parameters passed to OneEuroFilter
        """
        self.filters = [OneEuroFilter(**filter_params) for _ in range(dimensions)]
        self.dimensions = dimensions
    
    def __call__(self, coords: tuple, t: float) -> tuple:
        """
        Filter coordinates.
        
        Args:
            coords: Tuple of (x, y) or (x, y, z)
            t: Current timestamp
        
        Returns:
            Filtered coordinates tuple
        """
        if len(coords) != self.dimensions:
            raise ValueError(f"Expected {self.dimensions} coordinates, got {len(coords)}")
        
        return tuple(f(c, t) for f, c in zip(self.filters, coords))
    
    def reset(self) -> None:
        """Reset all filters."""
        for f in self.filters:
            f.reset()


class EMAFilter:
    """Simple exponential moving average filter as a lightweight alternative."""
    
    def __init__(self, alpha: float = 0.3):
        """
        Initialize EMA filter.
        
        Args:
            alpha: Smoothing factor (0 to 1, higher = less smoothing)
        """
        self.alpha = alpha
        self.value: Optional[float] = None
    
    def __call__(self, x: float) -> float:
        """Filter a value."""
        if self.value is None:
            self.value = x
            return x
        
        self.value = self.alpha * x + (1.0 - self.alpha) * self.value
        return self.value
    
    def reset(self) -> None:
        """Reset filter state."""
        self.value = None
