# pedals.py
import numpy as np
from scipy import signal
from audio_engine import AudioEffect

class DistortionPedal(AudioEffect):
    """Simple distortion/overdrive pedal"""
    
    def __init__(self):
        super().__init__("Distortion")
        self.parameters = {
            'drive': 2.0,
            'level': 0.5,
            'tone': 0.5
        }
    
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        drive = self.parameters['drive']
        level = self.parameters['level']
        
        # Apply drive/gain
        driven = input_buffer * drive
        
        # Soft clipping
        output = np.tanh(driven)
        
        # Apply output level
        return output * level

class DelayPedal(AudioEffect):
    """Digital delay pedal"""
    
    def __init__(self, max_delay_ms: float = 1000.0):
        super().__init__("Delay")
        self.max_delay_samples = int(44100 * max_delay_ms / 1000)
        self.delay_buffer = np.zeros(self.max_delay_samples)
        self.write_pos = 0
        self.parameters = {
            'delay_time': 250.0,  # ms
            'feedback': 0.3,
            'mix': 0.3
        }
    
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        delay_samples = int(sample_rate * self.parameters['delay_time'] / 1000)
        feedback = self.parameters['feedback']
        mix = self.parameters['mix']
        
        output = np.zeros_like(input_buffer)
        
        for i, sample in enumerate(input_buffer):
            # Read delayed sample
            read_pos = (self.write_pos - delay_samples) % self.max_delay_samples
            delayed_sample = self.delay_buffer[read_pos]
            
            # Write to delay buffer with feedback
            self.delay_buffer[self.write_pos] = sample + delayed_sample * feedback
            
            # Mix dry and wet signals
            output[i] = sample + delayed_sample * mix
            
            # Advance write position
            self.write_pos = (self.write_pos + 1) % self.max_delay_samples
        
        return output

class ReverbPedal(AudioEffect):
    """Simple reverb using multiple delays"""
    
    def __init__(self):
        super().__init__("Reverb")
        self.delays = [
            np.zeros(int(44100 * 0.03)),  # 30ms
            np.zeros(int(44100 * 0.05)),  # 50ms
            np.zeros(int(44100 * 0.07)),  # 70ms
        ]
        self.positions = [0, 0, 0]
        self.parameters = {
            'room_size': 0.5,
            'damping': 0.3,
            'mix': 0.2
        }
    
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        room_size = self.parameters['room_size']
        mix = self.parameters['mix']
        
        output = input_buffer.copy()
        
        for i, sample in enumerate(input_buffer):
            reverb_sum = 0
            
            for j, delay_line in enumerate(self.delays):
                # Read from delay line
                reverb_sum += delay_line[self.positions[j]]
                
                # Write to delay line with feedback
                delay_line[self.positions[j]] = sample + delay_line[self.positions[j]] * room_size * 0.5
                
                # Advance position
                self.positions[j] = (self.positions[j] + 1) % len(delay_line)
            
            output[i] = sample + reverb_sum * mix
        
        return output