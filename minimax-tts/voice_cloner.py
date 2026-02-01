#!/usr/bin/env python3
"""
MiniMax TTS Voice Cloning Tool

This module provides voice cloning and text-to-speech functionality.

Usage:
1. Set the environment variable MINIMAX_API_KEY
2. Create a .env file with MINIMAX_API_KEY=your-key
3. Import and use the VoiceCloner class

Example:
    from voice_cloner import VoiceCloner
    
    cloner = VoiceCloner(api_key="your-api-key")
    # Clone voice
    cloner.clone_voice(
        voice_id="my_voice",
        audio_path="/path/to/sample.m4a",
        prompt_audio="/path/to/prompt.m4a",
        prompt_text="Reference text content"
    )
"""

# Suppress SSL compatibility warnings on older macOS versions
# This must be set before importing urllib3 or requests
import os
os.environ['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'

import warnings
warnings.filterwarnings("ignore", message=".*urllib3.*")

import json
import requests
from typing import Optional
from dataclasses import dataclass


def load_api_key_from_config(config_path: Optional[str] = None) -> Optional[str]:
    """
    Load API key from local config file.
    
    Supported config file formats:
    - .env file with: MINIMAX_API_KEY=your-key
    - JSON file with: {"MINIMAX_API_KEY": "your-key"}
    - INI file with: [default] MINIMAX_API_KEY=your-key
    
    Search order:
    1. Custom config_path (if provided)
    2. .env in current directory
    3. .minimax.conf in current directory
    4. ~/.minimax.conf in home directory
    
    Args:
        config_path: Custom path to config file (optional)
        
    Returns:
        API key if found, None otherwise
    """
    # Build search paths
    search_paths = []
    
    if config_path:
        search_paths.append(config_path)
    
    search_paths.extend([
        ".env",
        ".minimax.conf",
        os.path.expanduser("~/.minimax.conf"),
    ])
    
    for path in search_paths:
        if not os.path.exists(path):
            continue
        
        api_key = _parse_config_file(path)
        if api_key:
            return api_key
    
    return None


def _parse_config_file(config_path: str) -> Optional[str]:
    """
    Parse a config file and extract API key.
    
    Args:
        config_path: Path to the config file
        
    Returns:
        API key if found, None otherwise
    """
    if not os.path.exists(config_path):
        return None
    
    try:
        # Try .env format (KEY=VALUE)
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                
                # Parse KEY=VALUE format
                if "=" in line:
                    key, value = line.split("=", 1)
                    if key.strip() == "MINIMAX_API_KEY":
                        return value.strip()
        
        # Try JSON format
        with open(config_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if "MINIMAX_API_KEY" in data:
                    return data["MINIMAX_API_KEY"]
            except json.JSONDecodeError:
                pass
        
        # Try INI format
        with open(config_path, "r", encoding="utf-8") as f:
            try:
                import configparser
                config = configparser.ConfigParser()
                config.read_string(f.read())
                if config.has_option("default", "MINIMAX_API_KEY"):
                    return config.get("default", "MINIMAX_API_KEY")
                if config.has_option("minimax", "MINIMAX_API_KEY"):
                    return config.get("minimax", "MINIMAX_API_KEY")
            except Exception:
                pass
                
    except Exception:
        pass
    
    return None


@dataclass
class VoiceCloneResult:
    """Voice cloning result"""
    task_id: str
    status: str
    audio_url: Optional[str] = None
    error_message: Optional[str] = None


class MiniMaxAPIError(Exception):
    """MiniMax API Error"""
    def __init__(self, message: str, status_code: int = None, response: str = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class VoiceCloner:
    """Voice Cloner"""
    
    BASE_URL = "https://api.minimaxi.com/v1"
    
    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the voice cloner
        
        Priority of API key sources:
        1. api_key parameter (highest priority)
        2. Environment variable MINIMAX_API_KEY
        3. Config file (.env, .minimax.conf, or custom path)
        
        Args:
            api_key: MiniMax API key, reads from environment variable or config if not provided
            config_path: Path to config file (default: searches in .env, .minimax.conf, ~/.minimax.conf)
        """
        # Priority 1: Direct parameter
        if api_key:
            self.api_key = api_key
        else:
            # Priority 2: Environment variable
            self.api_key = os.getenv("MINIMAX_API_KEY")
            
            # Priority 3: Config file
            if not self.api_key:
                if config_path and os.path.exists(config_path):
                    self.api_key = self._load_key_from_config_file(config_path)
                else:
                    self.api_key = load_api_key_from_config()
        
        if not self.api_key:
            raise ValueError(
                "API key not set. Please either:\n"
                "  1. Set the environment variable: export MINIMAX_API_KEY='your-key'\n"
                "  2. Create a .env file in the project directory with: MINIMAX_API_KEY=your-key\n"
                "  3. Pass api_key parameter: VoiceCloner(api_key='your-key')"
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _load_key_from_config_file(self, config_path: str) -> Optional[str]:
        """
        Load API key from a specific config file.
        
        Args:
            config_path: Path to the config file
            
        Returns:
            API key if found, None otherwise
        """
        return _parse_config_file(config_path)
    
    def _validate_audio_file(self, audio_path: str, purpose: str = "voice_clone") -> None:
        """
        Validate audio file format, size, and duration requirements.
        
        Requirements:
        - Reference audio (voice_clone): mp3/m4a/wav, 10s-5min, max 20MB
        - Prompt audio (prompt_audio): mp3/m4a/wav, <8s, max 20MB
        
        Args:
            audio_path: Path to the audio file
            purpose: Purpose of the audio (voice_clone or prompt_audio)
            
        Raises:
            ValueError: If validation fails
        """
        import os
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Get file size
        file_size = os.path.getsize(audio_path)
        max_size = 20 * 1024 * 1024  # 20MB
        
        if file_size > max_size:
            raise ValueError(
                f"Audio file size ({file_size / (1024 * 1024):.2f}MB) exceeds maximum limit of 20MB"
            )
        
        # Check file extension
        allowed_formats = {"mp3", "m4a", "wav"}
        file_ext = audio_path.lower().split(".")[-1] if "." in audio_path else ""
        
        if file_ext not in allowed_formats:
            raise ValueError(
                f"Unsupported audio format: .{file_ext}. "
                f"Supported formats: {', '.join(allowed_formats)}"
            )
    
    def _do_upload(self, audio_path: str, purpose: str) -> str:
        """
        Internal method to upload audio file and get file_id.
        
        Args:
            audio_path: Path to the audio file
            purpose: Purpose (voice_clone or prompt_audio)
            
        Returns:
            file_id: The uploaded file ID
            
        Raises:
            MiniMaxAPIError: Raised when upload fails
        """
        upload_url = f"{self.BASE_URL}/files/upload"
        
        with open(audio_path, "rb") as audio_file:
            files = {"file": (os.path.basename(audio_path), audio_file)}
            data = {"purpose": purpose}
            
            response = self.session.post(upload_url, data=data, files=files)
            
            if not response.ok:
                raise MiniMaxAPIError(
                    f"File upload failed: {response.text}",
                    response.status_code,
                    response.text
                )
            
            result = response.json()
            if "file" not in result or "file_id" not in result["file"]:
                raise MiniMaxAPIError(
                    f"Upload response format error: {response.text}",
                    response.status_code,
                    response.text
                )
            
            return result["file"]["file_id"]
    
    # ==================== Public Methods for Step-by-Step Workflow ====================
    
    def upload_clone_audio(self, audio_path: str) -> str:
        """
        Step 1: Upload reference audio for voice cloning.
        
        This is the first step in the voice cloning workflow. Upload your
        reference audio file and get a file_id for the cloning process.
        
        Requirements:
        - Format: mp3, m4a, wav
        - Duration: 10 seconds to 5 minutes
        - Size: Maximum 20MB
        
        Args:
            audio_path: Path to the reference audio file
            
        Returns:
            file_id: The uploaded file ID for cloning
            
        Raises:
            ValueError: If audio file validation fails
            MiniMaxAPIError: If upload fails
            
        Example:
            cloner = VoiceCloner()
            file_id = cloner.upload_clone_audio("/path/to/reference.m4a")
            print(f"Reference audio uploaded, file_id: {file_id}")
        """
        # Validate audio file
        self._validate_audio_file(audio_path, purpose="voice_clone")
        
        # Upload and get file_id
        file_id = self._do_upload(audio_path, purpose="voice_clone")
        
        return file_id
    
    def upload_prompt_audio(self, audio_path: str) -> str:
        """
        Step 2: Upload prompt audio for enhanced cloning quality (optional).
        
        Upload an additional prompt audio file to enhance the voice cloning
        quality. This is optional but recommended for better results.
        
        Requirements:
        - Format: mp3, m4a, wav
        - Duration: Less than 8 seconds
        - Size: Maximum 20MB
        
        Args:
            audio_path: Path to the prompt audio file
            
        Returns:
            file_id: The uploaded file ID for prompt audio
            
        Raises:
            ValueError: If audio file validation fails
            MiniMaxAPIError: If upload fails
            
        Example:
            cloner = VoiceCloner()
            prompt_file_id = cloner.upload_prompt_audio("/path/to/prompt.m4a")
            print(f"Prompt audio uploaded, file_id: {prompt_file_id}")
        """
        # Validate audio file
        self._validate_audio_file(audio_path, purpose="prompt_audio")
        
        # Upload and get file_id
        file_id = self._do_upload(audio_path, purpose="prompt_audio")
        
        return file_id
    
    def clone_voice(
        self,
        voice_id: str,
        audio_path: str,
        prompt_audio: Optional[str] = None,
        prompt_text: Optional[str] = None,
        text: Optional[str] = None,
        model: str = "speech-2.8-hd"
    ) -> VoiceCloneResult:
        """
        Clone voice and generate speech.
        
        This method performs the complete voice cloning workflow:
        1. Uploads reference audio (step 1)
        2. Uploads prompt audio if provided (step 2)
        3. Calls voice clone API (step 3)
        
        For step-by-step control, use the individual methods:
            file_id = cloner.upload_clone_audio(audio_path)
            prompt_file_id = cloner.upload_prompt_audio(prompt_audio)  # optional
            result = cloner.clone_voice(voice_id=voice_id, file_id=file_id, ...)
        
        Requirements:
        - Reference audio: mp3/m4a/wav, 10s-5min, max 20MB
        - Prompt audio (optional): mp3/m4a/wav, <8s, max 20MB
        
        Args:
            voice_id: Custom voice ID to identify this cloned voice
            audio_path: Path to the reference audio file for cloning
            prompt_audio: Path to the prompt audio file (optional)
            prompt_text: Text content corresponding to the prompt audio
            text: Text content to convert to speech (optional)
            model: Model name to use (default: speech-2.8-hd)
            
        Returns:
            VoiceCloneResult: The cloning result with task_id and status
            
        Raises:
            MiniMaxAPIError: Raised when API call fails
            ValueError: Raised when parameter validation fails
            
        Example:
            cloner = VoiceCloner()
            result = cloner.clone_voice(
                voice_id="my_voice",
                audio_path="/path/to/reference.m4a",
                prompt_audio="/path/to/prompt.m4a",
                prompt_text="Prompt text here",
                text="Text to synthesize"
            )
        """
        # Parameter validation
        if not voice_id or not voice_id.strip():
            raise ValueError("voice_id cannot be empty")
        
        if not audio_path:
            raise ValueError("audio_path cannot be empty")
        
        # Step 1: Upload clone audio
        print(f"Uploading clone audio: {audio_path}")
        file_id = self.upload_clone_audio(audio_path)
        print(f"Clone audio uploaded, file_id: {file_id}")
        
        # Build clone request
        clone_payload = {
            "file_id": file_id,
            "voice_id": voice_id,
            "model": model,
        }
        
        # Add prompt audio (if provided)
        if prompt_audio and prompt_text:
            print(f"Uploading prompt audio: {prompt_audio}")
            prompt_file_id = self.upload_prompt_audio(prompt_audio)
            print(f"Prompt audio uploaded, file_id: {prompt_file_id}")
            
            clone_payload["clone_prompt"] = {
                "prompt_audio": prompt_file_id,
                "prompt_text": prompt_text
            }
        
        # Add text to convert (if provided)
        if text:
            clone_payload["text"] = text
        
        # Make clone request
        clone_url = f"{self.BASE_URL}/voice_clone"
        clone_headers = self.headers.copy()
        clone_headers["Content-Type"] = "application/json"
        
        print("Cloning voice...")
        response = requests.post(
            clone_url,
            headers=clone_headers,
            json=clone_payload
        )
        
        # Detailed error diagnosis
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if not response.ok:
            raise MiniMaxAPIError(
                f"Voice cloning failed: {response.text}",
                response.status_code,
                response.text
            )
        
        result = response.json()
        print(f"Clone request successful: {json.dumps(result, ensure_ascii=False)}")
        
        return VoiceCloneResult(
            task_id=result.get("task_id", ""),
            status=result.get("status", "unknown")
        )
    
    def clone_voice_with_file_id(
        self,
        voice_id: str,
        file_id: str,
        prompt_file_id: Optional[str] = None,
        prompt_text: Optional[str] = None,
        text: Optional[str] = None,
        model: str = "speech-2.8-hd"
    ) -> VoiceCloneResult:
        """
        Clone voice using pre-obtained file_id.
        
        This method is useful for step-by-step workflow where you already
        have the file_id from uploading the reference audio.
        
        Args:
            voice_id: Custom voice ID to identify this cloned voice
            file_id: File ID obtained from uploading reference audio (step 1)
            prompt_file_id: File ID of prompt audio (optional, from step 2)
            prompt_text: Text content corresponding to the prompt audio
            text: Text content to convert to speech (optional)
            model: Model name to use (default: speech-2.8-hd)
            
        Returns:
            VoiceCloneResult: The cloning result with task_id and status
            
        Raises:
            MiniMaxAPIError: Raised when API call fails
            ValueError: Raised when parameter validation fails
            
        Example:
            # Step-by-step usage:
            cloner = VoiceCloner()
            file_id = cloner.upload_clone_audio("/path/to/reference.m4a")
            prompt_file_id = cloner.upload_prompt_audio("/path/to/prompt.m4a")
            
            # Step 3: Complete cloning with file_ids
            result = cloner.clone_voice_with_file_id(
                voice_id="my_voice",
                file_id=file_id,
                prompt_file_id=prompt_file_id,
                prompt_text="Prompt text here",
                text="Text to synthesize"
            )
        """
        # Parameter validation
        if not voice_id or not voice_id.strip():
            raise ValueError("voice_id cannot be empty")
        
        if not file_id or not file_id.strip():
            raise ValueError("file_id cannot be empty")
        
        # Validate file_id format (must be numeric)
        if not file_id.isdigit():
            raise ValueError(
                f"Invalid file_id format: '{file_id}'. "
                "File ID must be a numeric string (e.g., '361790326784095')"
            )
        
        # Validate voice_id length (must be 8-256 characters)
        if len(voice_id) < 8 or len(voice_id) > 256:
            raise ValueError(
                f"Invalid voice_id length: {len(voice_id)}. "
                "Voice ID must be between 8 and 256 characters. "
                "Example: 'my_voice_001', 'MiniMaxVoiceClone'"
            )
        
        # Validate voice_id format (must start with letter, end with letter or number)
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$', voice_id):
            raise ValueError(
                f"Invalid voice_id format: '{voice_id}'. "
                "Voice ID must:\n"
                "  - Start with a letter\n"
                "  - Contain only letters, numbers, hyphens (-), underscores (_)\n"
                "  - End with a letter or number (not - or _)"
            )
        
        # Convert file_id to integer (API requires integer, not string)
        file_id_int = int(file_id)
        
        # Build clone request
        clone_payload = {
            "file_id": file_id_int,
            "voice_id": voice_id,
            "model": model,
        }
        
        # Add prompt audio (if provided)
        if prompt_file_id and prompt_text:
            # Ensure prompt_text ends with punctuation
            if prompt_text.strip()[-1] not in '。！？.!?,;':
                prompt_text = prompt_text.strip() + '。'
            
            clone_payload["clone_prompt"] = {
                "prompt_audio": int(prompt_file_id),
                "prompt_text": prompt_text
            }
        
        # Add text to convert (if provided)
        if text:
            clone_payload["text"] = text
        
        # Debug: Print the request payload (for troubleshooting)
        print(f"Request payload: {json.dumps(clone_payload, ensure_ascii=False, indent=2)}")
        
        # Make clone request
        clone_url = f"{self.BASE_URL}/voice_clone"
        clone_headers = self.headers.copy()
        clone_headers["Content-Type"] = "application/json"
        
        print("Cloning voice...")
        response = requests.post(
            clone_url,
            headers=clone_headers,
            json=clone_payload
        )
        
        # Detailed error diagnosis
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if not response.ok:
            raise MiniMaxAPIError(
                f"Voice cloning failed: {response.text}",
                response.status_code,
                response.text
            )
        
        result = response.json()
        print(f"Clone request successful: {json.dumps(result, ensure_ascii=False)}")
        
        return VoiceCloneResult(
            task_id=result.get("task_id", ""),
            status=result.get("status", "unknown")
        )
    
    # ==================== 文件管理方法 ====================
    
    def list_files(self, purpose: Optional[str] = None) -> list:
        """
        列出所有上传的文件
        
        这个方法用于查询账户中已上传的所有文件，可以按类型筛选。
        
        Args:
            purpose: 筛选文件类型，可选值：
                    - voice_clone: 快速复刻原始文件
                    - prompt_audio: 音色复刻的示例音频
                    - t2a_async_input: 异步长文本语音生成合成中
                    如果不提供，返回所有类型的文件
        
        Returns:
            list: 文件列表，每个文件包含以下字段：
                - file_id: 文件唯一标识符
                - filename: 文件名
                - bytes: 文件大小（字节）
                - created_at: 创建时间戳
                - purpose: 文件用途
        
        Raises:
            MiniMaxAPIError: 如果API调用失败
            
        Example:
            cloner = VoiceCloner()
            
            # 列出所有文件
            all_files = cloner.list_files()
            for f in all_files:
                print(f"ID: {f['file_id']}, Name: {f['filename']}")
            
            # 只列出复刻音频
            clone_files = cloner.list_files(purpose="voice_clone")
        """
        url = f"{self.BASE_URL}/files/list"
        
        params = {}
        if purpose:
            # 验证 purpose 参数
            valid_purposes = ["voice_clone", "prompt_audio", "t2a_async_input"]
            if purpose not in valid_purposes:
                raise ValueError(
                    f"Invalid purpose: '{purpose}'. "
                    f"Must be one of: {', '.join(valid_purposes)}"
                )
            params["purpose"] = purpose
        
        response = self.session.get(url, params=params)
        
        if not response.ok:
            raise MiniMaxAPIError(
                f"Failed to list files: {response.text}",
                response.status_code,
                response.text
            )
        
        result = response.json()
        return result.get("files", [])
    
    def get_file_info(self, file_id: str) -> dict:
        """
        查询单个文件的详细信息
        
        这个方法用于获取指定 file_id 的详细元数据信息。
        
        Args:
            file_id: 文件的唯一标识符（从上传接口或列表接口获得）
        
        Returns:
            dict: 文件详情，包含以下字段：
                - file_id: 文件唯一标识符
                - filename: 文件名
                - bytes: 文件大小（字节）
                - created_at: 创建时间戳
                - purpose: 文件用途
                - download_url: 文件下载链接（如果有）
        
        Raises:
            MiniMaxAPIError: 如果API调用失败或文件不存在
            
        Example:
            cloner = VoiceCloner()
            file_info = cloner.get_file_info("123456789")
            print(f"文件名: {file_info['filename']}")
            print(f"大小: {file_info['bytes'] / 1024:.2f} KB")
            print(f"创建时间: {file_info['created_at']}")
        """
        url = f"{self.BASE_URL}/files/retrieve"
        
        params = {"file_id": file_id}
        
        response = self.session.get(url, params=params)
        
        if not response.ok:
            raise MiniMaxAPIError(
                f"Failed to get file info: {response.text}",
                response.status_code,
                response.text
            )
        
        result = response.json()
        
        if "file" not in result:
            raise MiniMaxAPIError(
                f"Invalid response format: no 'file' field",
                response.status_code,
                response.text
            )
        
        return result["file"]
    
    def delete_file(self, file_id: str) -> bool:
        """
        删除上传的文件
        
        这个方法用于删除指定 file_id 的文件。删除后该文件将无法恢复。
        
        Args:
            file_id: 要删除的文件唯一标识符
        
        Returns:
            bool: 删除是否成功
            
        Raises:
            MiniMaxAPIError: 如果API调用失败或文件不存在
            
        Example:
            cloner = VoiceCloner()
            
            # 删除指定文件
            success = cloner.delete_file("123456789")
            if success:
                print("文件删除成功")
            else:
                print("文件删除失败")
        """
        url = f"{self.BASE_URL}/files/{file_id}"
        
        response = self.session.delete(url)
        
        if not response.ok:
            raise MiniMaxAPIError(
                f"Failed to delete file: {response.text}",
                response.status_code,
                response.text
            )
        
        result = response.json()
        base_resp = result.get("base_resp", {})
        
        return base_resp.get("status_code", -1) == 0


def main():
    """Command line entry point"""
    import argparse
    
    # Create the main parser with detailed description
    parser = argparse.ArgumentParser(
        description="A command-line tool for cloning voices using the MiniMax TTS API. "
                    "This tool allows you to upload reference audio, optionally provide "
                    "prompt audio for enhanced cloning, and generate speech with the cloned voice.",
        epilog="""
Usage Steps:
  Step 1: Upload reference audio to get file_id
  Step 2: Upload prompt audio (optional) for enhanced quality
  Step 3: Clone voice with the uploaded audio

Quick Start (All-in-one):
  # Complete voice cloning workflow in one command
  python voice_cloner.py --voice-id my_voice --audio reference.m4a

  # With prompt audio for enhanced quality
  python voice_cloner.py -v my_voice -a reference.m4a -p prompt.m4a -t "Prompt text"

  # With text to synthesize
  python voice_cloner.py --voice-id my_voice --audio reference.m4a --text "Hello world!"

  # Using API key from config file
  python voice_cloner.py -k your-api-key -v my_voice -a reference.m4a

Step-by-Step Workflow:
  # Step 1: Upload reference audio and get file_id
  python voice_cloner.py --step 1 --audio reference.m4a

  # Step 2: Upload prompt audio for enhanced quality (optional)
  python voice_cloner.py --step 2 --prompt-audio prompt.m4a --file-id <file_id_from_step1>

  # Step 3: Complete voice cloning (basic)
  python voice_cloner.py --step 3 --voice-id my_voice --file-id <file_id>
  
  # Step 3: Complete voice cloning (with prompt audio)
  # NOTE: When using --prompt-file-id, you MUST provide --prompt-text or --prompt-text-file
  # The prompt_text must exactly match what is spoken in the prompt audio
  python voice_cloner.py --step 3 --voice-id my_voice --file-id <file_id> \
      --prompt-file-id <prompt_file_id> --prompt-text-file prompt_text.txt \
      --text-file speech_text.txt

File Management:
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

For more information, visit: https://platform.minimaxi.com/docs/guides/speech-voice-clone
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Step-by-step workflow arguments
    workflow_group = parser.add_argument_group("Step-by-Step Workflow")
    workflow_group.add_argument(
        "--step", "-S",
        type=int,
        choices=[1, 2, 3],
        help="Run a specific step: 1=Upload clone audio, 2=Upload prompt audio, 3=Complete cloning"
    )
    workflow_group.add_argument(
        "--file-id", "-f",
        help="File ID from previous step (required for step 2 and 3)"
    )
    workflow_group.add_argument(
        "--prompt-file-id", "-F",
        help="Prompt file ID from step 2. REQUIRED if using step 2 output. "
             "Must be used with --prompt-text or --prompt-text-file."
    )
    
    # Required arguments (for quick start mode)
    required_group = parser.add_argument_group("Required Arguments (Quick Start)")
    required_group.add_argument(
        "--voice-id", "-v",
        help="Custom voice ID to identify this cloned voice"
    )
    required_group.add_argument(
        "--audio", "-a",
        help="Path to the reference audio file for cloning (mp3/m4a/wav, 10s-5min, max 20MB)"
    )
    
    # Optional arguments
    optional_group = parser.add_argument_group("Optional Arguments")
    optional_group.add_argument(
        "--api-key", "-k",
        help="MiniMax API key. If not provided, reads from MINIMAX_API_KEY environment variable or .env file"
    )
    optional_group.add_argument(
        "--prompt-audio", "-p",
        help="Path to the prompt audio file for enhanced cloning quality (mp3/m4a/wav, <8s, max 20MB)"
    )
    optional_group.add_argument(
        "--prompt-text", "-t",
        help="Text content corresponding to the prompt audio (used for better cloning accuracy)"
    )
    optional_group.add_argument(
        "--text", "-s",
        help="Text content to convert to speech with the cloned voice"
    )
    optional_group.add_argument(
        "--model", "-m",
        default="speech-2.8-hd",
        choices=["speech-2.8", "speech-2.8-hd"],
        help="Model to use for voice cloning (default: speech-2.8-hd)"
    )
    
    # Text input from file options
    text_file_group = parser.add_argument_group("Text Input from File")
    text_file_group.add_argument(
        "--text-file", "-T",
        help="Path to a file containing text to synthesize (for step 3). "
             "Use this instead of --text for long content."
    )
    text_file_group.add_argument(
        "--prompt-text-file", "-P",
        help="Path to a file containing prompt text (for step 3 with --prompt-file-id). "
             "Use this instead of --prompt-text for long content."
    )
    
    # File management options
    file_mgmt_group = parser.add_argument_group("File Management")
    file_mgmt_group.add_argument(
        "--list-files", "-L",
        action="store_true",
        help="List all uploaded files. Use --purpose to filter by type."
    )
    file_mgmt_group.add_argument(
        "--purpose", "-u",
        choices=["voice_clone", "prompt_audio", "t2a_async_input"],
        help="Filter files by purpose when listing. "
             "voice_clone: clone audio files, "
             "prompt_audio: prompt audio files, "
             "t2a_async_input: async T2A input files"
    )
    file_mgmt_group.add_argument(
        "--get-file-info", "-I",
        metavar="FILE_ID",
        help="Get detailed information about a specific file by its ID"
    )
    file_mgmt_group.add_argument(
        "--delete-file", "-D",
        metavar="FILE_ID",
        help="Delete a specific file by its ID. WARNING: This action cannot be undone!"
    )
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational output, only show results"
    )
    output_group.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results in JSON format"
    )
    
    # Add version argument
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Import sys module (needed for sys.argv and sys.stdout)
    import sys
    
    # Handle quiet mode
    if args.quiet:
        sys.stdout = open("/dev/null", "w")
    
    cloner = VoiceCloner(api_key=args.api_key)
    
    try:
        # File management commands (highest priority)
        if args.list_files:
            # 列出所有文件
            from datetime import datetime
            
            files = cloner.list_files(purpose=args.purpose)
            
            if args.json:
                import json
                output = {
                    "files": files,
                    "total": len(files)
                }
                print(json.dumps(output, indent=2, ensure_ascii=False))
            else:
                print(f"\n{'='*60}")
                print(f"文件列表")
                print(f"{'='*60}")
                
                if not files:
                    print("没有找到文件")
                else:
                    purpose_name = {
                        "voice_clone": "复刻音频",
                        "prompt_audio": "示例音频",
                        "t2a_async_input": "异步T2A输入"
                    }
                    
                    for i, f in enumerate(files, 1):
                        created_time = datetime.fromtimestamp(f.get("created_at", 0)).strftime("%Y-%m-%d %H:%M:%S")
                        purpose_chinese = purpose_name.get(f.get("purpose", ""), f.get("purpose", "未知"))
                        size_kb = f.get("bytes", 0) / 1024
                        
                        print(f"\n{i}. 文件 ID: {f.get('file_id', 'N/A')}")
                        print(f"   文件名: {f.get('filename', 'N/A')}")
                        print(f"   大小: {size_kb:.2f} KB")
                        print(f"   用途: {purpose_chinese}")
                        print(f"   创建时间: {created_time}")
                    
                    print(f"\n{'-'*60}")
                    print(f"共 {len(files)} 个文件")
                print()
            return 0
        
        if args.get_file_info:
            # 查询单个文件详情
            file_info = cloner.get_file_info(args.get_file_info)
            
            if args.json:
                import json
                print(json.dumps(file_info, indent=2, ensure_ascii=False))
            else:
                from datetime import datetime
                
                print(f"\n{'='*60}")
                print(f"文件详情")
                print(f"{'='*60}")
                print(f"文件 ID: {file_info.get('file_id', 'N/A')}")
                print(f"文件名: {file_info.get('filename', 'N/A')}")
                print(f"大小: {file_info.get('bytes', 0) / 1024:.2f} KB")
                print(f"用途: {file_info.get('purpose', 'N/A')}")
                created_time = datetime.fromtimestamp(file_info.get("created_at", 0)).strftime("%Y-%m-%d %H:%M:%S")
                print(f"创建时间: {created_time}")
                
                if file_info.get("download_url"):
                    print(f"下载链接: {file_info.get('download_url')}")
                print()
            return 0
        
        if args.delete_file:
            # 删除文件
            confirm = input(f"确定要删除文件 {args.delete_file} 吗? (输入 y 确认): ")
            if confirm.lower() != 'y':
                print("取消删除")
                return 0
            
            success = cloner.delete_file(args.delete_file)
            
            if success:
                if args.json:
                    import json
                    print(json.dumps({"success": True, "file_id": args.delete_file}, indent=2))
                else:
                    print(f"\n文件 {args.delete_file} 删除成功")
            else:
                if args.json:
                    import json
                    print(json.dumps({"success": False, "file_id": args.delete_file}, indent=2))
                else:
                    print(f"\n文件 {args.delete_file} 删除失败")
            return 0
        
        # Step-by-step workflow mode
        if args.step:
            if args.step == 1:
                # Step 1: Upload clone audio
                if not args.audio:
                    parser.error("--audio is required for step 1")
                file_id = cloner.upload_clone_audio(args.audio)
                print(f"\n[Step 1 Complete] Reference audio uploaded successfully")
                print(f"  File ID: {file_id}")
                print(f"\nNext steps:")
                print(f"  Option A: Complete cloning now")
                print(f"    {sys.argv[0]} --step 3 --voice-id <your_voice_id> --file-id {file_id} --text-file speech_text.txt")
                print(f"")
                print(f"  Option B: Upload prompt audio for enhanced quality")
                print(f"    {sys.argv[0]} --step 2 --file-id {file_id} --prompt-audio prompt.m4a --prompt-text-file prompt_text.txt")
                return 0
            
            elif args.step == 2:
                # Step 2: Upload prompt audio
                if not args.prompt_audio:
                    parser.error("--prompt-audio is required for step 2")
                if not args.file_id:
                    parser.error("--file-id is required for step 2 (from step 1)")
                prompt_file_id = cloner.upload_prompt_audio(args.prompt_audio)
                print(f"\n[Step 2 Complete] Prompt audio uploaded successfully")
                print(f"  Prompt File ID: {prompt_file_id}")
                print(f"  Reference File ID: {args.file_id}")
                print(f"\nNext step: Complete voice cloning")
                print(f"  Basic: {sys.argv[0]} --step 3 --voice-id <voice_id> --file-id {args.file_id}")
                print(f"  With prompt audio (recommended):")
                print(f"    {sys.argv[0]} --step 3 --voice-id <voice_id> --file-id {args.file_id} \\")
                print(f"        --prompt-file-id {prompt_file_id} --prompt-text-file prompt_text.txt --text-file speech_text.txt")
                return 0
            
            elif args.step == 3:
                # Step 3: Complete voice cloning
                if not args.voice_id:
                    parser.error("--voice-id is required for step 3")
                if not args.file_id:
                    parser.error("--file-id is required for step 3 (from step 1)")
                
                # Read text from file if specified, otherwise use command line argument
                text = args.text
                if args.text_file:
                    try:
                        with open(args.text_file, "r", encoding="utf-8") as f:
                            text = f.read().strip()
                    except FileNotFoundError:
                        parser.error(f"Text file not found: {args.text_file}")
                    except Exception as e:
                        parser.error(f"Error reading text file: {e}")
                
                # Read prompt text from file if specified
                prompt_text = args.prompt_text
                if args.prompt_text_file:
                    try:
                        with open(args.prompt_text_file, "r", encoding="utf-8") as f:
                            prompt_text = f.read().strip()
                    except FileNotFoundError:
                        parser.error(f"Prompt text file not found: {args.prompt_text_file}")
                    except Exception as e:
                        parser.error(f"Error reading prompt text file: {e}")
                
                # Validate: if prompt_file_id is provided, prompt_text is required
                if args.prompt_file_id and not prompt_text:
                    parser.error(
                        "--prompt-file-id requires --prompt-text or --prompt-text-file. "
                        "The prompt_text must exactly match the content spoken in the prompt audio."
                    )
                
                result = cloner.clone_voice_with_file_id(
                    voice_id=args.voice_id,
                    file_id=args.file_id,
                    prompt_file_id=args.prompt_file_id,
                    prompt_text=prompt_text,
                    text=text,
                    model=args.model
                )
                print(f"\n[Step 3 Complete] Voice cloning initiated")
                print(f"  Task ID: {result.task_id}")
                print(f"  Status: {result.status}")
                return 0
        
        # Quick start mode (all-in-one)
        if not args.voice_id or not args.audio:
            parser.error("--voice-id and --audio are required for quick start mode. "
                        "Or use --step for step-by-step workflow.")
        
        result = cloner.clone_voice(
            voice_id=args.voice_id,
            audio_path=args.audio,
            prompt_audio=args.prompt_audio,
            prompt_text=args.prompt_text,
            text=args.text,
            model=args.model
        )
        
        if args.json:
            import json
            output = {
                "task_id": result.task_id,
                "status": result.status,
                "audio_url": result.audio_url
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\nVoice cloning task submitted successfully")
            print(f"  Task ID: {result.task_id}")
            print(f"  Status: {result.status}")
            if result.audio_url:
                print(f"  Audio URL: {result.audio_url}")
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
