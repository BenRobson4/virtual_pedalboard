"""Example demonstrating stereo processing with ping-pong delay"""

import time
from ..ui.pedalboard import VirtualPedalboard


def main():
    # Create stereo pedalboard
    pedalboard = VirtualPedalboard(
        sample_rate=44100,
        buffer_size=128,
        audio_mode='stereo'
    )
    
    # Setup with stereo effects
    pedalboard.setup_default_pedalboard()
    
    # Configure for stereo demonstration
    pedalboard.set_pedal_parameter('delay', 'delay_time', 375.0)  # 3/8 beat at 120 BPM
    pedalboard.set_pedal_parameter('delay', 'feedback', 0.5)
    pedalboard.set_pedal_parameter('delay', 'mix', 0.4)
    pedalboard.set_pedal_parameter('delay', 'stereo_width', 1.0)  # Full ping-pong
    
    pedalboard.get_pedal('distortion').enabled = False
    pedalboard.get_pedal('delay').enabled = True
    pedalboard.get_pedal('reverb').enabled = True
    
    try:
        pedalboard.start()
        print("Stereo Pedalboard Demo Started!")
        print("Play some audio to hear the ping-pong delay effect")
        print("Press Ctrl+C to stop...")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        pedalboard.stop()


if __name__ == "__main__":
    main()
