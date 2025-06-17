"""Distortion/Overdrive pedal effect"""

import numpy as np
from typing import Literal
from ...core.audio_effect import AudioEffect


class DistortionPedal(AudioEffect):
    """Simple distortion/overdrive pedal with multiple clipping modes
    
    Parameters:
        drive: Amount of gain/distortion (1.0 - 10.0)
        level: Output level (0.0 - 1.0)
        tone: Tone control (0.0 - 1.0)
        mode: Clipping mode ('soft', 'hard', 'tube')
    """
    
    def __init__(self, name: str = "Distortion"):
        super().__init__(name)
        self.parameters = {
            'drive': 2.0,
            'level': 0.5,
            'tone': 0.5,
            'mode': 0  # 0=soft, 1=hard, 2=tube
        }
        
        # Pre-compute tone filter coefficients
        self._update_tone_filter()
        
    def _update_tone_filter(self):
        """Update tone filter coefficients based on tone parameter"""
        # Simple one-pole low-pass filter for tone control
        tone = self.parameters['tone']
        self.tone_coeff = tone * 0.9  # More tone = more high frequencies
        
    def _soft_clip(self, signal: np.ndarray) -> np.ndarray:
        """Soft clipping using tanh"""
        return np.tanh(signal)
    
    def _hard_clip(self, signal: np.ndarray) -> np.ndarray:
        """Hard clipping"""
        return np.clip(signal, -0.7, 0.7) / 0.7
    
    def _tube_clip(self, signal: np.ndarray) -> np.ndarray:
        """Tube-like asymmetric clipping"""
        positive = signal > 0
        negative = ~positive
        
        # Asymmetric clipping
        output = np.zeros_like(signal)
        output[positive] = np.tanh(signal[positive] * 0.7)
        output[negative] = np.tanh(signal[negative] * 1.2) * 0.8
        
        return output
    
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process audio through distortion effect"""
        drive = self.parameters['drive']
        level = self.parameters['level']
        mode = int(self.parameters['mode'])
        
        # Apply drive/gain
        driven = input_buffer * drive
        
        # Apply clipping based on mode
        if mode == 0:
            clipped = self._soft_clip(driven)
        elif mode == 1:
            clipped = self._hard_clip(driven)
        else:
            clipped = self._tube_clip(driven)
        
        # Simple tone control (low-pass filter)
        output = np.zeros_like(clipped)
        output[0] = clipped[0]
        for i in range(1, len(clipped)):
            output[i] = clipped[i] * (1 - self.tone_coeff) + output[i-1] * self.tone_coeff
        
        # Apply output level
        return output * level
    
    def set_parameter(self, param_name: str, value: float) -> None:
        """Set parameter and update internal state if needed"""
        super().set_parameter(param_name, value)
        if param_name == 'tone':
            self._update_tone_filter()
