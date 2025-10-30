"""
상수 정의
"""

# Claude API
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 4096
CLAUDE_MAX_IMAGE_SIZE_MB = 5

# 이미지 처리
IMAGE_JPEG_FORMAT = "JPEG"
IMAGE_RGBA_MODE = "RGBA"
IMAGE_RGB_MODE = "RGB"

# 비디오
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
TEMP_AUDIO_FILE = "temp-audio.m4a"

# TTS
TTS_MODEL = "tts-1"

# HTTP
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HTTP_TIMEOUT_SECONDS = 30

# 경로
DEFAULT_ENV_PATH = "Desktop/.env.shorts"
DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_DB_PATH = "shorts_art.db"

# UI 메시지
SEPARATOR_LINE = "=" * 60
TITLE_EMOJI = "🎨"
DOWNLOAD_EMOJI = "📥"
ANALYSIS_EMOJI = "🤖"
ZOOM_EMOJI = "🔍"
SUBTITLE_EMOJI = "✍️"
MUSEUM_EMOJI = "🖼️"
VIDEO_EMOJI = "🎬"
SUCCESS_EMOJI = "✅"
ERROR_EMOJI = "❌"
WARNING_EMOJI = "⚠️"

# 기본값
DEFAULT_ARTIST = "Unknown Artist"
DEFAULT_FINAL_SCENE_DURATION = 5.0
DEFAULT_MUSEUM_PADDING = 200
DEFAULT_MUSEUM_TEXT_HEIGHT = 550
