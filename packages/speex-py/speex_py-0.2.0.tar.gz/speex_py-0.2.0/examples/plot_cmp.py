#!/usr/bin/env python3
import sys
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import pandas as pd
import os

def load_and_analyze_audio(file_path):
    """Load audio file and return signal, sample rate and statistics."""
    y, sr = librosa.load(file_path, sr=None)
    
    # Determine number of channels
    if y.ndim > 1:
        channels = y.shape[0]
        # Extract left channel for multi-channel audio
        y = y[0]
    else:
        channels = 1
    
    # Calculate statistics
    duration = librosa.get_duration(y=y, sr=sr)
    rms = np.sqrt(np.mean(y**2))
    peak = np.max(np.abs(y))
    
    stats = {
        "duration": duration,
        "sample_rate": sr,
        "channels": channels,
        "rms": rms,
        "peak": peak,
        "dynamic_range": 20 * np.log10(peak / (rms + 1e-10))
    }
    
    return y, sr, stats

def load_speech_detection(file_path):
    """Load speech detection CSV file if it exists."""
    # Construct the expected speech detection CSV filename
    base_name = os.path.splitext(file_path)[0]
    speech_csv = f"{base_name}_speech_detection.csv"
    
    if os.path.exists(speech_csv):
        try:
            return pd.read_csv(speech_csv)
        except Exception as e:
            print(f"Warning: Could not load speech detection file {speech_csv}: {e}")
    
    return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python plot_cmp.py <audio_file1> <audio_file2>")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    # Load and analyze both audio files
    y1, sr1, stats1 = load_and_analyze_audio(file1)
    y2, sr2, stats2 = load_and_analyze_audio(file2)
    
    # Load speech detection data if available
    speech_data1 = load_speech_detection(file1)
    speech_data2 = load_speech_detection(file2)
    
    # Create plot with 3 rows if speech data is available, otherwise 2 rows
    if speech_data1 is not None or speech_data2 is not None:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    else:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot first audio waveform
    librosa.display.waveshow(y1, sr=sr1, ax=ax1)
    ax1.set_title(f'Waveform: {file1}')
    ax1.set_xlabel('')
    ax1.set_ylim(-1, 1)  # Set y-axis limits to -1 to 1
    
    # Plot second audio waveform
    librosa.display.waveshow(y2, sr=sr2, ax=ax2)
    ax2.set_title(f'Waveform: {file2}')
    ax2.set_ylim(-1, 1)  # Set y-axis limits to -1 to 1
    
    # Plot speech detection data if available
    if speech_data1 is not None or speech_data2 is not None:
        ax3.set_title('Speech Detection')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Is Speech')
        ax3.set_ylim(-0.1, 1.1)  # Set y-axis limits for binary data
        
        # Plot speech detection for first file
        if speech_data1 is not None:
            ax3.step(speech_data1['timestamp_seconds'], speech_data1['is_speech'], 
                    where='post', label=os.path.basename(file1), alpha=0.7)
        
        # Plot speech detection for second file
        if speech_data2 is not None:
            ax3.step(speech_data2['timestamp_seconds'], speech_data2['is_speech'], 
                    where='post', label=os.path.basename(file2), alpha=0.7, linestyle='--')
        
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # Enable synchronized zooming and panning
    plt.tight_layout()
    
    # Print statistics
    print(f"\nStatistics for {file1}:")
    print(f"Duration: {stats1['duration']:.2f} seconds")
    print(f"Sample rate: {stats1['sample_rate']} Hz")
    print(f"Channels: {stats1['channels']}")
    print(f"RMS amplitude: {stats1['rms']:.6f}")
    print(f"Peak amplitude: {stats1['peak']:.6f}")
    print(f"Dynamic range: {stats1['dynamic_range']:.2f} dB")
    
    print(f"\nStatistics for {file2}:")
    print(f"Duration: {stats2['duration']:.2f} seconds")
    print(f"Sample rate: {stats2['sample_rate']} Hz")
    print(f"Channels: {stats2['channels']}")
    print(f"RMS amplitude: {stats2['rms']:.6f}")
    print(f"Peak amplitude: {stats2['peak']:.6f}")
    print(f"Dynamic range: {stats2['dynamic_range']:.2f} dB")
    
    plt.show()

if __name__ == "__main__":
    main()
