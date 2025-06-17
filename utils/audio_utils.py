"""Audio utility functions"""

import numpy as np
from typing import Union


def db_to_linear(db_value: float) -> float:
    """Convert decibels to linear amplitude
    
    Args:
        db_value: Value in decibels
        
    Returns:
        Linear amplitude value
    """
    return 10.0 ** (db_value / 20.0)


def linear_to_db(linear_value: float, min_db: float = -60.0) -> float:
    """Convert linear amplitude to decibels
    
    Args:
        linear_value: Linear amplitude value
        min_db: Minimum dB value to return for very small inputs
        
    Returns:
        Value in decibels
    """
    if linear_value <= 0:
        return min_db
    db = 20.0 * np.log10(linear_value)
    return max(db, min_db)


def normalize_audio(audio: np.ndarray, target_db: float = -3.0) -> np.ndarray:
    """Normalize audio to a target peak level
    
    Args:
        audio: Audio array
        target_db: Target peak level in decibels
        
    Returns:
        Normalized audio array
    """
    peak = np.max(np.abs(audio))
    if peak == 0:
        return audio
    
    target_linear = db_to_linear(target_db)
    gain = target_linear / peak
    
    return audio * gain


def soft_clip(audio: np.ndarray, threshold: float = 0.9) -> np.ndarray:
    """Apply soft clipping to prevent harsh distortion
    
    Args:
        audio: Audio array
        threshold: Clipping threshold (0-1)
        
    Returns:
        Soft-clipped audio
    """
    # Apply different processing for values above threshold
    mask = np.abs(audio) > threshold
    
    # Soft clip using tanh for smooth saturation
    clipped = audio.copy()
    clipped[mask] = threshold * np.tanh(audio[mask] / threshold)
    
    return clipped


def crossfade(audio1: np.ndarray, audio2: np.ndarray, 
              fade_samples: int, fade_type: str = 'linear') -> np.ndarray:
    """Crossfade between two audio arrays
    
    Args:
        audio1: First audio array (fading out)
        audio2: Second audio array (fading in)
        fade_samples: Number of samples for the crossfade
        fade_type: Type of fade curve ('linear', 'exponential', 'equal_power')
        
    Returns:
        Crossfaded audio
    """
    if len(audio1) < fade_samples or len(audio2) < fade_samples:
        raise ValueError("Audio arrays must be at least as long as fade_samples")
    
    # Create fade curves
    if fade_type == 'linear':
        fade_out = np.linspace(1, 0, fade_samples)
        fade_in = np.linspace(0, 1, fade_samples)
    elif fade_type == 'exponential':
        fade_out = np.exp(np.linspace(0, -5, fade_samples))
        fade_in = 1 - np.exp(np.linspace(-5, 0, fade_samples))
    elif fade_type == 'equal_power':
        fade_out = np.cos(np.linspace(0, np.pi/2, fade_samples))
        fade_in = np.sin(np.linspace(0, np.pi/2, fade_samples))
    else:
        raise ValueError(f"Unknown fade type: {fade_type}")
    
    # Apply crossfade
    result = np.zeros(max(len(audio1), len(audio2)))
    
    # Copy non-fading parts
    if len(audio1) > fade_samples:
        result[:len(audio1)-fade_samples] = audio1[:-fade_samples]
    if len(audio2) > fade_samples:
        result[-len(audio2)+fade_samples:] = audio2[fade_samples:]
    
    # Apply crossfade
    fade_start = len(audio1) - fade_samples
    result[fade_start:fade_start+fade_samples] = (
        audio1[-fade_samples:] * fade_out + audio2[:fade_samples] * fade_in
    )
    
    return result
