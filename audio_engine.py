# audio_engine.py
import numpy as np
import sounddevice as sd
import threading
from abc import ABC, abstractmethod
from typing import List, Optional
import time

class AudioEffect(ABC):
    """Base class for all audio effects/pedals"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.parameters = {}
    
    @abstractmethod
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process audio buffer and return processed audio"""
        pass
    
    def set_parameter(self, param_name: str, value: float):
        """Set effect parameter"""
        self.parameters[param_name] = value
    
    def toggle(self):
        """Enable/disable effect"""
        self.enabled = not self.enabled

class AudioEngine:
    """Low-latency audio processing engine"""
    
    def __init__(self, sample_rate: int = 44100, buffer_size: int = 64):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.effects_chain: List[AudioEffect] = []
        self.running = False
        self.input_buffer = np.zeros(buffer_size, dtype=np.float32)
        self.output_buffer = np.zeros(buffer_size, dtype=np.float32)
        
    def add_effect(self, effect: AudioEffect):
        """Add effect to the chain"""
        self.effects_chain.append(effect)
    
    def remove_effect(self, effect_name: str):
        """Remove effect from chain"""
        self.effects_chain = [e for e in self.effects_chain if e.name != effect_name]
    
    def audio_callback(self, indata, outdata, frames, time, status):
        """Real-time audio callback - keep this minimal for low latency"""
        if status:
            print(f"Audio callback status: {status}")
        
        # Copy input data
        audio_data = indata[:, 0].copy()  # Mono input
        
        # Process through effects chain
        for effect in self.effects_chain:
            if effect.enabled:
                audio_data = effect.process(audio_data, self.sample_rate)
        
        # Output processed audio (mono to stereo)
        outdata[:, 0] = audio_data
        outdata[:, 1] = audio_data
    
    def start(self):
        """Start audio processing"""
        self.running = True
        self.stream = sd.Stream(
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            channels=2,  # Stereo output
            callback=self.audio_callback,
            latency='low'
        )
        self.stream.start()
        print(f"Audio engine started - Sample rate: {self.sample_rate}, Buffer size: {self.buffer_size}")
    
    def stop(self):
        """Stop audio processing"""
        self.running = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()