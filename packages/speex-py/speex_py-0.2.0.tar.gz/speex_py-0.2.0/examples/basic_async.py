from dataclasses import dataclass
import os
from speex_py import SpeexPreprocessor, version
import soundfile as sf
import numpy as np
import threading
import time

print("Example Basic")

print(version())


@dataclass
class Config:
    denoise: int | None
    vad: bool
    echo: int | None
    agc: int | None

    def to_file_name(self):
        parts = []
        if self.denoise:
            parts.append(f"dn{self.denoise}")
        if self.vad:
            parts.append("vad")
        if self.echo:
            parts.append(f"e{self.echo}")
        if self.agc:
            parts.append(f"agc{self.agc}")
        return "_".join(parts) if parts else "none"

    def apply(self, processor: SpeexPreprocessor):
        if self.denoise:
            processor.set_denoise(self.denoise)
        if self.vad:
            processor.set_vad(self.vad)
        if self.echo:
            processor.set_echo(self.echo)
        if self.agc:
            processor.set_agc(enabled=self.agc is not None, 
                              level=self.agc,
                              max_gain=15,
                              increment=3,
                              decrement=10,
                              )


# SETUP

config = Config(denoise=30, vad=False, echo=8192, agc=24000)

print("Creating processor")
processor = SpeexPreprocessor(frame_size=1024, sampling_rate=16000)
print("Applying config")
config.apply(processor)
print(f"current thread: {threading.current_thread().name}")
print(f"frame_size: {processor.frame_size}")
print(f"sampling_rate: {processor.sampling_rate}")



# Read the audio file
audio_data, sample_rate = sf.read(".protected/cut_call_original.wav")

print(type(audio_data))
print(audio_data.shape)
print(f"audio_data dtype: {audio_data.dtype}")


clean_audio: list[np.ndarray] = []
# Create a list to store speech detection results with sample indices
speech_detection_results = []
sample_index = 0
print("Thread: Processing all")

# Track the number of pending callbacks
pending_callbacks = 0
callback_condition = threading.Condition()
    
# Keep a list of callbacks to prevent garbage collection
def callback(processed_bytes: bytes, vad: bool):
    global sample_index, pending_callbacks

    print(f"callback thread: {threading.current_thread().name}")
    with callback_condition:
        speech_detection_results.append((sample_index, vad))
        sample_index += frame_length
        
        assert len(processed_bytes) == len(received)
        # Convert the processed bytes back to a numpy array before appending
        processed_audio_array = np.frombuffer(processed_bytes, dtype=np.int16)
        
        # Convert from int16 back to float64 (scale back to original range)
        processed_audio_float = processed_audio_array.astype(np.float64) / 32767.0

        # Only append the actual audio data (not the padding)
        if frame_length < processor.frame_size:
            clean_audio.append(processed_audio_float[:frame_length])
        else:
            clean_audio.append(processed_audio_float)
            
        # Decrement pending callbacks counter
        pending_callbacks -= 1
        # Notify waiting threads that a callback completed
        callback_condition.notify_all()

for i in range(0, len(audio_data), processor.frame_size):
    print(f"Thread: Processing frame {i // processor.frame_size} of {len(audio_data) // processor.frame_size}")
    # Get the current frame
    frame_end = min(i + processor.frame_size, len(audio_data))
    frame_length = frame_end - i

    
    # If the frame is shorter than frame_size, we need to pad
    if frame_length < processor.frame_size:
        # Create padded arrays for both channels
        padded_original = np.zeros(processor.frame_size, dtype=audio_data.dtype)
        padded_received = np.zeros(processor.frame_size, dtype=audio_data.dtype)
        
        # Copy the available data
        padded_original[:frame_length] = audio_data[i:frame_end, 1]
        padded_received[:frame_length] = audio_data[i:frame_end, 0]
        
        # Convert to bytes - scale float to int16 range
        original = (padded_original * 32767).astype('int16').tobytes()  # Right channel - original audio
        received = (padded_received * 32767).astype('int16').tobytes()  # Left channel - received signal with echo
    else:
        # Process full-sized frame normally - scale float to int16 range
        original = (audio_data[i:frame_end, 1] * 32767).astype('int16').tobytes()  # Right channel - original audio
        received = (audio_data[i:frame_end, 0] * 32767).astype('int16').tobytes()  # Left channel - received signal with echo
    
    
    # Increment pending callbacks counter before starting processing
    with callback_condition:
        pending_callbacks += 1
    
    # Add the callback to our list to prevent garbage collection
    processor.process_async(received, original, callback)
    

# Wait for the thread to finish
try:
    # Wait for all callbacks to complete
    with callback_condition:
        while pending_callbacks > 0:
            print(f"Waiting for {pending_callbacks} callbacks to complete...")
            callback_condition.wait()
    
    print("All callbacks completed")
    
    # Concatenate all processed frames
    clean_audio_array = np.concatenate(clean_audio)
    print(clean_audio_array.shape)

    out_folder = ".protected"
    os.makedirs(out_folder, exist_ok=True)

    sf.write(f'{out_folder}/{config.to_file_name()}.wav', clean_audio_array, sample_rate)

    print(f"saved to {out_folder}/{config.to_file_name()}.wav")
    
    # Only clean up after all processing is complete
    print("Cleaning up processor")
    processor.cleanup()
except Exception as e:
    print(f"Error: {e}")