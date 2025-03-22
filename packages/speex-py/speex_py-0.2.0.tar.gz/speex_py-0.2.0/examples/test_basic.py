import unittest
import numpy as np
from speex_py import SpeexPreprocessor, version

class TestBasic(unittest.TestCase):
    def test_version(self):
        """Test that version returns a non-empty string"""
        ver = version()
        self.assertIsInstance(ver, str)
        self.assertTrue(len(ver) > 0)
    
    def test_processor_process(self):
        """Test that processor.process returns processed audio bytes"""
        # Create a processor with standard settings
        processor = SpeexPreprocessor(frame_size=1024, sampling_rate=16000)
        
        # Create some dummy audio data (sine wave)
        t = np.linspace(0, 1, processor.frame_size)
        sine_wave = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        
        # Convert to bytes
        received_bytes = sine_wave.tobytes()
        original_bytes = sine_wave.tobytes()  # Using same data for simplicity
        
        # Process the audio
        processed_audio, is_speech = processor.process(received_bytes, original_bytes)
        
        # Verify the result is bytes
        self.assertIsInstance(processed_audio, bytes)
        
        # Verify the length is the same
        self.assertEqual(len(processed_audio), len(received_bytes))
        
        # Convert processed audio back to numpy array for comparison
        processed_array = np.frombuffer(processed_audio, dtype=np.int16)
        received_array = np.frombuffer(received_bytes, dtype=np.int16)
        
        # Verify the processed audio is different from the input
        # (Since processing should modify the audio in some way)
        self.assertFalse(np.array_equal(processed_array, received_array))

    def test_processor_cleanup(self):
        """Test that processor.cleanup works"""
        processor = SpeexPreprocessor(frame_size=1024, sampling_rate=16000)
        processor.cleanup()
        self.assertRaises(RuntimeError, processor.cleanup)
        
if __name__ == "__main__":
    print("Running tests...")
    unittest.main()
