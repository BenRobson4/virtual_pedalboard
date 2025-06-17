# main.py
from audio_engine import AudioEngine
from pedals import DistortionPedal, DelayPedal, ReverbPedal
import time

class VirtualPedalboard:
    def __init__(self):
        self.engine = AudioEngine(sample_rate=44100, buffer_size=64)
        self.pedals = {}
        self.setup_default_pedalboard()
    
    def setup_default_pedalboard(self):
        """Setup a basic pedalboard"""
        # Add pedals in signal chain order
        distortion = DistortionPedal()
        delay = DelayPedal()
        reverb = ReverbPedal()
        
        self.engine.add_effect(distortion)
        self.engine.add_effect(delay)
        self.engine.add_effect(reverb)
        
        self.pedals['distortion'] = distortion
        self.pedals['delay'] = delay
        self.pedals['reverb'] = reverb
    
    def start(self):
        """Start the pedalboard"""
        self.engine.start()
    
    def stop(self):
        """Stop the pedalboard"""
        self.engine.stop()

if __name__ == "__main__":
    pedalboard = VirtualPedalboard()
    
    try:
        pedalboard.start()
        print("Pedalboard started! Press Ctrl+C to stop.")
        
        # Example: Modify pedal parameters in real-time
        time.sleep(2)
        pedalboard.pedals['distortion'].set_parameter('drive', 5.0)
        print("Increased distortion drive")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping pedalboard...")
    finally:
        pedalboard.stop()