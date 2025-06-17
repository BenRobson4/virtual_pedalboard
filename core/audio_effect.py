"""Base class for all audio effects/pedals"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Union, Tuple


class AudioEffect(ABC):
    """Base class for all audio effects/pedals
    
    Attributes:
        name (str): Effect name
        enabled (bool): Whether the effect is enabled
        parameters (Dict[str, float]): Effect parameters
        is_stereo (bool): Whether the effect processes stereo audio
    """
    
    def __init__(self, name: str, is_stereo: bool = False):
        self.name = name
        self.enabled = True
        self.parameters: Dict[str, float] = {}
        self.is_stereo = is_stereo
    
    @abstractmethod
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process audio buffer and return processed audio
        
        Args:
            input_buffer: Audio input buffer (mono or stereo)
            sample_rate: Sample rate in Hz
            
        Returns:
            Processed audio buffer (same shape as input)
        """
        pass
    
    def process_stereo(self, left_buffer: np.ndarray, right_buffer: np.ndarray, 
                      sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        """Process stereo audio buffers
        
        Default implementation processes each channel independently.
        Override this method for true stereo processing.
        
        Args:
            left_buffer: Left channel audio buffer
            right_buffer: Right channel audio buffer
            sample_rate: Sample rate in Hz
            
        Returns:
            Tuple of (processed_left, processed_right) buffers
        """
        processed_left = self.process(left_buffer, sample_rate)
        processed_right = self.process(right_buffer, sample_rate)
        return processed_left, processed_right
    
    def set_parameter(self, param_name: str, value: float) -> None:
        """Set effect parameter
        
        Args:
            param_name: Parameter name
            value: Parameter value
        """
        if param_name in self.parameters:
            self.parameters[param_name] = value
        else:
            raise ValueError(f"Unknown parameter: {param_name}")
    
    def get_parameter(self, param_name: str) -> float:
        """Get effect parameter value
        
        Args:
            param_name: Parameter name
            
        Returns:
            Parameter value
        """
        if param_name in self.parameters:
            return self.parameters[param_name]
        else:
            raise ValueError(f"Unknown parameter: {param_name}")
    
    def toggle(self) -> None:
        """Enable/disable effect"""
        self.enabled = not self.enabled
    
    def reset(self) -> None:
        """Reset effect state. Override in subclasses if needed."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', enabled={self.enabled})"
