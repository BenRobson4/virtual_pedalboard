"""Virtual Pedalboard main application class"""

from typing import Dict, Optional, Literal
from ..core import AudioEngine, AudioEffect
from ..effects import DistortionPedal, DelayPedal, ReverbPedal


class VirtualPedalboard:
    """Main virtual pedalboard application
    
    Manages the audio engine and effects chain for real-time audio processing.
    """
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 buffer_size: int = 64,
                 audio_mode: Literal['mono', 'stereo'] = 'mono'):
        """Initialize the virtual pedalboard
        
        Args:
            sample_rate: Audio sample rate in Hz
            buffer_size: Audio buffer size in samples
            audio_mode: 'mono' or 'stereo' processing mode
        """
        self.engine = AudioEngine(
            sample_rate=sample_rate, 
            buffer_size=buffer_size,
            audio_mode=audio_mode
        )
        self.pedals: Dict[str, AudioEffect] = {}
        self.audio_mode = audio_mode
    
    def setup_default_pedalboard(self) -> None:
        """Setup a basic pedalboard with common effects"""
        # Create pedals with stereo support if in stereo mode
        is_stereo = self.audio_mode == 'stereo'
        
        # Add pedals in signal chain order
        distortion = DistortionPedal("Distortion")
        delay = DelayPedal("Delay", is_stereo=is_stereo)
        reverb = ReverbPedal("Reverb", is_stereo=is_stereo)
        
        # Start with some effects disabled
        delay.enabled = False
        reverb.enabled = False
        
        self.add_pedal("distortion", distortion)
        self.add_pedal("delay", delay)
        self.add_pedal("reverb", reverb)
        
        print(f"Default pedalboard setup complete ({self.audio_mode} mode)")
    
    def add_pedal(self, pedal_id: str, pedal: AudioEffect) -> None:
        """Add a pedal to the pedalboard
        
        Args:
            pedal_id: Unique identifier for the pedal
            pedal: AudioEffect instance
        """
        self.engine.add_effect(pedal)
        self.pedals[pedal_id] = pedal
    
    def remove_pedal(self, pedal_id: str) -> None:
        """Remove a pedal from the pedalboard
        
        Args:
            pedal_id: Identifier of the pedal to remove
        """
        if pedal_id in self.pedals:
            pedal = self.pedals[pedal_id]
            self.engine.remove_effect(pedal.name)
            del self.pedals[pedal_id]
    
    def get_pedal(self, pedal_id: str) -> Optional[AudioEffect]:
        """Get a pedal by its identifier
        
        Args:
            pedal_id: Pedal identifier
            
        Returns:
            AudioEffect instance or None if not found
        """
        return self.pedals.get(pedal_id)
    
    def set_pedal_parameter(self, pedal_id: str, param_name: str, value: float) -> None:
        """Set a parameter on a specific pedal
        
        Args:
            pedal_id: Pedal identifier
            param_name: Parameter name
            value: Parameter value
        """
        if pedal_id in self.pedals:
            self.pedals[pedal_id].set_parameter(param_name, value)
        else:
            raise ValueError(f"Pedal '{pedal_id}' not found")
    
    def toggle_pedal(self, pedal_id: str) -> None:
        """Toggle a pedal on/off
        
        Args:
            pedal_id: Pedal identifier
        """
        if pedal_id in self.pedals:
            self.pedals[pedal_id].toggle()
            state = "ON" if self.pedals[pedal_id].enabled else "OFF"
            print(f"{pedal_id}: {state}")
        else:
            raise ValueError(f"Pedal '{pedal_id}' not found")
    
    def start(self) -> None:
        """Start the pedalboard audio processing"""
        self.engine.start()
    
    def stop(self) -> None:
        """Stop the pedalboard audio processing"""
        self.engine.stop()
    
    def get_status(self) -> Dict:
        """Get current pedalboard status
        
        Returns:
            Dictionary with status information
        """
        return {
            'running': self.engine.running,
            'audio_mode': self.audio_mode,
            'sample_rate': self.engine.sample_rate,
            'buffer_size': self.engine.buffer_size,
            'latency_ms': self.engine.get_latency(),
            'pedals': {
                pedal_id: {
                    'name': pedal.name,
                    'enabled': pedal.enabled,
                    'parameters': pedal.parameters
                }
                for pedal_id, pedal in self.pedals.items()
            }
        }
    
    def __repr__(self) -> str:
        return f"VirtualPedalboard(mode={self.audio_mode}, pedals={list(self.pedals.keys())})"
