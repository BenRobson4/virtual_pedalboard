"""Example demonstrating how to create a custom effect"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from core.audio_effect import AudioEffect
from ui.pedalboard import VirtualPedalboard


class TremoloEffect(AudioEffect):
    """Simple tremolo effect (amplitude modulation)"""
    
    def __init__(self, name: str = "Tremolo"):
        super().__init__(name)
        self.parameters = {
            'rate': 5.0,      # Hz
            'depth': 0.5,     # 0-1
            'waveform': 0     # 0=sine, 1=square, 2=triangle
        }
        self.phase = 0.0
        
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        rate = self.parameters['rate']
        depth = self.parameters['depth']
        waveform = int(self.parameters['waveform'])
        
        output = np.zeros_like(input_buffer)
        phase_increment = 2 * np.pi * rate / sample_rate
        
        for i, sample in enumerate(input_buffer):
            # Generate modulation signal
            if waveform == 0:  # Sine
                modulation = np.sin(self.phase)
            elif waveform == 1:  # Square
                modulation = 1.0 if np.sin(self.phase) > 0 else -1.0
            else:  # Triangle
                modulation = 2 * np.arcsin(np.sin(self.phase)) / np.pi
            
            # Apply tremolo (1 + depth * modulation) / 2 for 0-1 range
            gain = (1 + depth * modulation) / 2
            output[i] = sample * gain
            
            # Update phase
            self.phase += phase_increment
            if self.phase >= 2 * np.pi:
                self.phase -= 2 * np.pi
                
        return output


class PhaserEffect(AudioEffect):
    """Simple phaser effect using all-pass filters"""
    
    def __init__(self, name: str = "Phaser"):
        super().__init__(name)
        self.parameters = {
            'rate': 0.5,      # Hz
            'depth': 1.0,     # 0-1
            'feedback': 0.7,  # 0-0.9
            'mix': 0.5        # 0-1
        }
        self.phase = 0.0
        
        # All-pass filter states
        self.num_stages = 4
        self.states = np.zeros(self.num_stages)
        
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        rate = self.parameters['rate']
        depth = self.parameters['depth']
        feedback = self.parameters['feedback']
        mix = self.parameters['mix']
        
        output = np.zeros_like(input_buffer)
        phase_increment = 2 * np.pi * rate / sample_rate
        
        for i, sample in enumerate(input_buffer):
            # LFO for modulating all-pass filter frequency
            lfo = (np.sin(self.phase) + 1) / 2  # 0-1 range
            
            # All-pass filter coefficient
            # Varies between 0.2 and 0.9 based on LFO
            coeff = 0.2 + 0.7 * lfo * depth
            
            # Process through cascaded all-pass filters
            filtered = sample
            for stage in range(self.num_stages):
                # All-pass filter: y = -x + a*(x - y_prev) + y_prev
                temp = filtered - self.states[stage] * coeff
                filtered = -filtered + coeff * temp + self.states[stage]
                self.states[stage] = temp
            
            # Apply feedback
            filtered += sample * feedback
            
            # Mix dry and wet
            output[i] = sample * (1 - mix) + filtered * mix
            
            # Update phase
            self.phase += phase_increment
            if self.phase >= 2 * np.pi:
                self.phase -= 2 * np.pi
                
        return output


def main():
    # Create pedalboard
    pedalboard = VirtualPedalboard(
        sample_rate=44100,
        buffer_size=64,
        audio_mode='mono'
    )
    
    # Add custom effects
    tremolo = TremoloEffect()
    phaser = PhaserEffect()
    
    pedalboard.add_pedal('tremolo', tremolo)
    pedalboard.add_pedal('phaser', phaser)
    
    # Setup some other effects
    pedalboard.setup_default_pedalboard()
    pedalboard.get_pedal('distortion').enabled = False
    pedalboard.get_pedal('delay').enabled = False
    pedalboard.get_pedal('reverb').enabled = False
    
    try:
        pedalboard.start()
        print("Custom Effect Demo Started!")
        print("Tremolo and Phaser effects are active")
        print("\nPress keys to control effects:")
        print("1: Toggle Tremolo")
        print("2: Toggle Phaser")
        print("3: Change Tremolo rate")
        print("4: Change Phaser rate")
        print("Q: Quit")
        
        import sys
        if sys.platform != 'win32':
            import termios, tty
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        
        while True:
            if sys.platform == 'win32':
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8').upper()
                else:
                    time.sleep(0.1)
                    continue
            else:
                import select
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1).upper()
                else:
                    time.sleep(0.1)
                    continue
            
            if key == '1':
                pedalboard.toggle_pedal('tremolo')
                print(f"\nTremolo: {'ON' if tremolo.enabled else 'OFF'}")
            elif key == '2':
                pedalboard.toggle_pedal('phaser')
                print(f"\nPhaser: {'ON' if phaser.enabled else 'OFF'}")
            elif key == '3':
                current_rate = tremolo.get_parameter('rate')
                new_rate = (current_rate % 10) + 1
                tremolo.set_parameter('rate', new_rate)
                print(f"\nTremolo rate: {new_rate} Hz")
            elif key == '4':
                current_rate = phaser.get_parameter('rate')
                new_rate = (current_rate + 0.25) % 2.0
                phaser.set_parameter('rate', new_rate)
                print(f"\nPhaser rate: {new_rate:.2f} Hz")
            elif key == 'Q':
                break
                
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        if sys.platform != 'win32':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        pedalboard.stop()


if __name__ == "__main__":
    main()
