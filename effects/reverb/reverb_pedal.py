"""Reverb pedal effect using multiple delay lines"""

import numpy as np
from typing import List, Tuple
from ...core.audio_effect import AudioEffect


class ReverbPedal(AudioEffect):
    """Simple reverb using multiple delay lines and all-pass filters
    
    Parameters:
        room_size: Size of the virtual room (0.0-1.0)
        damping: High frequency damping (0.0-1.0)
        mix: Dry/wet mix (0.0-1.0)
        pre_delay: Pre-delay in milliseconds (0-100ms)
    """
    
    def __init__(self, name: str = "Reverb", is_stereo: bool = False):
        super().__init__(name, is_stereo)
        
        # Delay times in samples (at 44100 Hz) for a more natural reverb
        self.delay_times = [
            int(44100 * 0.0297),  # 29.7ms
            int(44100 * 0.0371),  # 37.1ms
            int(44100 * 0.0411),  # 41.1ms
            int(44100 * 0.0437),  # 43.7ms
        ]
        
        # Initialize delay lines
        self.delays = [np.zeros(delay_time, dtype=np.float32) 
                      for delay_time in self.delay_times]
        self.positions = [0] * len(self.delays)
        
        # All-pass filter delays for diffusion
        self.allpass_delays = [
            np.zeros(int(44100 * 0.005), dtype=np.float32),
            np.zeros(int(44100 * 0.0067), dtype=np.float32),
        ]
        self.allpass_positions = [0, 0]
        self.allpass_gain = 0.5
        
        # Damping filters (one per delay line)
        self.damping_states = [0.0] * len(self.delays)
        
        self.parameters = {
            'room_size': 0.5,
            'damping': 0.3,
            'mix': 0.2,
            'pre_delay': 10.0  # ms
        }
        
        # Pre-delay buffer
        self.pre_delay_buffer = np.zeros(int(44100 * 0.1), dtype=np.float32)  # 100ms max
        self.pre_delay_pos = 0
        
    def _apply_damping(self, sample: float, damping: float, state_idx: int) -> float:
        """Apply damping (low-pass filter)"""
        filtered = sample * (1 - damping) + self.damping_states[state_idx] * damping
        self.damping_states[state_idx] = filtered
        return filtered
    
    def _process_allpass(self, sample: float, delay_idx: int) -> float:
        """Process through all-pass filter for diffusion"""
        delay_line = self.allpass_delays[delay_idx]
        pos = self.allpass_positions[delay_idx]
        
        delayed = delay_line[pos]
        output = delayed - sample * self.allpass_gain
        delay_line[pos] = sample + delayed * self.allpass_gain
        
        self.allpass_positions[delay_idx] = (pos + 1) % len(delay_line)
        return output
    
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process audio through reverb"""
        room_size = self.parameters['room_size']
        damping = self.parameters['damping']
        mix = self.parameters['mix']
        pre_delay_samples = int(sample_rate * self.parameters['pre_delay'] / 1000)
        
        output = np.zeros_like(input_buffer)
        
        for i, sample in enumerate(input_buffer):
            # Pre-delay
            pre_delay_pos = (self.pre_delay_pos - pre_delay_samples) % len(self.pre_delay_buffer)
            pre_delayed_sample = self.pre_delay_buffer[pre_delay_pos]
            self.pre_delay_buffer[self.pre_delay_pos] = sample
            self.pre_delay_pos = (self.pre_delay_pos + 1) % len(self.pre_delay_buffer)
            
            # Process through delay lines
            reverb_sum = 0.0
            
            for j, delay_line in enumerate(self.delays):
                # Read from delay line
                delayed = delay_line[self.positions[j]]
                
                # Apply damping
                damped = self._apply_damping(delayed, damping, j)
                
                # Accumulate
                reverb_sum += damped
                
                # Write to delay line with feedback
                delay_line[self.positions[j]] = pre_delayed_sample + damped * room_size * 0.5
                
                # Advance position
                self.positions[j] = (self.positions[j] + 1) % len(delay_line)
            
            # Average the delay lines
            reverb_sum /= len(self.delays)
            
            # Apply all-pass filters for diffusion
            reverb_sum = self._process_allpass(reverb_sum, 0)
            reverb_sum = self._process_allpass(reverb_sum, 1)
            
            # Mix dry and wet signals
            output[i] = sample * (1 - mix) + reverb_sum * mix
        
        return output
    
    def process_stereo(self, left_buffer: np.ndarray, right_buffer: np.ndarray,
                      sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        """Process stereo with slight variations between channels for width"""
        # Process left channel normally
        left_out = self.process(left_buffer, sample_rate)
        
        # Process right channel with slight parameter variations
        original_room_size = self.parameters['room_size']
        self.parameters['room_size'] *= 1.05  # Slightly different room size
        right_out = self.process(right_buffer, sample_rate)
        self.parameters['room_size'] = original_room_size
        
        return left_out, right_out
    
    def reset(self) -> None:
        """Clear all delay buffers"""
        for delay in self.delays:
            delay.fill(0)
        for delay in self.allpass_delays:
            delay.fill(0)
        self.pre_delay_buffer.fill(0)
        self.positions = [0] * len(self.delays)
        self.allpass_positions = [0] * len(self.allpass_delays)
        self.damping_states = [0.0] * len(self.delays)
