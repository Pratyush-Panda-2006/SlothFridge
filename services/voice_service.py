import logging
from typing import Optional
import config

logger = logging.getLogger("sloth_voice")
logging.basicConfig(level=logging.INFO)

# Voice ID for "George" in ElevenLabs default library
GEORGE_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"

eleven = None
if config.ELEVENLABS_API_KEY:
    try:
        from elevenlabs.client import ElevenLabs
        eleven = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        logger.info("ElevenLabs client initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not initialize ElevenLabs client: {e}")
else:
    logger.info("ELEVENLABS_API_KEY not configured. Audio generation will return empty bytes gracefully.")


def stream_sloth_audio(script: str) -> bytes:
    """
    Generates slow, deadpan audio narration using ElevenLabs.
    Returns raw MP3 audio bytes, or empty bytes b"" if API key is missing
    or if an error occurs, without crashing the server.
    """
    if not config.ELEVENLABS_API_KEY:
        logger.info("ELEVENLABS_API_KEY is not set; returning empty audio bytes.")
        return b""

    if not script or not script.strip():
        logger.warning("Empty script passed to stream_sloth_audio.")
        return b""

    try:
        # Re-initialize client if necessary
        global eleven
        if eleven is None:
            from elevenlabs.client import ElevenLabs
            eleven = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

        # Handle various ElevenLabs SDK version interfaces
        if hasattr(eleven, "generate"):
            audio_stream = eleven.generate(
                text=script,
                voice="George",
                model="eleven_turbo_v2_5"
            )
        elif hasattr(eleven, "text_to_speech"):
            audio_stream = eleven.text_to_speech.convert(
                voice_id=GEORGE_VOICE_ID,
                text=script,
                model_id="eleven_turbo_v2_5"
            )
        else:
            from elevenlabs import generate
            audio_stream = generate(
                text=script,
                voice="George",
                model="eleven_turbo_v2_5",
                api_key=config.ELEVENLABS_API_KEY
            )

        # Collect generator chunks into single bytes buffer
        audio_bytes = b"".join(audio_stream)
        return audio_bytes

    except Exception as e:
        logger.error(f"Error during ElevenLabs audio generation: {e}")
        return b""
