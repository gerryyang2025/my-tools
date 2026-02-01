# MiniMax TTS Voice Cloning Tool - Usage Guide

## Overview

MiniMax TTS Voice Cloning Tool is a Python library for quickly cloning voices and generating speech. This tool is based on the MiniMax platform's text-to-speech API, supporting users to upload reference audio to clone specific voices and use those voices for text-to-speech synthesis.

## Complete Workflow

The voice cloning process involves the following steps:

### Step 1: Upload Reference Audio

Call the file upload endpoint to upload the audio file to be cloned and obtain the `file_id`. This audio serves as the primary reference for voice cloning.

### Step 2: Upload Prompt Audio (Optional)

If you need to provide a prompt audio to enhance cloning quality, upload the prompt audio file and obtain its `file_id`. This will be used in the `clone_prompt.prompt_audio` field.

### Step 3: Call Voice Clone API

Use the obtained `file_id` along with your custom `voice_id` as input parameters to clone the voice.

### Step 4: Use Cloned Voice

With the generated `voice_id`, you can call speech generation APIs for actual text-to-speech synthesis.

## Environment Setup

### 1. Obtain API Key

Before using this tool, you need to obtain an API key from the MiniMax platform. Please visit the MiniMax Developer Platform (https://platform.minimaxi.com/) to register an account and create an API key.

### 2. Set Environment Variable

It is recommended to set the API key as an environment variable to avoid hardcoding keys in your code and improve security. Run the following commands in your terminal:

```bash
# macOS/Linux
export MINIMAX_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:MINIMAX_API_KEY="your-api-key-here"
```

Alternatively, you can pass the API key directly in your code.

## Installation and Import

Copy the `voice_cloner.py` file to your project directory and import it as follows:

```python
from voice_cloner import VoiceCloner
```

## Quick Start

### Basic Usage

Here is the simplest way to use this tool for voice cloning:

```python
from voice_cloner import VoiceCloner

# Initialize the cloner (automatically reads API key from environment variable)
cloner = VoiceCloner()

# Perform voice cloning
result = cloner.clone_voice(
    voice_id="my_custom_voice",  # Custom voice ID
    audio_path="/path/to/reference_audio.mp3",  # Reference audio path
)
```

### Full Parameter Example

If you need more granular control, you can provide additional parameters:

```python
from voice_cloner import VoiceCloner

cloner = VoiceCloner(api_key="your-api-key-here")

result = cloner.clone_voice(
    voice_id="tianjin_dialect_voice",  # Voice ID for identification and reuse
    audio_path="/path/to/clone_input.mp3",  # Reference audio for cloning
    prompt_audio="/path/to/clone_prompt.mp3",  # Prompt audio (optional)
    prompt_text="后来认为啊，是有人抓这鸡，可是抓鸡的地方呢没人听过鸡叫。",  # Prompt text (optional)
    text="大兄弟，听您口音不是本地人吧，头回来天津卫，啊，待会您可甭跟着导航走，那玩意儿净给您往大马路上绕。",  # Text to convert (optional)
    model="speech-2.8-hd"  # Model to use
)
```

### Command Line Usage

This tool also supports command line invocation, suitable for quick testing and script integration:

```bash
python voice_cloner.py \
    --voice-id my_voice \
    --audio /path/to/sample.mp3 \
    --prompt-audio /path/to/prompt.mp3 \
    --prompt-text "提示文本内容" \
    --text "要转换的文本内容"
```

#### Step-by-Step Workflow Commands

```bash
# Step 1: Upload reference audio and get file_id
python voice_cloner.py --step 1 --audio reference.m4a

# Step 2: Upload prompt audio for enhanced quality (optional)
python voice_cloner.py --step 2 --prompt-audio prompt.m4a --file-id <file_id_from_step1>

# Step 3: Complete voice cloning (basic)
python voice_cloner.py --step 3 --voice-id my_voice --file-id <file_id>

# Step 3: Complete voice cloning (with prompt audio)
python voice_cloner.py --step 3 --voice-id my_voice --file-id <file_id> \
    --prompt-file-id <prompt_file_id> --prompt-text-file prompt_text.txt \
    --text-file speech_text.txt
```

#### File Management Commands

```bash
# List all uploaded files
python voice_cloner.py --list-files

# List only voice clone files
python voice_cloner.py --list-files --purpose voice_clone

# List only prompt audio files
python voice_cloner.py --list-files -u prompt_audio

# Get detailed info about a specific file
python voice_cloner.py --get-file-info 123456789

# Delete a specific file (will prompt for confirmation)
python voice_cloner.py --delete-file 123456789

# Output in JSON format
python voice_cloner.py --list-files --json
python voice_cloner.py --get-file-info 123456789 --json
```

## Detailed Workflow Examples

### 1. Upload Reference Audio

**Python Example:**

```python
"""
This example demonstrates how to obtain the file_id for reference audio.
Note: Ensure the environment variable MINIMAX_API_KEY is set first.
"""
import requests
import os

api_key = os.getenv("MINIMAX_API_KEY")
url = "https://api.minimaxi.com/v1/files/upload"

payload = {"purpose": "voice_clone"}
files = [
    ("file", ("clone_input.mp3", open("/path/to/clone_input.mp3", "rb")))
]
headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.post(url, headers=headers, data=payload, files=files)
response.raise_for_status()
file_id = response.json().get("file", {}).get("file_id")
print(file_id)
```

**cURL Example:**

```bash
curl --location 'https://api.minimaxi.com/v1/files/upload' \
  --header 'Authorization: Bearer ${MINIMAX_API_KEY}' \
  --form 'purpose="voice_clone"' \
  --form 'file=@"/path/to/clone_input.mp3"'
```

### 2. Upload Prompt Audio

**Python Example:**

```python
"""
This example demonstrates how to obtain the file_id for prompt audio.
Note: Ensure the environment variable MINIMAX_API_KEY is set first.
"""
import requests
import os

api_key = os.getenv("MINIMAX_API_KEY")
url = "https://api.minimaxi.com/v1/files/upload"

payload = {"purpose": "prompt_audio"}
files = [
    ("file", ("clone_prompt.mp3", open("/path/to/clone_prompt.mp3", "rb")))
]
headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.post(url, headers=headers, data=payload, files=files)
response.raise_for_status()
prompt_file_id = response.json().get("file", {}).get("file_id")
print(prompt_file_id)
```

**cURL Example:**

```bash
curl --location 'https://api.minimaxi.com/v1/files/upload' \
  --header 'Authorization: Bearer ${MINIMAX_API_KEY}' \
  --form 'purpose="prompt_audio"' \
  --form 'file=@"/path/to/clone_prompt.mp3"'
```

### 3. Perform Voice Cloning

**Python Example:**

```python
"""
This example demonstrates voice cloning.
Note: Set the environment variable MINIMAX_API_KEY,
and replace "<voice_id>", <file_id_of_cloned_voice>, <file_id_of_prompt_audio> with actual values.
"""
import requests
import json
import os

api_key = os.getenv("MINIMAX_API_KEY")
url = "https://api.minimaxi.com/v1/voice_clone"

clone_payload = {
    "file_id": file_id,
    "voice_id": "<your_custom_voice_id>",
    "clone_prompt": {
        "prompt_audio": prompt_file_id,
        "prompt_text": "后来认为啊，是有人抓这鸡，可是抓鸡的地方呢没人听过鸡叫。"
    },
    "text": "大兄弟，听您口音不是本地人吧，头回来天津卫，啊，待会您可甭跟着导航走，那玩意儿净给您往大马路上绕。",
    "model": "speech-2.8-hd"
}
clone_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=payload)
response.raise_for_status()
print(response.text)
```

**cURL Example:**

```bash
curl --location 'https://api.minimaxi.com/v1/voice_clone' \
  --header 'Authorization: Bearer ${MINIMAX_API_KEY}' \
  --header 'Content-Type: application/json' \
  --data '{
    "file_id": <file_id_of_cloned_voice>,
    "voice_id": "<your_custom_voice_id>",
    "clone_prompt": {
      "prompt_audio": <file_id_of_prompt_audio>,
      "prompt_text": "后来认为啊，是有人抓这鸡，可是抓鸡的地方呢没人听过鸡叫。"
    },
    "text": "大兄弟，听您口音不是本地人吧，头回来天津卫，啊，待会您可甭跟着导航走，那玩意儿净给您往大马路上绕。",
    "model": "speech-2.8-hd"
  }'
```

### 4. Complete Integration Example

This example demonstrates the entire workflow from upload to cloning:

```python
"""
This example demonstrates quick voice cloning to obtain preview audio.
Note: Ensure the environment variable MINIMAX_API_KEY is set,
and replace "<your_custom_voice_id>" with your defined voice ID.
"""
import json
import requests
import os

api_key = os.getenv("MINIMAX_API_KEY")
upload_url = "https://api.minimaxi.com/v1/files/upload"
clone_url = "https://api.minimaxi.com/v1/voice_clone"
headers = {"Authorization": f"Bearer {api_key}"}

# 1. Upload reference audio
with open("/path/to/clone_input.mp3", "rb") as f:
    files = {"file": ("clone_input.mp3", f)}
    data = {"purpose": "voice_clone"}
    response = requests.post(upload_url, headers=headers, data=data, files=files)
file_id = response.json()["file"]["file_id"]
print(f"File ID of the cloned audio: {file_id}")

# 2. Upload prompt audio (optional)
with open("/path/to/clone_prompt.mp3", "rb") as f:
    files = {"file": ("clone_prompt.mp3", f)}
    data = {"purpose": "prompt_audio"}
    response = requests.post(upload_url, headers=headers, data=data, files=files)
prompt_file_id = response.json()["file"]["file_id"]
print(f"File ID of the prompt audio: {prompt_file_id}")

# 3. Perform voice cloning
clone_payload = {
    "file_id": file_id,
    "voice_id": "<your_custom_voice_id>",
    "clone_prompt": {
        "prompt_audio": prompt_file_id,
        "prompt_text": "后来认为啊，是有人抓这鸡，可是抓鸡的地方呢没人听过鸡叫。"
    },
    "text": "大兄弟，听您口音不是本地人吧，头回来天津卫，啊，待会您可甭跟着导航走，那玩意儿净给您往大马路上绕。",
    "model": "speech-2.8-hd"
}
clone_headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
response = requests.post(clone_url, headers=clone_headers, json=clone_payload)
print(response.text)
```

## Audio File Requirements

### Reference Audio (audio_path)

The reference audio used for voice cloning must meet the following specifications:

- **Format**: mp3, m4a, wav
- **Duration**: Minimum 10 seconds, maximum 5 minutes
- **Size**: Maximum 20MB
- **Quality**: Clear, no noise, moderate volume
- **Content**: Single-person reading in Mandarin or the target language

### Prompt Audio (prompt_audio, optional)

If you need more precise cloning results, you can provide additional prompt audio with the following specifications:

- **Format**: mp3, m4a, wav
- **Duration**: Less than 8 seconds
- **Size**: Maximum 20MB
- **Purpose**: Provide more detailed voice characteristic references
- **Requirements**: Similar recording conditions to the reference audio

#### Important: prompt_text Must Match prompt_audio

When using `prompt_audio`, you **must** provide the corresponding `prompt_text`. The text must **exactly match** what is spoken in the prompt audio.

**Why this is required:**

The `prompt_text` provides a transcription of the `prompt_audio`, allowing the API to:
- Align audio signals with text content
- Accurately extract voice characteristics
- Learn pronunciation patterns, intonation, and rhythm
- Generate more natural cloned voice output

**Example:**

If your `prompt_audio` contains:
```
后来认为啊，是有人抓这鸡，可是抓鸡的地方呢没人听过鸡叫。
```

Then your `prompt_text` must be exactly the same:
```python
prompt_text="后来认为啊，是有人抓这鸡，可是抓鸡的地方呢没人听过鸡叫。"
```

**Consequences of mismatch:**

| Scenario | Result |
|----------|--------|
| prompt_text matches prompt_audio | High-quality voice cloning |
| prompt_text does not match | Poor alignment, reduced quality |

**Recommendation:** Use the same audio clip for both `prompt_audio` and ensure `prompt_text` is an accurate transcription of what is spoken.

## Successful Conversion Example

This section documents a real successful voice cloning and text-to-speech conversion.

### Input Text

The following text was successfully converted using the cloned voice:

**Speech Text (speech_text.txt):**
```
祥子每天放胆地跑，对于什么时候出车也不大考虑，兵荒马乱的时候，他照样出去拉车。有一天，为了多赚一点儿钱，他冒险把车拉到清华，途中连车带人被十来个兵捉了去。这些日子，他随着兵们跑。每天得扛着或推着兵们的东西，还得去挑水烧火喂牲口，汗从头上一直流到脚后跟，他恨透了那些乱兵。他自食其力的理想第一次破灭了。
```

**Prompt Text (prompt_text.txt):**
```
《骆驼祥子》主要内容及章节概括。
```

### Conversion Result

The voice cloning and text-to-speech conversion was completed successfully, producing natural-sounding audio output with the cloned voice characteristics.

### Key Observations from Successful Conversion

- The cloned voice successfully replicated the tone and characteristics of the reference audio
- Long-form text (several hundred characters) was processed without issues
- The voice maintained consistent quality throughout the generated audio
- Punctuation and natural pauses were handled appropriately

### Recommendations for Best Results

Based on successful conversions:

1. **Text Length**: Works well with paragraphs of several hundred characters
2. **Content Type**: Literary Chinese text with proper punctuation converts smoothly
3. **Voice Stability**: Cloned voices maintain consistency across different text lengths
4. **Audio Quality**: Ensure reference audio is clear with minimal background noise

## Audio Examples

After completing the voice cloning process, you can preview the results:

**Reference Audio Sample:**
Audio playback available at: https://filecdn.minimax.chat/public/9a226362-dddb-42bc-99fd-e8b426539ca7.wav

**Prompt Audio Sample:**
Audio playback available at: https://filecdn.minimax.chat/public/846b954e-772f-4e26-a598-eac0bce1b491.wav

**Result Audio Sample:**
Audio playback available at: https://filecdn.minimax.chat/public/90f581ac-cf37-4866-be54-711689c14cf9.mp3

## Using Cloned Voices

After obtaining the `voice_id` from the cloning process, you can use it for various speech synthesis operations:

### Synchronous Speech Synthesis

For short text-to-speech conversions (up to 10,000 characters), use the synchronous speech synthesis API.

### Asynchronous Long Text Speech Synthesis

For longer text content, use the asynchronous speech synthesis API designed for large-scale text processing.

## Error Handling

This tool includes comprehensive error handling for common exception scenarios:

### API Key Error

```python
try:
    cloner = VoiceCloner(api_key="invalid-key")
except ValueError as e:
    print(f"Configuration error: {e}")
```

### File Not Found

```python
try:
    result = cloner.clone_voice(
        voice_id="test",
        audio_path="/nonexistent/file.mp3"
    )
except FileNotFoundError as e:
    print(f"File error: {e}")
```

### API Call Failed

```python
from voice_cloner import MiniMaxAPIError

try:
    result = cloner.clone_voice(...)
except MiniMaxAPIError as e:
    print(f"API error: {e.message}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
```

## API Reference

### VoiceCloner Class

#### `__init__(api_key=None)`

Initialize the voice cloner.

**Parameters:**
- `api_key` (str, optional): API key. If not provided, reads from the environment variable `MINIMAX_API_KEY`.

**Exceptions:**
- `ValueError`: Raised when no API key is provided and the environment variable is not set.

#### `clone_voice(voice_id, audio_path, prompt_audio=None, prompt_text=None, text=None, model='speech-2.8-hd')`

Perform voice cloning.

**Parameters:**
- `voice_id` (str): Custom voice ID used to identify the voice.
- `audio_path` (str): Path to the reference audio file for cloning.
- `prompt_audio` (str, optional): Path to the prompt audio file.
- `prompt_text` (str, optional): Text content corresponding to the prompt audio.
- `text` (str, optional): Text content to convert to speech.
- `model` (str, optional): Model name to use, defaults to `"speech-2.8-hd"`.

**Returns:**
- `VoiceCloneResult`: Result object containing task ID and status.

**Exceptions:**
- `ValueError`: Raised when required parameters are empty or validation fails.
- `MiniMaxAPIError`: Raised when API call fails.
- `FileNotFoundError`: Raised when audio file does not exist.

### VoiceCloneResult Data Class

Result object for cloning operations, containing the following attributes:

- `task_id` (str): Task ID used to query task status.
- `status` (str): Task status, such as `"processing"`, `"completed"`, etc.
- `audio_url` (str, optional): Generated audio URL (after task completion).
- `error_message` (str, optional): Error message (when task fails).

### File Management Methods

#### `list_files(purpose=None)`

List all uploaded files in your account.

**Parameters:**
- `purpose` (str, optional): Filter files by type. Available options:
  - `"voice_clone"`: Reference audio files for voice cloning
  - `"prompt_audio"`: Prompt audio files
  - `"t2a_async_input"`: Async T2A input files
  - If not provided, returns all files

**Returns:**
- `list`: List of files, each containing:
  - `file_id` (str): Unique file identifier
  - `filename` (str): Original filename
  - `bytes` (int): File size in bytes
  - `created_at` (int): Unix timestamp of creation time
  - `purpose` (str): File purpose type

**Example:**
```python
# List all files
all_files = cloner.list_files()
for f in all_files:
    print(f"ID: {f['file_id']}, Name: {f['filename']}")

# List only voice clone files
clone_files = cloner.list_files(purpose="voice_clone")

# List only prompt audio files
prompt_files = cloner.list_files(purpose="prompt_audio")
```

#### `get_file_info(file_id)`

Get detailed information about a specific file.

**Parameters:**
- `file_id` (str): The unique file identifier

**Returns:**
- `dict`: File details including:
  - `file_id` (str): File unique identifier
  - `filename` (str): Original filename
  - `bytes` (int): File size in bytes
  - `created_at` (int): Unix timestamp of creation time
  - `purpose` (str): File purpose type
  - `download_url` (str, optional): File download URL (if available)

**Example:**
```python
file_info = cloner.get_file_info("123456789")
print(f"Filename: {file_info['filename']}")
print(f"Size: {file_info['bytes'] / 1024:.2f} KB")
print(f"Created: {file_info['created_at']}")
```

#### `delete_file(file_id)`

Delete an uploaded file.

**Parameters:**
- `file_id` (str): The unique file identifier to delete

**Returns:**
- `bool`: `True` if deletion was successful, `False` otherwise

**Example:**
```python
success = cloner.delete_file("123456789")
if success:
    print("File deleted successfully")
else:
    print("Failed to delete file")
```

**Warning:** This action cannot be undone. Once deleted, the file cannot be recovered.

## Best Practices

### 1. API Key Management

It is recommended to use environment variables or a secure key management service to store API keys, avoiding hardcoding in your code. You can manage sensitive information by setting up `.env` files with the `python-dotenv` library.

### 2. Error Retry Mechanism

For temporary failures caused by network instability, you can implement retry logic:

```python
import time
from voice_cloner import VoiceCloner, MiniMaxAPIError

def clone_with_retry(cloner, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return cloner.clone_voice(**kwargs)
        except MiniMaxAPIError as e:
            if attempt < max_retries - 1:
                print(f"Retrying attempt {attempt + 1}...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

### 3. Asynchronous Processing

For scenarios requiring large numbers of requests, you can use `asyncio` to implement asynchronous calls for improved efficiency.

### 4. Result Persistence

It is recommended to persist task IDs and related parameters for easier subsequent queries and tracking.

### 5. Quality Optimization

For better cloning results:
- Use high-quality reference audio with minimal background noise
- Ensure consistent recording conditions across reference and prompt audio
- Provide prompt audio that clearly demonstrates the desired voice characteristics
- Use clear and natural speech content for both reference and prompt audio

## FAQ

### Q: How long does voice cloning take?

Voice cloning typically takes from a few seconds to tens of seconds, depending on audio length and server load.

### Q: Can cloned voices be reused?

Yes. Each voice has a unique `voice_id`, which you can use in subsequent requests to generate speech with the same voice.

### Q: Why is the cloning quality not ideal?

Possible reasons include: low quality reference audio, excessive ambient noise, insufficient audio duration, etc. It is recommended to use clear, quiet recordings as reference.

### Q: Does it support batch cloning?

The current version does not support batch operations. You can process multiple requests in a loop by calling the `clone_voice` method multiple times.

### Q: What audio formats are supported?

Both reference audio and prompt audio support MP3, M4A, and WAV formats.

### Q: What are the audio size limits?

Audio files must not exceed 20MB in size.

### Q: What is the maximum duration for reference audio?

Reference audio should be between 10 seconds and 5 minutes. Audio outside this range may result in reduced cloning quality.

### Q: How long can the prompt audio be?

Prompt audio should be less than 8 seconds for optimal results.

### Q: Do uploaded files expire?

There is no explicit documentation stating that uploaded files expire. Files uploaded via the file management API should remain in your account until you manually delete them. You can use the `list_files()` method to view all your uploaded files and `delete_file()` to remove files you no longer need.

### Q: What is the difference between file_id and voice_id?

- `file_id`: A unique identifier for an uploaded audio file. It is obtained by uploading audio files (reference audio or prompt audio) and remains valid until the file is deleted.
- `voice_id`: A custom identifier you create for a cloned voice profile. Once you clone a voice using a `file_id`, you receive a `voice_id` that can be used for text-to-speech synthesis. Note that cloned voices are temporary and expire after 168 hours (7 days) unless used for synthesis.

### Q: Can I reuse a file_id for multiple voice cloning operations?

Yes, once you upload an audio file and obtain its `file_id`, you can use that `file_id` to clone voices multiple times. The same reference audio can be used to create different `voice_id` values.

### Q: How do I check what files I have uploaded?

Use the `--list-files` command to view all uploaded files:

```bash
# List all files
python voice_cloner.py --list-files

# List only voice clone files
python voice_cloner.py --list-files --purpose voice_clone

# Output in JSON format
python voice_cloner.py --list-files --json
```

This will show you all uploaded files including their `file_id`, filename, size, purpose, and creation time.

## References

- Complete Documentation Index: https://platform.minimaxi.com/docs/llms.txt
- Voice Cloning Guide: https://platform.minimaxi.com/docs/guides/speech-voice-clone
- API Documentation: https://platform.minimaxi.com/docs/api-reference
- Voice Clone API Reference: https://platform.minimaxi.com/docs/api-reference/voice-cloning-clone
- Synchronous Speech Synthesis: https://platform.minimaxi.com/docs/guides/speech-t2a-websocket
- Pricing Information: https://platform.minimaxi.com/docs/guides/pricing-payg#speech
- Rate Limits: https://platform.minimaxi.com/docs/guides/rate-limits

## License

This tool is open source under the MIT License.
