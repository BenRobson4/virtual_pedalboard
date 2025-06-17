# Virtual Pedalboard

A real-time audio effects processing system with support for both mono and stereo audio.

## Features

- **Low-latency audio processing** with configurable buffer sizes
- **Mono and stereo support** with automatic format detection
- **Modular effect system** with easy-to-extend base classes
- **Built-in effects**:
  - Distortion/Overdrive with multiple clipping modes
  - Digital Delay with stereo ping-pong support
  - Reverb with multiple delay lines and diffusion
- **Interactive control** system for real-time parameter adjustment
- **Clean architecture** with separated concerns

## Project Structure

```
virtual_pedalboard/
├── core/                    # Core audio processing components
│   ├── __init__.py
│   ├── audio_effect.py     # Base class for all effects
│   └── audio_engine.py     # Main audio processing engine
├── effects/                # Audio effects implementations
│   ├── __init__.py
│   ├── distortion/        # Distortion effect module
│   │   ├── __init__.py
│   │   └── distortion_pedal.py
│   ├── delay/             # Delay effect module
│   │   ├── __init__.py
│   │   └── delay_pedal.py
│   └── reverb/            # Reverb effect module
│       ├── __init__.py
│       └── reverb_pedal.py
├── ui/                    # User interface components
│   ├── __init__.py
│   └── pedalboard.py      # Main pedalboard application
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── audio_utils.py     # Audio processing utilities
├── examples/              # Example scripts
│   ├── stereo_demo.py     # Stereo processing demonstration
│   └── custom_effect_demo.py  # Creating custom effects
├── tests/                 # Unit tests (to be implemented)
├── main.py               # Main entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd virtual_pedalboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the pedalboard with default settings (mono mode):
```bash
python main.py
```

Run in stereo mode:
```bash
python main.py --mode stereo
```

### Command Line Options

- `--mode {mono,stereo}`: Audio processing mode (default: mono)
- `--buffer-size BUFFER_SIZE`: Audio buffer size in samples (default: 64)
- `--sample-rate SAMPLE_RATE`: Sample rate in Hz (default: 44100)
- `--no-interactive`: Run without interactive controls

### Interactive Controls

When running in interactive mode:
- **1**: Toggle Distortion
- **2**: Toggle Delay
- **3**: Toggle Reverb
- **4**: Adjust Distortion Drive
- **5**: Adjust Delay Time
- **6**: Adjust Reverb Mix
- **7**: Show Status
- **8**: Reset All Effects
- **Q**: Quit

## Creating Custom Effects

To create a custom effect, inherit from `AudioEffect`:

```python
from core.audio_effect import AudioEffect
import numpy as np

class MyCustomEffect(AudioEffect):
    def __init__(self):
        super().__init__("MyEffect")
        self.parameters = {
            'param1': 0.5,
            'param2': 1.0
        }
    
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        # Your processing code here
        return processed_buffer
```

For stereo effects, set `is_stereo=True` and optionally override `process_stereo()`:

```python
class MyStereoEffect(AudioEffect):
    def __init__(self):
        super().__init__("MyStereoEffect", is_stereo=True)
    
    def process_stereo(self, left_buffer: np.ndarray, right_buffer: np.ndarray, 
                      sample_rate: int) -> Tuple[np.ndarray, np.ndarray]:
        # Custom stereo processing
        return processed_left, processed_right
```

## Audio Engine Features

The `AudioEngine` class supports:
- Configurable mono or stereo processing
- Low-latency audio callbacks
- Dynamic effect chain management
- Real-time parameter updates
- Latency reporting

## Performance Considerations

- Keep buffer sizes small (64-256 samples) for low latency
- Avoid heavy computations in the audio callback
- Pre-compute values when possible
- Use numpy operations for better performance

## Requirements

- Python 3.7+
- NumPy
- SciPy
- python-sounddevice

## License

This project is provided as-is for educational and personal use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
