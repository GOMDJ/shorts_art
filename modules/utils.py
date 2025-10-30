"""
공통 유틸리티 함수
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv
from PIL import ImageDraw, ImageFont


def load_env_file(env_path: Optional[Path] = None) -> None:
    """
    환경 변수 파일 로드

    Args:
        env_path: .env 파일 경로 (None이면 기본 경로 사용)

    Raises:
        FileNotFoundError: .env 파일을 찾을 수 없는 경우
    """
    if env_path is None:
        env_path = Path.home() / "Desktop" / ".env.shorts"

    if not env_path.exists():
        raise FileNotFoundError(f"환경 변수 파일을 찾을 수 없습니다: {env_path}")

    load_dotenv(env_path)


def get_api_key(key_name: str) -> str:
    """
    API 키 가져오기

    Args:
        key_name: 환경 변수 이름

    Returns:
        API 키

    Raises:
        ValueError: API 키를 찾을 수 없는 경우
    """
    api_key = os.getenv(key_name)
    if not api_key:
        raise ValueError(f"환경 변수 {key_name}를 찾을 수 없습니다.")
    return api_key


def load_config(config_path: Path = Path("config.json")) -> Dict[str, Any]:
    """
    설정 파일 로드

    Args:
        config_path: 설정 파일 경로

    Returns:
        설정 딕셔너리

    Raises:
        FileNotFoundError: 설정 파일을 찾을 수 없는 경우
        json.JSONDecodeError: JSON 파싱 오류
    """
    if not config_path.exists():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    draw: ImageDraw.ImageDraw,
    stroke_width: int = 0
) -> List[str]:
    """
    텍스트 자동 줄바꿈

    Args:
        text: 줄바꿈할 텍스트
        font: 폰트 객체
        max_width: 최대 너비 (픽셀)
        draw: ImageDraw 객체
        stroke_width: 외곽선 두께

    Returns:
        줄바꿈된 텍스트 리스트
    """
    # 언더스코어를 공백으로 변환
    text = text.replace('_', ' ')

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font, stroke_width=stroke_width)
        width = bbox[2] - bbox[0]

        if width > max_width:
            if len(current_line) > 1:
                # 마지막 단어 빼고 줄 추가
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # 단어 하나가 너무 긴 경우 강제 추가
                lines.append(word)
                current_line = []

    # 마지막 줄 추가
    if current_line:
        lines.append(' '.join(current_line))

    return lines


def ensure_directory(directory: Path) -> None:
    """
    디렉토리 존재 확인 및 생성

    Args:
        directory: 디렉토리 경로
    """
    directory.mkdir(exist_ok=True, parents=True)


def calculate_aspect_ratio_fit(
    source_size: Tuple[int, int],
    target_size: Tuple[int, int]
) -> Tuple[int, int]:
    """
    종횡비를 유지하며 타겟 크기에 맞추기

    Args:
        source_size: 원본 크기 (width, height)
        target_size: 타겟 크기 (width, height)

    Returns:
        새로운 크기 (width, height)
    """
    source_width, source_height = source_size
    target_width, target_height = target_size

    source_ratio = source_width / source_height
    target_ratio = target_width / target_height

    if source_ratio > target_ratio:
        # 너비 기준
        new_width = target_width
        new_height = int(target_width / source_ratio)
    else:
        # 높이 기준
        new_height = target_height
        new_width = int(target_height * source_ratio)

    return new_width, new_height


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    값을 범위 내로 제한

    Args:
        value: 입력 값
        min_value: 최소 값
        max_value: 최대 값

    Returns:
        제한된 값
    """
    return max(min_value, min(max_value, value))


def format_file_size(size_bytes: int) -> str:
    """
    파일 크기를 읽기 쉬운 형식으로 변환

    Args:
        size_bytes: 바이트 단위 크기

    Returns:
        포맷된 문자열 (예: "1.5MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f}TB"
