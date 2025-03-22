"""
Provides an abstract text-to-speech (TTS) class.

with methods for synthesis, playback, and property management.
Designed to be extended by specific TTS engine implementations.
"""

from __future__ import annotations

import io
import logging
import re
import threading
import time
from abc import ABC, abstractmethod
from io import BytesIO
from pathlib import Path
from threading import Event
from typing import (
    Any,
    Callable,
    Union,
)

import numpy as np
import sounddevice as sd
import soundfile as sf

from .ssml import AbstractSSMLNode

# Type Definitions and Constants
FileFormat = Union[str, None]
WordTiming = Union[tuple[float, str], tuple[float, float, str]]
SSML = Union[str, AbstractSSMLNode]
PropertyType = Union[None, float, str]

TIMING_TUPLE_LENGTH_TWO = 2
TIMING_TUPLE_LENGTH_THREE = 3
STEREO_CHANNELS = 2
SIXTEEN_BIT_PCM_SIZE = 2


class AbstractTTS(ABC):
    """
    Abstract class (ABC) for text-to-speech functionalities,
    including synthesis and playback.
    """

    def __init__(self) -> None:
        """Initialize the TTS engine with default values."""
        self.voice_id = None
        self.lang = "en-US"  # Default language
        self.stream = None
        self.audio_rate = 44100
        self.audio_bytes = None
        self.playing = Event()
        self.playing.clear()  # Not playing by default
        self.position = 0  # Position in the byte stream
        self.timings: list[tuple[float, float, str]] = []
        self.timers: list[threading.Timer] = []
        self.properties = {"volume": "", "rate": "", "pitch": ""}
        self.callbacks = {"onStart": None, "onEnd": None, "started-word": None}
        self.stream_lock = threading.Lock()

        # addition for pause resume
        # self.sample_rate is audio_rate
        self.channels = 1
        self.sample_width = 2
        self.chunk_size = 1024

        self.isplaying = False
        self.paused = False
        self.position = 0

        self.stream_pyaudio = None
        self.playback_thread = None
        self.pause_timer = None
        self.pyaudio = None

    @abstractmethod
    def get_voices(self) -> list[dict[str, Any]]:
        """Retrieve a list of available voices from the TTS service."""

    def check_credentials(self) -> bool:
        """
        Verify that the provided credentials are valid by calling get_voices.

        This method should be implemented by the child classes to handle the
          specific credential checks.
        Also try not to use get_voices. It can be wasteful in credits/bandwidth.
        """
        try:
            voices = self.get_voices()
            return bool(voices)
        except (ConnectionError, ValueError):
            return False

    def set_voice(self, voice_id: str, lang: str | None = None) -> None:
        """
        Set the voice for the TTS engine.

        Parameters
        ----------
        voice_id : str
            The ID of the voice to be used for synthesis.

        lang : str | None, optional
            The language code for the voice to be used for synthesis.
            Defaults to None, which will use "en-US".
        """
        self.voice_id = voice_id
        self.lang = lang or "en-US"

    def _convert_mp3_to_pcm(self, mp3_data: bytes) -> bytes:
        """
        Convert MP3 data to raw PCM data.

        :param mp3_data: MP3 audio data as bytes.
        :return: Raw PCM data as bytes (int16).
        """
        from soundfile import read

        # Use soundfile to read MP3 data
        mp3_fp = BytesIO(mp3_data)
        pcm_data, _ = read(mp3_fp, dtype="int16", always_2d=False)
        return pcm_data.tobytes()

    def _strip_wav_header(self, wav_data: bytes) -> bytes:
        """
        Strip the WAV header from the audio data to return raw PCM.

        WAV headers are typically 44 bytes,
        so we slice the data after the header.
        """
        return wav_data[44:]

    def _infer_channels_from_pcm(self, pcm_data: np.ndarray) -> int:
        """
        Infer the number of channels from the PCM data.

        :param pcm_data: PCM data as a numpy array.
        :return: Number of channels (1 for mono, 2 for stereo).
        """
        if pcm_data.ndim == 1:
            return 1  # Mono audio
        if pcm_data.ndim == STEREO_CHANNELS:
            return pcm_data.shape[1]  # Stereo or multi-channel
        msg = "Unsupported PCM data format"
        raise ValueError(msg)

    def _convert_audio(
        self,
        pcm_data: np.ndarray,
        target_format: str,
        sample_rate: int,
    ) -> bytes:
        """
        Convert raw PCM data to a specified audio format.

        :param pcm_data: Raw PCM audio data (assumed to be in int16 format).
        :param target_format: Target format (e.g., 'mp3', 'flac').
        :param sample_rate: Sample rate of the audio data.
        :return: Converted audio data as bytes.
        """
        # Set default format if target_format is None
        if target_format is None:
            target_format = "wav"
        if target_format not in ["mp3", "flac", "wav"]:
            msg = f"Unsupported format: {target_format}"
            raise ValueError(msg)

        # Create an in-memory file object
        output = BytesIO()
        if target_format in ("flac", "wav"):
            from soundfile import write as sf_write

            sf_write(
                output,
                pcm_data,
                samplerate=sample_rate,
                format=target_format.upper(),
            )
            output.seek(0)
            return output.read()
        if target_format == "mp3":
            # Infer number of channels from the shape of the PCM data
            import mp3

            nchannels = self._infer_channels_from_pcm(pcm_data)
            # Ensure sample size is 16-bit PCM
            sample_size = pcm_data.dtype.itemsize
            if sample_size != SIXTEEN_BIT_PCM_SIZE:
                msg = "Only PCM 16-bit sample size is supported"
                raise ValueError(msg)

            pcm_bytes = pcm_data.tobytes()

            # Create an in-memory file object for MP3 output
            output = BytesIO()

            # Initialize the MP3 encoder
            encoder = mp3.Encoder(output)
            encoder.set_bit_rate(64)  # Example bit rate in kbps
            encoder.set_sample_rate(sample_rate)
            encoder.set_channels(nchannels)
            encoder.set_quality(5)  # Adjust quality: 2 = highest, 7 = fastest

            # Write PCM data in chunks
            chunk_size = 8000 * nchannels * sample_size
            for i in range(0, len(pcm_bytes), chunk_size):
                encoder.write(pcm_bytes[i : i + chunk_size])

            # Finalize the MP3 encoding
            encoder.flush()

            # Return the MP3-encoded data
            output.seek(0)
            return output.read()
        msg = f"Unsupported format: {target_format}"
        raise ValueError(msg)

    @abstractmethod
    def synth_to_bytes(self, text: str | SSML, voice_id: str | None = None) -> bytes:
        """
        Transform written text to audio bytes on supported formats.

        Parameters
        ----------
        text : str | SSML
            The text to synthesize, can be plain text or SSML.
        voice_id : str | None, optional
            The ID of the voice to use for synthesis. If None, uses the voice set by set_voice.

        Returns
        -------
        bytes
            Raw PCM data with no headers for sounddevice playback.
        """

    def load_audio(self, audio_bytes: bytes) -> None:
        """
        Load audio bytes into the player.

        Parameters
        ----------
        audio_bytes : bytes
            The raw audio data to be loaded into the player.
            Must be PCM data in int16 format.
        """
        if not audio_bytes:
            msg = "Audio bytes cannot be empty"
            raise ValueError(msg)

        import pyaudio

        self.pyaudio = pyaudio.PyAudio()

        # Convert to numpy array for internal processing
        self._audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        self.audio_bytes = audio_bytes
        self.position = 0

    def _create_stream(self) -> None:
        """Create a new audio stream."""
        if self.stream_pyaudio is not None and not self.stream_pyaudio.is_stopped():
            self.stream_pyaudio.stop_stream()
            self.stream_pyaudio.close()

        self.isplaying = True
        try:
            self.stream_pyaudio = self.pyaudio.open(
                format=self.pyaudio.get_format_from_width(self.sample_width),
                channels=self.channels,
                rate=self.audio_rate,
                output=True,
            )
        except Exception:
            logging.exception("Failed to create stream")
            self.isplaying = False
            raise

    def _playback_loop(self) -> None:
        """Run main playback loop in a separate thread."""
        try:
            self._create_stream()
            self._trigger_callback(
                "onStart"
            )  # Trigger onStart when playback actually starts
            self._on_end_triggered = (
                False  # Reset the guard flag at the start of playback
            )

            while self.isplaying and self.position < len(self.audio_bytes):
                if not self.paused:
                    chunk = self.audio_bytes[
                        self.position : self.position + self.chunk_size
                    ]
                    if chunk:
                        self.stream_pyaudio.write(chunk)
                        self.position += len(chunk)
                    else:
                        break
                else:
                    time.sleep(0.1)  # Reduce CPU usage while paused

            # Trigger "onEnd" only once when playback ends
            if not self._on_end_triggered:
                if self.position >= len(self.audio_bytes):
                    self._trigger_callback("onEnd")
                    self._on_end_triggered = True
                self.playing.clear()

            # Cleanup after playback ends
            if self.stream_pyaudio and not self.stream_pyaudio.is_stopped():
                self.stream_pyaudio.stop_stream()
                self.stream_pyaudio.close()
            self.isplaying = False
        except OSError:
            # Handle stream-related exceptions gracefully
            self.isplaying = False

    def _auto_resume(self) -> None:
        """Resume audio after timed pause."""
        self.paused = False
        logging.info("Resuming playback after pause")

    def play(self, duration: float | None = None) -> None:
        """Start or resume playback."""
        if self.audio_bytes is None:
            msg = "No audio loaded"
            raise ValueError(msg)

        if not self.isplaying:
            self.isplaying = True
            self.paused = False
            self.position = 0
            self._on_end_triggered = (
                False  # Reset the guard flag at the start of playback
            )
            self.playback_thread = threading.Thread(target=self._playback_loop)
            self.playback_thread.start()
            time.sleep(float(duration or 0))
        elif self.paused:
            self.paused = False

    def pause(self, duration: float | None = None) -> None:
        """
        Pause playback with optional duration.

        Parameters
        ----------
        duration: (Optional[float])
            Number of seconds to pause. If None, pause indefinitely

        """
        self.paused = True

        # Cancel any existing pause timer
        if self.pause_timer:
            self.pause_timer.cancel()
            self.pause_timer = None

        # If duration specified, create timer for auto-resume
        if duration is not None:
            self.pause_timer = threading.Timer(duration, self._auto_resume)
            self.pause_timer.start()
            time.sleep(float(duration or 0))

    def resume(self) -> None:
        """Resume playback."""
        if self.isplaying:
            # Cancel any existing pause timer
            if self.pause_timer:
                self.pause_timer.cancel()
                self.pause_timer = None
            self.paused = False

    def stop(self) -> None:
        """Stop playback."""
        self.isplaying = False
        self.paused = False
        if self.pause_timer:
            self.pause_timer.cancel()
            self.pause_timer = None

        # Stop and close the stream if it exists
        if self.stream_pyaudio:
            try:
                if not self.stream_pyaudio.is_stopped():
                    self.stream_pyaudio.stop_stream()
                self.stream_pyaudio.close()
            except OSError as e:
                logging.info("Stream already closed or encountered an error: %s", e)

            self.stream_pyaudio = None

        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join()
        self.position = 0

    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.stop()

            if self.pyaudio:
                self.pyaudio.terminate()
        except OSError as e:
            logging.warning("Error during cleanup: %s", e)

    def synth_to_file(
        self,
        text: str | SSML,
        output_file: str | Path,
        output_format: str = "wav",
        voice_id: str | None = None,
    ) -> None:
        """
        Synthesizes text to audio and saves it to a file.

        Parameters
        ----------
        text : str | SSML
            The text to synthesize.
        output_file : str | Path
            The path to save the audio file to.
        output_format : str
            The format to save the audio file as. Default is "wav".
        voice_id : str | None, optional
            The ID of the voice to use for synthesis. If None, uses the voice set by set_voice.
        """
        # Convert text to audio bytes
        audio_bytes = self.synth_to_bytes(text, voice_id)

        # Convert to the desired format if needed
        if output_format != "raw":
            # Convert the raw PCM data to the target format
            audio_bytes = self._convert_pcm_to_format(
                np.frombuffer(audio_bytes, dtype=np.int16),
                output_format,
                self.audio_rate,
                self.channels,
            )

        # Save to file
        if isinstance(output_file, str):
            output_file = Path(output_file)

        # Create parent directories if they don't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "wb") as f:
            f.write(audio_bytes)

    def speak(self, text: str | SSML, voice_id: str | None = None) -> None:
        """
        Synthesize text and play it back using sounddevice.

        Parameters
        ----------
        text : str | SSML
            The text to synthesize.
        voice_id : str | None, optional
            The ID of the voice to use for synthesis. If None, uses the voice set by set_voice.
        """
        # Convert text to audio bytes
        audio_bytes = self.synth_to_bytes(text, voice_id)

        # Load the audio into the player
        self.load_audio(audio_bytes)

        # Play the audio
        self.play()

    def synth(
        self,
        text: str | SSML,
        output_file: str | Path,
        output_format: str = "wav",
        voice_id: str | None = None,
    ) -> None:
        """
        Alias for synth_to_file for backward compatibility.

        Parameters
        ----------
        text : str | SSML
            The text to synthesize.
        output_file : str | Path
            The path to save the audio file to.
        output_format : str
            The format to save the audio file as. Default is "wav".
        voice_id : str | None, optional
            The ID of the voice to use for synthesis. If None, uses the voice set by set_voice.
        """
        self.synth_to_file(text, output_file, output_format, voice_id)

    def speak_streamed(self, text: str | SSML, voice_id: str | None = None) -> None:
        """
        Synthesize text to speech and stream it for playback.

        Parameters
        ----------
        text : str | SSML
            The text to synthesize and stream.
        voice_id : str | None, optional
            The ID of the voice to use for synthesis. If None, uses the voice set by set_voice.
        """
        try:
            # Check if the engine supports streaming
            if hasattr(self, "stream_synthesis") and callable(self.stream_synthesis):
                # Get streaming generator
                generator = self.stream_synthesis(text, voice_id)

                # Set up audio stream for playback
                self._setup_audio_stream()

                # Start streaming
                for chunk in generator:
                    if self.stop_flag.is_set():
                        break
                    self._stream_chunk(chunk)

                # Collect all chunks for word timing calculation
                audio_data = b"".join(generator)
            else:
                # Fall back to non-streaming synthesis
                audio_data = self.synth_to_bytes(text, voice_id)

                # For non-streaming engines, create simple word timings
                # Extract plain text from SSML if needed
                if self._is_ssml(str(text)):
                    # Very basic SSML stripping - just get the text content
                    plain_text = re.sub(r"<[^>]+>", "", str(text))
                else:
                    plain_text = str(text)

                words = plain_text.split()
                if words:
                    # Calculate approximate duration
                    duration = self.get_audio_duration()
                    word_duration = duration / len(words)

                    # Create simple evenly-spaced word timings
                    word_timings = []
                    for i, word in enumerate(words):
                        start_time = i * word_duration
                        end_time = (
                            (i + 1) * word_duration if i < len(words) - 1 else duration
                        )
                        word_timings.append((start_time, end_time, word))
                    self.set_timings(word_timings)

                # Play the audio
                self.load_audio(audio_data)
                self.play()
        except Exception:
            logging.exception("Error in streaming synthesis")

    def setup_stream(
        self, samplerate: int = 44100, channels: int = 1, dtype: str | int = "int16"
    ) -> None:
        """
        Set up the audio stream for playback.

        Parameters
        ----------
        samplerate : int
            The sample rate for the audio stream. Defaults to 22050.
        channels : int
            The number of audio channels. Defaults to 1.
        dtype : Union[str, int]
            The data type for audio samples. Defaults to "int16".

        """
        try:
            if self.stream is not None:
                self.stream.close()
            self.stream = sd.OutputStream(
                samplerate=samplerate,
                channels=channels,
                dtype=dtype,
                callback=self.callback,
            )
            self.stream.start()
        except Exception:
            logging.exception("Failed to set up audio stream")
            raise

    def callback(
        self,
        outdata: np.ndarray,
        frames: int,
        time: sd.CallbackTime,
        status: sd.CallbackFlags,
    ) -> None:
        """Handle streamed audio playback as a callback."""
        if status:
            logging.warning("Sounddevice status: %s", status)
        if self.playing:
            # Each frame is 2 bytes for int16, so frames * 2 gives the number of bytes
            end_position = self.position + frames * 2
            data = self.audio_bytes[self.position : end_position]
            if len(data) < frames * 2:
                # Not enough data to fill outdata, zero-pad it
                outdata.fill(0)
                outdata[: len(data) // 2] = np.frombuffer(data, dtype="int16").reshape(
                    -1, 1
                )
            else:
                outdata[:] = np.frombuffer(data, dtype="int16").reshape(outdata.shape)
            self.position = end_position

            if self.position >= len(self.audio_bytes):
                self._trigger_callback("onEnd")
                self.playing.clear()
        else:
            outdata.fill(0)

    def _start_stream(self) -> None:
        """Start the audio stream."""
        with self.stream_lock:
            if self.stream:
                self.stream.start()
            while self.stream.active and self.playing.is_set():
                time.sleep(0.1)
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

    def set_timings(
        self, timings: list[tuple[float, str] | tuple[float, float, str]]
    ) -> None:
        """
        Set the word timings for the synthesized speech.

        Parameters
        ----------
        timings : list[tuple[float, str] | tuple[float, float, str]]
            A list of tuples containing word timings.
            Each tuple can be either (start_time, word) or (start_time, end_time, word).
        """
        logging.debug("Setting timings: %s", timings)
        self.timings = []
        if not timings:
            logging.debug("No timings provided, returning empty list")
            return

        # Calculate total duration for estimating end times if needed
        total_duration = 0
        for timing in timings:
            if len(timing) > 2:  # If we have (start, end, word)
                # Unpack only what we need
                end_time = timing[1]
                total_duration = max(total_duration, end_time)

        # If we don't have end times, estimate the total duration
        if total_duration == 0 and timings:
            # Estimate based on the last start time plus a small buffer
            total_duration = timings[-1][0] + 0.5
            logging.debug("Estimated total duration: %s", total_duration)

        # Process the timings
        for i, timing in enumerate(timings):
            if len(timing) == TIMING_TUPLE_LENGTH_TWO:
                start_time, word = timing
                # Use ternary operator for cleaner code
                end_time = timings[i + 1][0] if i < len(timings) - 1 else total_duration
                self.timings.append((start_time, end_time, word))
                logging.debug("Processed 2-tuple timing: %s", timing)
                logging.debug("Converted to: (%s, %s, %s)", start_time, end_time, word)
            else:
                self.timings.append(timing)
                logging.debug("Added 3-tuple timing: %s", timing)

        logging.debug("Final timings: %s", self.timings)

    def get_timings(self) -> list[tuple[float, float, str]]:
        """Retrieve the word timings for the spoken text."""
        return self.timings

    def get_audio_duration(self) -> float:
        """
        Calculate the duration of the audio.

        Calculate the duration of the audio based
        on the number of samples and sample rate.
        """
        if self.timings:
            return self.timings[-1][1]
        return 0.0

    def on_word_callback(self, word: str, start_time: float, end_time: float) -> None:
        """
        Trigger a callback when a word is spoken during playback.

        :param word: The word being spoken.
        :param start_time: The start time of the word in seconds.
        :param end_time: The end time of the word in seconds.
        """
        logging.info(
            "Word spoken: %s, Start: %.3fs, End: %.3fs",
            word,
            start_time,
            end_time,
        )

    def connect(self, event_name: str, callback: Callable) -> None:
        """Connect a callback function to an event."""
        if event_name in self.callbacks:
            self.callbacks[event_name] = callback

    def _trigger_callback(self, event_name: str, *args: tuple[Any, ...]) -> None:
        """Trigger the specified callback event with optional arguments."""
        if event_name in self.callbacks and self.callbacks[event_name] is not None:
            self.callbacks[event_name](*args)

    def start_playback_with_callbacks(
        self, text: str, callback: Callable | None = None, voice_id: str | None = None
    ) -> None:
        """
        Start playback of the given text with callbacks triggered at each word.

        Parameters
        ----------
        text : str
            The text to be spoken.
        callback : Callable, optional
            A callback function to invoke at each word
            with arguments (word, start, end).
            If None, `self.on_word_callback` is used.
        voice_id : str | None, optional
            The ID of the voice to use for synthesis. If None, uses the voice set by set_voice.
        """
        if callback is None:
            callback = self.on_word_callback

        self.speak_streamed(text, voice_id)
        start_time = time.time()

        try:
            for start, end, word in self.timings:
                delay = max(0, start - (time.time() - start_time))
                timer = threading.Timer(delay, callback, args=(word, start, end))
                timer.start()
                self.timers.append(timer)
        except (ValueError, TypeError):
            logging.exception("Error in start_playback_with_callbacks")

    def finish(self) -> None:
        """Clean up resources and stop the audio stream."""
        try:
            with self.stream_lock:
                if self.stream:
                    self.stream.stop()
                    self.stream.close()
        except Exception:
            logging.exception("Failed to clean up audio resources")
        finally:
            self.stream = None

    def __del__(self) -> None:
        """Clean up resources when the object is deleted."""
        self.finish()

    def get_property(self, property_name: str) -> PropertyType:
        """
        Retrieve the value of a specified property for the TTS engine.

        Parameters
        ----------
        property_name : str
            The name of the property to retrieve.
            Expected values may include "rate", "volume", or "pitch".

        Returns
        -------
        Optional[Any]
            The value of the specified property if it exists; otherwise, returns None.

        """
        return self.properties.get(property_name, None)

    def set_property(self, property_name: str, value: float | str) -> None:
        """
        Set a property for the TTS engine and update its internal state.

        Parameters
        ----------
        property_name : str
            The name of the property to set.
            Expected values are "rate", "volume", or "pitch".
        value : float | str
            The value to assign to the specified property.

        Updates the corresponding internal variable (_rate, _volume, or _pitch)
        based on the property name.

        """
        self.properties[property_name] = value

        if property_name == "rate":
            self._rate = value
        elif property_name == "volume":
            self._volume = value
        elif property_name == "pitch":
            self._pitch = value

    def _is_ssml(self, text: str) -> bool:
        return bool(re.match(r"^\s*<speak>", text, re.IGNORECASE))

    def _convert_to_ssml(self, text: str) -> str:
        """Convert plain text to simple SSML."""
        ssml_parts = [
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">'
        ]
        words = text.split()
        for i, word in enumerate(words):
            ssml_parts.append(f'<mark name="word{i}"/>{word}')
        ssml_parts.append("</speak>")
        return " ".join(ssml_parts)

    def set_output_device(self, device_id: int) -> None:
        """
        Set the default output sound device by its ID.

        :param device_id: The ID of the device to be set as the default output.
        """
        try:
            # Validate the device_id
            if device_id not in [device["index"] for device in sd.query_devices()]:
                msg = f"Invalid device ID: {device_id}"
                raise ValueError(msg)

            sd.default.device = device_id
            logging.info("Output device set to %s", sd.query_devices(device_id)["name"])
        except ValueError:
            logging.exception("Invalid device ID")
        except Exception:
            logging.exception("Failed to set output device")

    def _convert_pcm_to_format(
        self,
        pcm_data: np.ndarray,
        output_format: str,
        samplerate: int,
        channels: int = 1,
    ) -> bytes:
        """
        Convert PCM data to the specified audio format.

        Parameters
        ----------
        pcm_data : np.ndarray
            The PCM audio data to convert.
        output_format : str
            The target audio format (e.g., 'wav', 'mp3', etc.)
        samplerate : int
            The sample rate of the audio data.
        channels : int, optional
            The number of audio channels. Default is 1.

        Returns
        -------
        bytes
            The converted audio data in the specified format.
        """

        # Create a BytesIO object to hold the output
        output_buffer = io.BytesIO()

        # Convert to the desired format
        if output_format.lower() == "wav":
            sf.write(output_buffer, pcm_data, samplerate, format="WAV")
        elif output_format.lower() == "mp3":
            try:
                from pydub import AudioSegment

                # Convert to WAV first
                wav_buffer = io.BytesIO()
                sf.write(wav_buffer, pcm_data, samplerate, format="WAV")
                wav_buffer.seek(0)

                # Then convert WAV to MP3
                audio_segment = AudioSegment.from_wav(wav_buffer)
                audio_segment.export(output_buffer, format="mp3")
            except ImportError:
                logging.error(
                    "pydub is required for MP3 conversion. Please install it with pip"
                )
                raise
        elif output_format.lower() == "ogg":
            sf.write(output_buffer, pcm_data, samplerate, format="OGG")
        elif output_format.lower() == "flac":
            sf.write(output_buffer, pcm_data, samplerate, format="FLAC")
        else:
            # Default to WAV if format not recognized
            logging.warning("Unsupported format: %s. Using WAV instead.", output_format)
            sf.write(output_buffer, pcm_data, samplerate, format="WAV")

        # Get the bytes from the buffer
        output_buffer.seek(0)
        return output_buffer.read()
