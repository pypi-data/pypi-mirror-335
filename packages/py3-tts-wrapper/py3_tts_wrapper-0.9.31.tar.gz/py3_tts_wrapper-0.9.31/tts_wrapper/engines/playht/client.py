import logging
from typing import Any, Optional

import requests


class PlayHTClient:
    """Client for Play.HT TTS API."""

    def __init__(self, credentials=None, api_key=None, user_id=None) -> None:
        """
        Initialize the Play.HT client.

        @param credentials: Tuple of (api_key, user_id)
        @param api_key: API key for Play.HT
        @param user_id: User ID for Play.HT
        """
        if credentials:
            if isinstance(credentials, tuple) and len(credentials) == 2:
                self.api_key, self.user_id = credentials
            else:
                self.api_key = credentials
                self.user_id = user_id
        else:
            self.api_key = api_key
            self.user_id = user_id

        if not self.api_key:
            msg = "API key is required"
            raise ValueError(msg)

        if not self.user_id:
            # Try to get user_id from environment variable
            import os
            self.user_id = os.getenv("PLAYHT_USER_ID")
            if not self.user_id:
                msg = "User ID is required"
                raise ValueError(msg)

        self.base_url = "https://api.play.ht/api/v2"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-USER-ID": self.user_id,
        }
        # Separate headers for synthesis which needs audio/mpeg
        self.synth_headers = {**self.headers, "accept": "audio/mpeg"}

    def synth(self, text: str, options: Optional[dict[str, Any]] = None) -> bytes:
        """Synthesize text to speech."""
        url = "https://api.play.ht/api/v2/tts/stream"

        options = options or {}

        # Default voice with full S3 URL
        default_voice = (
            "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/"
            "female-cs/manifest.json"
        )

        # Base payload with required parameters
        payload = {
            "text": text,
            "voice": options.get("voice", default_voice),
            "output_format": "wav",  # Request WAV instead of MP3
            "voice_engine": options.get("voice_engine", "PlayDialog"),
            "sample_rate": 44100,  # Standard audio rate
        }

        # Optional parameters
        if "quality" in options:
            payload["quality"] = options["quality"]
        if "speed" in options:
            payload["speed"] = float(options["speed"])
        if "sample_rate" in options:
            payload["sample_rate"] = int(options["sample_rate"])

        # Advanced parameters for PlayHT2.0 and Play3.0-mini
        for param in ["emotion", "voice_guidance", "style_guidance", "text_guidance"]:
            if param in options:
                payload[param] = options[param]

        # Set headers based on output format
        headers = {**self.headers}
        if payload["output_format"] == "wav":
            headers["accept"] = "audio/wav"
        else:
            headers["accept"] = "audio/mpeg"

        logging.debug("Sending synthesis request to Play.HT:")
        logging.debug(f"URL: {url}")
        logging.debug(f"Headers: {headers}")
        logging.debug(f"Payload: {payload}")

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            status = response.status_code
            error = response.json() if response.content else {"error": "Unknown error"}
            logging.error(f"Play.HT synthesis failed with status {status}")
            logging.error(f"Response content: {error}")
            response.raise_for_status()

        return response.content

    def get_voices(self) -> list[dict[str, Any]]:
        """
        Get available voices from Play.HT, including both standard and cloned voices.

        @returns: List of standardized voice dictionaries with format:
            {
                "id": str,           # Unique voice ID
                "name": str,         # Display name
                "language_codes": list[str],  # List of supported language codes
                "gender": str,       # "male", "female", or "unknown"
            }
        """
        standardized_voices = []

        # Get standard voices
        url = f"{self.base_url}/voices"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        voices_data = response.json()

        for voice in voices_data:
            standardized_voices.append(
                {
                    "id": voice.get("id"),
                    "name": voice.get("name", "Unknown"),
                    "language_codes": [voice.get("language", "en-US")],
                    "gender": voice.get("gender", "unknown").lower(),
                }
            )

        # Get cloned voices
        url = f"{self.base_url}/cloned-voices"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            cloned_voices_data = response.json()

            for voice in cloned_voices_data:
                standardized_voices.append(
                    {
                        "id": voice.get("id"),
                        "name": f"{voice.get('name', 'Unknown')} (Cloned)",
                        "language_codes": [voice.get("language", "en-US")],
                        "gender": voice.get("gender", "unknown").lower(),
                    }
                )
        except requests.RequestException:
            # If cloned voices request fails, continue with standard voices
            pass

        return standardized_voices

    def check_credentials(self) -> bool:
        """Check if the provided credentials are valid."""
        try:
            self.get_voices()
            return True
        except requests.RequestException:
            return False
