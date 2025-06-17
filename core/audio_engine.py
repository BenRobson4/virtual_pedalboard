"""Low-latency audio processing engine with mono/stereo support"""

import numpy as np
import sounddevice as sd
from typing import List, Optional, Literal
from .audio_effect import AudioEffect


class AudioEngine:
    """Low-latency audio processing engine with mono/stereo support
    
    Attributes:
        sample_rate (int): Sample rate in Hz
        buffer_size (int): Audio buffer size in samples
        audio_mode (str): 'mono' or 'stereo'
        effects_chain (List[AudioEffect]): List of effects in processing chain
        running (bool): Whether the engine is currently running
    """
    
    def __init__(self, 
                 sample_rate: int = 44100, 
                 buffer_size: int = 64,
                 audio_mode: Literal['mono', 'stereo'] = 'mono'):
        """Initialize the audio engine
        
        Args:
            sample_rate: Sample rate in Hz
            buffer_size: Audio buffer size in samples
            audio_mode: 'mono' or 'stereo' processing mode
        """
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.audio_mode = audio_mode
        self.channels = 1 if audio_mode == 'mono' else 2
        self.effects_chain: List[AudioEffect] = []
        self.running = False
        self.stream = None
        
        # Pre-allocate buffers for performance
        if self.audio_mode == 'mono':
            self.working_buffer = np.zeros(buffer_size, dtype=np.float32)
        else:
            self.working_buffer_left = np.zeros(buffer_size, dtype=np.float32)
            self.working_buffer_right = np.zeros(buffer_size, dtype=np.float32)
        
    def add_effect(self, effect: AudioEffect) -> None:
        """Add effect to the chain
        
        Args:
            effect: AudioEffect instance to add
        """
        self.effects_chain.append(effect)
        print(f"Added effect: {effect.name}")
    
    def remove_effect(self, effect_name: str) -> None:
        """Remove effect from chain by name
        
        Args:
            effect_name: Name of the effect to remove
        """
        self.effects_chain = [e for e in self.effects_chain if e.name != effect_name]
        print(f"Removed effect: {effect_name}")
    
    def clear_effects(self) -> None:
        """Remove all effects from the chain"""
        self.effects_chain.clear()
        print("Cleared all effects")
    
    def audio_callback_mono(self, indata, outdata, frames, time, status):
        """Real-time audio callback for mono processing"""
        if status:
            print(f"Audio callback status: {status}")
        
        # Copy input data
        audio_data = indata[:, 0].copy()
        
        # Process through effects chain
        for effect in self.effects_chain:
            if effect.enabled:
                audio_data = effect.process(audio_data, self.sample_rate)
        
        # Output processed audio
        outdata[:, 0] = audio_data
    
    def audio_callback_stereo(self, indata, outdata, frames, time, status):
        """Real-time audio callback for stereo processing"""
        if status:
            print(f"Audio callback status: {status}")
        
        # Copy input data
        left_data = indata[:, 0].copy()
        right_data = indata[:, 1].copy()
        
        # Process through effects chain
        for effect in self.effects_chain:
            if effect.enabled:
                if effect.is_stereo:
                    # True stereo processing
                    left_data, right_data = effect.process_stereo(
                        left_data, right_data, self.sample_rate
                    )
                else:
                    # Process each channel independently
                    left_data = effect.process(left_data, self.sample_rate)
                    right_data = effect.process(right_data, self.sample_rate)
        
        # Output processed audio
        outdata[:, 0] = left_data
        outdata[:, 1] = right_data
    
    def start(self) -> None:
        """Start audio processing"""
        if self.running:
            print("Audio engine is already running")
            return
            
        self.running = True
        
        # Select appropriate callback based on mode
        callback = self.audio_callback_mono if self.audio_mode == 'mono' else self.audio_callback_stereo
        
        self.stream = sd.Stream(
            samplerate=self.sample_rate,
            blocksize=self.buffer_size,
            channels=self.channels,
            callback=callback,
            latency='low'
        )
        self.stream.start()
        print(f"Audio engine started - Mode: {self.audio_mode}, Sample rate: {self.sample_rate}, Buffer size: {self.buffer_size}")
    
    def stop(self) -> None:
        """Stop audio processing"""
        if not self.running:
            print("Audio engine is not running")
            return
            
        self.running = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("Audio engine stopped")
    
    def get_latency(self) -> Optional[float]:
        """Get current audio latency in milliseconds
        
        Returns:
            Latency in ms, or None if engine not running
        """
        if self.stream and self.running:
            return (self.buffer_size / self.sample_rate) * 1000
        return None
    
    def __repr__(self) -> str:
        return f"AudioEngine(mode={self.audio_mode}, rate={self.sample_rate}, buffer={self.buffer_size}, effects={len(self.effects_chain)})"
