# MiniMax TTS Voice Cloning Tool

A Python library for voice cloning and text-to-speech synthesis using the MiniMax API.

## Features

- **Voice Cloning**: Upload reference audio to clone specific voices
- **Text-to-Speech**: Convert text to speech using cloned or built-in voices
- **Synchronous & Async**: Support for both sync and async TTS operations
- **Task Management**: Query task status and retrieve generated audio
- **Multi-Format Config**: Support for .env, JSON, and INI configuration files
- **CLI Support**: Command-line interface for quick testing and scripting

## Requirements

- Python 3.7+
- requests
- python-dotenv (optional, for .env file support)

## Installation

```bash
# Clone or copy the project
git clone <repository-url>
cd minimax-tts

# Install dependencies
pip install requests python-dotenv
```

## Configuration

Set your MiniMax API key. Create a `.env` file in the project directory:

```bash
MINIMAX_API_KEY=your-api-key-here
```

Or set it as an environment variable:

```bash
export MINIMAX_API_KEY="your-api-key-here"
```

## Quick Start

### Basic Voice Cloning

```python
from voice_cloner import VoiceCloner

cloner = VoiceCloner()

# Clone a voice from reference audio
result = cloner.clone_voice(
    voice_id="my_voice",
    audio_path="/path/to/reference_audio.mp3"
)
```

### With Prompt Audio for Enhanced Quality

```python
result = cloner.clone_voice(
    voice_id="my_voice",
    audio_path="/path/to/reference_audio.mp3",
    prompt_audio="/path/to/prompt_audio.mp3",
    prompt_text="Text spoken in the prompt audio"
)
```

### Text-to-Speech with Cloned Voice

```python
# Synchronous TTS (up to 10,000 characters)
audio_url = cloner.text_to_speech(
    text="Hello, this is a test.",
    voice_id="my_voice"
)
```

### Async TTS for Long Text

```python
# Async TTS for longer content
task_id = cloner.text_to_speech_async(
    text="Long text content here...",
    voice_id="my_voice"
)

# Check task status
status = cloner.get_task_status(task_id)
if status.status == "completed":
    audio_url = status.audio_url
```

## Command Line Usage

```bash
# Clone a voice
python voice_cloner.py \
    --voice-id my_voice \
    --audio /path/to/sample.mp3

# Text-to-speech
python voice_cloner.py \
    --voice-id my_voice \
    --text "要转换的文本内容" \
    --output result.mp3
```

## Supported Audio Formats

| Type | Formats | Max Size | Duration |
|------|---------|----------|----------|
| Reference Audio | mp3, m4a, wav | 20MB | 10s - 5min |
| Prompt Audio | mp3, m4a, wav | 20MB | < 8s |

## API Reference

### VoiceCloner

| Method | Description |
|--------|-------------|
| `clone_voice()` | Clone a voice from reference audio |
| `text_to_speech()` | Synchronous TTS conversion |
| `text_to_speech_async()` | Async TTS for long text |
| `get_task_status()` | Query async task status |
| `generate_audio_from_task()` | Get audio from completed task |

### Result Classes

- `VoiceCloneResult`: Contains task_id, status, audio_url
- `MiniMaxAPIError`: Custom exception for API errors

## Documentation

See [USAGE.md](USAGE.md) for detailed documentation, examples, and best practices.

## License

MIT
