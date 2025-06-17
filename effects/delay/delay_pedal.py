"""Digital delay pedal effect with stereo support"""

import numpy as np
from typing import Tuple
from ...core.audio_effect import AudioEffect


class DelayPedal(AudioEffect):
    """Digital delay pedal with feedback and mix control
    
    Parameters:
        delay_time: Delay time in milliseconds (1-2000ms)
        feedback: Amount of delayed signal fed back (0.0-0.9)
        mix: Dry/wet mix (0.0-1.0)
        stereo_width: Stereo width for ping-pong delay (0.0-1.0)
    """
    
    def __init__(self, name: str = "Delay", max_delay_ms: float = 2000.0, is_stereo: bool = False):
        super().__init__(name, is_stereo)
        self.max_delay_ms = max_delay_ms
        self.max_delay_samples = int(44100 * max_delay_ms / 1000)
        
        # Initialize delay buffers
        self.delay_buffer_left = np.zeros(self.max_delay_samples, dtype=np.float32)
        self.delay_buffer_right = np.zeros(self.max_delay_samples, dtype=np.float32)
        self.write_pos = 0
        
        self.parameters = {
            'delay_time': 250.0,  # ms
            'feedback': 0.3,
            'mix': 0.3,
            'stereo_width': 0.0  # 0=mono delay, 1=full ping-pong
        }
        
        # Low-pass filter for feedback path
        self.feedback_filter_state = 0.0
        self.feedback_filter_coeff = 0.7
        
    def _apply_feedback_filter(self, sample: float) -> float:
        """Apply low-pass filter to feedback signal"""
        filtered = sample * (1 - self.feedback_filter_coeff) + \
                  self.feedback_filter_state * self.feedback_filter_coeff
        self.feedback_filter_state = filtered
        return filtered
    
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process mono audio through delay"""
        delay_samples = int(sample_rate * self.parameters['delay_time'] / 1000)
        feedback = self.parameters['feedback']
        mix = self.parameters['mix']
        
        output = np.zeros_like(input_buffer)
        
        for i, sample in enumerate(input_buffer):
            # Read delayed sample
            read_pos = (self.write_pos - delay_samples) % self.max_delay_samples
            delayed_sample = self.delay_buffer_left[read_pos]
            
            # Apply feedback filter
            filtered_feedback = self._apply_feedback_filter(delayed_sample * feedback)
            
            # Write to delay buffer with filtered feedback
            self.delay_buffer_left[self.write_pos] = sample + filtered_feedback
            
            # Mix dry and wet signals
            output[i] = sample * (1 - mix) + delayed_sample * mix
            
            # Advance write position
            self.write_pos = (self.write_pos + 1) % self.max_delay_samples
        
        return output
    
    def process_stereo(self, left_buffer: np.ndarray, right_buffer: np.ndarray, 
                      sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        """Process stereo audio with optional ping-pong delay"""
        delay_samples = int(sample_rate * self.parameters['delay_time'] / 1000)
        feedback = self.parameters['feedback']
        mix = self.parameters['mix']
        stereo_width = self.parameters['stereo_width']
        
        output_left = np.zeros_like(left_buffer)
        output_right = np.zeros_like(right_buffer)
        
        for i in range(len(left_buffer)):
            # Read delayed samples
            read_pos = (self.write_pos - delay_samples) % self.max_delay_samples
            delayed_left = self.delay_buffer_left[read_pos]
            delayed_right = self.delay_buffer_right[read_pos]
            
            # Cross-feedback for ping-pong effect
            if stereo_width > 0:
                feedback_left = delayed_left * (1 - stereo_width) + delayed_right * stereo_width
                feedback_right = delayed_right * (1 - stereo_width) + delayed_left * stereo_width
            else:
                feedback_left = delayed_left
                feedback_right = delayed_right
            
            # Write to delay buffers with feedback
            self.delay_buffer_left[self.write_pos] = left_buffer[i] + feedback_left * feedback
            self.delay_buffer_right[self.write_pos] = right_buffer[i] + feedback_right * feedback
            
            # Mix dry and wet signals
            output_left[i] = left_buffer[i] * (1 - mix) + delayed_left * mix
            output_right[i] = right_buffer[i] * (1 - mix) + delayed_right * mix
            
            # Advance write position
            self.write_pos = (self.write_pos + 1) % self.max_delay_samples
        
        return output_left, output_right
    
    def reset(self) -> None:
        """Clear delay buffers"""
        self.delay_buffer_left.fill(0)
        self.delay_buffer_right.fill(0)
        self.write_pos = 0
        self.feedback_filter_state = 0.0
