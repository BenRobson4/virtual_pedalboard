"""Main entry point for the Virtual Pedalboard application"""

import time
import argparse
from typing import Optional
from .ui.pedalboard import VirtualPedalboard


def print_menu():
    """Print interactive menu"""
    print("\n" + "="*50)
    print("Virtual Pedalboard Controls:")
    print("="*50)
    print("1. Toggle Distortion")
    print("2. Toggle Delay") 
    print("3. Toggle Reverb")
    print("4. Adjust Distortion Drive")
    print("5. Adjust Delay Time")
    print("6. Adjust Reverb Mix")
    print("7. Show Status")
    print("8. Reset All Effects")
    print("Q. Quit")
    print("="*50)


def interactive_mode(pedalboard: VirtualPedalboard):
    """Run pedalboard in interactive mode"""
    import sys
    if sys.platform == 'win32':
        import msvcrt
        
        def get_key():
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8').upper()
            return None
    else:
        import termios, tty, select
        
        def get_key():
            if select.select([sys.stdin], [], [], 0)[0]:
                return sys.stdin.read(1).upper()
            return None
        
        # Set terminal to raw mode
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())
    
    try:
        print_menu()
        
        while True:
            key = get_key()
            
            if key == '1':
                pedalboard.toggle_pedal('distortion')
            elif key == '2':
                pedalboard.toggle_pedal('delay')
            elif key == '3':
                pedalboard.toggle_pedal('reverb')
            elif key == '4':
                current = pedalboard.get_pedal('distortion').get_parameter('drive')
                new_drive = (current % 10) + 1  # Cycle 1-10
                pedalboard.set_pedal_parameter('distortion', 'drive', new_drive)
                print(f"\nDistortion drive: {new_drive}")
            elif key == '5':
                current = pedalboard.get_pedal('delay').get_parameter('delay_time')
                new_delay = ((current + 100) % 1000) + 100  # Cycle 100-1000ms
                pedalboard.set_pedal_parameter('delay', 'delay_time', new_delay)
                print(f"\nDelay time: {new_delay}ms")
            elif key == '6':
                current = pedalboard.get_pedal('reverb').get_parameter('mix')
                new_mix = (current + 0.1) % 1.0  # Cycle 0-1
                pedalboard.set_pedal_parameter('reverb', 'mix', new_mix)
                print(f"\nReverb mix: {new_mix:.1f}")
            elif key == '7':
                status = pedalboard.get_status()
                print(f"\n{status}")
            elif key == '8':
                for pedal in pedalboard.pedals.values():
                    pedal.reset()
                print("\nAll effects reset")
            elif key == 'Q':
                break
            
            time.sleep(0.05)  # Small delay to prevent CPU spinning
            
    finally:
        if sys.platform != 'win32':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Virtual Pedalboard - Real-time audio effects processor')
    parser.add_argument('--mode', choices=['mono', 'stereo'], default='mono',
                       help='Audio processing mode (default: mono)')
    parser.add_argument('--buffer-size', type=int, default=64,
                       help='Audio buffer size in samples (default: 64)')
    parser.add_argument('--sample-rate', type=int, default=44100,
                       help='Sample rate in Hz (default: 44100)')
    parser.add_argument('--no-interactive', action='store_true',
                       help='Run without interactive controls')
    
    args = parser.parse_args()
    
    # Create pedalboard
    pedalboard = VirtualPedalboard(
        sample_rate=args.sample_rate,
        buffer_size=args.buffer_size,
        audio_mode=args.mode
    )
    
    # Setup default effects
    pedalboard.setup_default_pedalboard()
    
    try:
        # Start audio processing
        pedalboard.start()
        print(f"\nVirtual Pedalboard started in {args.mode} mode!")
        print(f"Sample rate: {args.sample_rate} Hz, Buffer size: {args.buffer_size} samples")
        print(f"Latency: {pedalboard.engine.get_latency():.1f} ms")
        
        if args.no_interactive:
            print("\nPress Ctrl+C to stop...")
            while True:
                time.sleep(1)
        else:
            print("\nStarting interactive mode...")
            time.sleep(1)  # Give audio engine time to stabilize
            interactive_mode(pedalboard)
            
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        pedalboard.stop()
        print("Goodbye!")


if __name__ == "__main__":
    main()
