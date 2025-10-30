"""
TTS 음성 생성 (OpenAI)
"""
import openai
from pathlib import Path
from typing import Dict, List, Any

from .constants import TTS_MODEL
from .utils import load_env_file, get_api_key, format_file_size


class TTSGenerator:
    """TTS 음성 생성 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.voice = config['tts']['voice']
        self.speed = config['tts']['speed']

        # API 키 로드
        try:
            load_env_file()
            self.api_key = get_api_key("OPENAI_API_KEY")
            openai.api_key = self.api_key
            self.enabled = True
        except (FileNotFoundError, ValueError) as e:
            print(f"  ⚠️  {e}")
            print("  TTS 비활성화")
            self.enabled = False

    def generate(self, texts: List[str], output_path: Path) -> bool:
        """
        텍스트 → TTS 음성 생성

        Args:
            texts: 텍스트 리스트
            output_path: 출력 오디오 경로

        Returns:
            성공 여부
        """
        if not self.enabled:
            print("\n🔇 TTS 비활성화 (API 키 없음)")
            return False

        print("\n🎙️  TTS 음성 생성 중...")
        print(f"  음성: {self.voice}")
        print(f"  속도: {self.speed}x")

        try:
            # 전체 텍스트 합치기
            full_text = " ".join(texts)

            # OpenAI TTS API 호출
            response = openai.audio.speech.create(
                model=TTS_MODEL,
                voice=self.voice,
                input=full_text,
                speed=self.speed
            )

            # 저장
            response.stream_to_file(str(output_path))

            file_size = format_file_size(output_path.stat().st_size)
            print(f"  ✓ TTS 생성 완료: {file_size}")

            return True

        except Exception as e:
            print(f"  ✗ TTS 생성 실패: {e}")
            return False
