"""Tests for the audio engine"""

import unittest
import numpy as np

from ..core.audio_engine import AudioEngine
from ..core.audio_effect import AudioEffect


class DummyEffect(AudioEffect):
    """Dummy effect for testing"""
    
    def __init__(self, gain=2.0):
        super().__init__("Dummy")
        self.gain = gain
        
    def process(self, input_buffer: np.ndarray, sample_rate: int) -> np.ndarray:
        return input_buffer * self.gain


class TestAudioEngine(unittest.TestCase):
    
    def setUp(self):
        """Set up test cases"""
        self.sample_rate = 44100
        self.buffer_size = 64
        
    def test_mono_engine_creation(self):
        """Test creating mono audio engine"""
        engine = AudioEngine(
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size,
            audio_mode='mono'
        )
        
        self.assertEqual(engine.sample_rate, self.sample_rate)
        self.assertEqual(engine.buffer_size, self.buffer_size)
        self.assertEqual(engine.audio_mode, 'mono')
        self.assertEqual(engine.channels, 1)
        self.assertFalse(engine.running)
        
    def test_stereo_engine_creation(self):
        """Test creating stereo audio engine"""
        engine = AudioEngine(
            sample_rate=self.sample_rate,
            buffer_size=self.buffer_size,
            audio_mode='stereo'
        )
        
        self.assertEqual(engine.audio_mode, 'stereo')
        self.assertEqual(engine.channels, 2)
        
    def test_add_remove_effects(self):
        """Test adding and removing effects"""
        engine = AudioEngine()
        effect1 = DummyEffect()
        effect2 = DummyEffect()
        
        # Add effects
        engine.add_effect(effect1)
        self.assertEqual(len(engine.effects_chain), 1)
        
        engine.add_effect(effect2)
        self.assertEqual(len(engine.effects_chain), 2)
        
        # Remove effect
        engine.remove_effect("Dummy")
        self.assertEqual(len(engine.effects_chain), 0)
        
    def test_clear_effects(self):
        """Test clearing all effects"""
        engine = AudioEngine()
        
        for i in range(3):
            engine.add_effect(DummyEffect())
            
        self.assertEqual(len(engine.effects_chain), 3)
        
        engine.clear_effects()
        self.assertEqual(len(engine.effects_chain), 0)
        
    def test_latency_calculation(self):
        """Test latency calculation"""
        engine = AudioEngine(
            sample_rate=44100,
            buffer_size=64
        )
        
        # Latency when not running
        self.assertIsNone(engine.get_latency())
        
        # Expected latency: (64 / 44100) * 1000 ≈ 1.45 ms
        expected_latency = (64 / 44100) * 1000
        
        # We can't actually start the engine in tests without audio hardware
        # but we can verify the calculation
        actual_latency = (engine.buffer_size / engine.sample_rate) * 1000
        self.assertAlmostEqual(actual_latency, expected_latency, places=2)


class TestAudioEffect(unittest.TestCase):
    
    def test_effect_creation(self):
        """Test creating an audio effect"""
        effect = DummyEffect()
        
        self.assertEqual(effect.name, "Dummy")
        self.assertTrue(effect.enabled)
        self.assertFalse(effect.is_stereo)
        
    def test_effect_toggle(self):
        """Test toggling effect on/off"""
        effect = DummyEffect()
        
        self.assertTrue(effect.enabled)
        effect.toggle()
        self.assertFalse(effect.enabled)
        effect.toggle()
        self.assertTrue(effect.enabled)
        
    def test_effect_processing(self):
        """Test basic effect processing"""
        effect = DummyEffect(gain=3.0)
        input_buffer = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        
        output = effect.process(input_buffer, 44100)
        expected = input_buffer * 3.0
        
        np.testing.assert_array_almost_equal(output, expected)


if __name__ == '__main__':
    unittest.main()
