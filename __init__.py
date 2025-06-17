"""Virtual Pedalboard - A real-time audio effects processing system"""

__version__ = "1.0.0"
__author__ = "Virtual Pedalboard Team"

from .core.audio_engine import AudioEngine
from .core.audio_effect import AudioEffect
from .ui.pedalboard import VirtualPedalboard

__all__ = ['AudioEngine', 'AudioEffect', 'VirtualPedalboard']
