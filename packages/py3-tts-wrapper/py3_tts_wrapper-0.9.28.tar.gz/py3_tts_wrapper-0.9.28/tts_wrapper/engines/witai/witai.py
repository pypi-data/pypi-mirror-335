from typing import Any, Optional

from tts_wrapper.engines.utils import (
    estimate_word_timings,  # Import the timing estimation function
)
from tts_wrapper.tts import AbstractTTS

from . import WitAiClient, WitAiSSML


class WitAiTTS(AbstractTTS):
    def __init__(
        self,
        client: WitAiClient,
        voice: Optional[str] = "Rebecca",
        lang: Optional[str] = "en-US",
    ) -> None:
        super().__init__()
        self._client = client
        self._voice = voice
        self._lang = lang
        self.audio_rate = 24000  # Adjusted based on Wit.ai's 24kHz sample rate for PCM

    def synth_to_bytes(self, text: str, voice_id: Optional[str] = None) -> bytes:
        if not self._is_ssml(str(text)):
            text = self.ssml.add(str(text))
        word_timings = estimate_word_timings(str(text))
        self.set_timings(word_timings)

        # Use voice_id if provided, otherwise use the default voice
        voice_to_use = voice_id or self._voice

        generated_audio = self._client.synth(str(text), voice_to_use)

        if generated_audio[:4] == b"RIFF":
            generated_audio = self._strip_wav_header(generated_audio)

        return generated_audio

    @property
    def ssml(self) -> WitAiSSML:
        """Returns an instance of the WitSSML class for constructing SSML strings."""
        return WitAiSSML()

    def get_voices(self) -> list[dict[str, Any]]:
        """Retrieves a list of available voices from the Wit.ai service."""
        return self._client.get_voices()

    def set_voice(self, voice_id: str, lang_id: str) -> None:
        """Sets the voice for the TTS engine."""
        super().set_voice(voice_id)
        self._voice = voice_id
        self._lang = lang_id

    def construct_prosody_tag(self, text: str) -> str:
        pass
