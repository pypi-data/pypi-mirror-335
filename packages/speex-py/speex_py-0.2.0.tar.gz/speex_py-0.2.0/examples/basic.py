from dataclasses import dataclass
import os
from speex_py import SpeexPreprocessor, version
import soundfile as sf
import numpy as np
import threading

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

print(f"frame_size: {processor.frame_size}")
print(f"sampling_rate: {processor.sampling_rate}")

print("denoise:", processor.get_denoise())
print("agc:", processor.get_agc())


# Read the audio file
audio_data, sample_rate = sf.read(".protected/cut_call_original.wav")

print(type(audio_data))
print(audio_data.shape)
print(f"audio_data dtype: {audio_data.dtype}")


clean_audio: list[np.ndarray] = []
# Create a list to store speech detection results with sample indices
speech_detection_results = []
def process_all():
    global clean_audio, processor
    sample_index = 0
    print("Thread: Processing all")
    for i in range(0, len(audio_data), processor.frame_size):
        print(f"Thread: Processing frame {i}")
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
        
        processed_audio_bytes, is_speech = processor.process(received, original)
        
        # Store the speech detection result with sample index
        speech_detection_results.append((sample_index, is_speech))
        sample_index += frame_length
        
        assert len(processed_audio_bytes) == len(received)

        # Convert both to numpy arrays to properly compare their content
        received_array = np.frombuffer(received, dtype=np.int16)
        processed_array = np.frombuffer(processed_audio_bytes, dtype=np.int16)

        # Convert the processed bytes back to a numpy array before appending
        processed_audio_array = np.frombuffer(processed_audio_bytes, dtype=np.int16)
        
        # Convert from int16 back to float64 (scale back to original range)
        processed_audio_float = processed_audio_array.astype(np.float64) / 32767.0
        
        
        # Only append the actual audio data (not the padding)
        if frame_length < processor.frame_size:
            clean_audio.append(processed_audio_float[:frame_length])
        else:
            clean_audio.append(processed_audio_float)




# Create a thread to run the processing in the background
thread = threading.Thread(target=process_all)
thread.start()

# Wait for the thread to finish

try:
    thread.join()
    print("Cleaning up processor")
    print("agc:", processor.get_agc())
    processor.cleanup()
except Exception as e:
    print(f"Error cleaning up processor: {e}")

# Concatenate all processed frames
clean_audio_array = np.concatenate(clean_audio)
print(clean_audio_array.shape)



# Compare the processed audio with the original right channel
original_right = audio_data[:len(clean_audio_array), 1]

out_folder = ".protected"
os.makedirs(out_folder, exist_ok=True)

sf.write(f'{out_folder}/{config.to_file_name()}.wav', clean_audio_array, sample_rate)

print(f"saved to {out_folder}/{config.to_file_name()}.wav")