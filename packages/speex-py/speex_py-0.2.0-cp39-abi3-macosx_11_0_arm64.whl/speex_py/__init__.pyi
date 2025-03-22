from typing import Callable


def version() -> str: ...


class SpeexPreprocessor:
    frame_size: int
    sampling_rate: int
    
    def __init__(self, frame_size: int, sampling_rate: int) -> None: ...

    
    def process_async(self, input: bytes, echo: bytes, callback: Callable[[bytes, bool], None]) -> None:
        """
        Process the input audio data asynchronously.
        Input data must be 16-bit PCM samples in the right frame size, else will raise an error.

        Calls the callback in a seperate thread with the processed audio data and a boolean indicating if the input was detected as speech. (VAD is currently buggy!!!)
        """
        ...

    def set_denoise(self, supression_db: int | None = None) -> None:
        """
        Enable or disable the noise suppression and set the suppression level
        If supression_db is None, noise suppression is disabled
        If supression_db is provided, it specifies the attenuation in dB (positive value)
        """
        ...
    

    
    def set_echo(self, filter_length: int) -> None:
        """
        Enable echo cancellation with the specified filter length
        """
        ...
    
    def set_agc(self, enabled: bool, level: int | None = None, increment: int | None = None, 
                decrement: int | None = None, max_gain: int | None = None) -> None:
        """
        Enable or disable Automatic Gain Control (AGC) and optionally configure its parameters
        - level: Target level for the AGC
        - increment: How fast the gain can increase
        - decrement: How fast the gain can decrease
        - max_gain: Maximum gain that can be applied
        """
        ...

    
    def cleanup(self) -> None:
        """
        Clean up the Speex preprocessor resources. Any calls to process() after this will raise an error.
        """
        ...
