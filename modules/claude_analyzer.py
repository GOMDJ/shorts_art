"""
Claude API를 사용한 이미지 좌표 분석
"""
import anthropic
import json
import base64
from pathlib import Path
from PIL import Image
from typing import Dict, List, Any
import io

from .constants import (
    CLAUDE_MODEL,
    CLAUDE_MAX_TOKENS,
    CLAUDE_MAX_IMAGE_SIZE_MB,
    IMAGE_RGBA_MODE,
    IMAGE_RGB_MODE,
    IMAGE_JPEG_FORMAT
)
from .utils import load_env_file, get_api_key


class ClaudeAnalyzer:
    """Claude AI를 사용한 이미지 분석 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        초기화

        Args:
            config: 설정 딕셔너리

        Raises:
            ValueError: API 키가 없는 경우
        """
        # API 키 로드
        load_env_file()
        self.api_key = get_api_key("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.config = config

    def resize_image_under_limit(self, image_path: Path) -> str:
        """
        이미지를 크기 제한 이하로 리사이즈하고 base64 반환

        Args:
            image_path: 이미지 파일 경로

        Returns:
            base64 인코딩된 이미지 데이터

        Raises:
            Exception: 이미지를 제한 크기 이하로 줄일 수 없는 경우
        """
        img = Image.open(image_path)

        # RGBA를 RGB로 변환
        if img.mode == IMAGE_RGBA_MODE:
            img = img.convert(IMAGE_RGB_MODE)

        width, height = img.size
        quality = 85

        max_dimension = self.config['image']['max_dimension']
        min_dimension = self.config['image']['min_dimension']

        # 너무 큰 이미지는 먼저 리사이즈
        if width > max_dimension or height > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            width, height = new_width, new_height
            print(f"  리사이즈: {width}x{height}")

        # 품질 조정으로 크기 제한 이하로
        max_size_bytes = CLAUDE_MAX_IMAGE_SIZE_MB * 1_000_000

        while True:
            buffer = io.BytesIO()
            img.save(buffer, format=IMAGE_JPEG_FORMAT, quality=quality)
            buffer.seek(0)
            image_bytes = buffer.read()
            size = len(image_bytes)

            # Base64 인코딩 후 크기 체크
            encoded = base64.b64encode(image_bytes)
            encoded_size = len(encoded)

            if encoded_size <= max_size_bytes:
                image_data = encoded.decode('utf-8')
                print(f"  ✓ 이미지 크기: {size / 1024 / 1024:.2f}MB "
                      f"(인코딩: {encoded_size / 1024 / 1024:.2f}MB, 품질: {quality}%)")
                return image_data

            # 품질 낮추기
            if quality > 40:
                quality -= 5
            else:
                # 더 작게 리사이즈
                width = int(width * 0.85)
                height = int(height * 0.85)
                img = img.resize((width, height), Image.Resampling.LANCZOS)
                quality = 85
                print(f"  추가 리사이즈: {width}x{height}")

            if width < min_dimension or height < min_dimension:
                raise Exception(
                    f"이미지를 {CLAUDE_MAX_IMAGE_SIZE_MB}MB 이하로 줄일 수 없습니다"
                )

    def analyze(self, image_path: Path, scenes: List[str]) -> Dict[str, Any]:
        """
        이미지를 분석해서 각 장면에 맞는 줌 좌표 생성

        Args:
            image_path: 이미지 파일 경로
            scenes: 장면 텍스트 리스트

        Returns:
            {
                "success": bool,
                "coordinates": List[Dict],
                "error": str (실패 시),
                "raw_response": str (성공 시)
            }
        """
        print("\n🤖 Claude API 분석 중...")
        print(f"  장면 수: {len(scenes)}개")

        try:
            # 이미지 리사이즈 및 base64 변환
            image_data = self.resize_image_under_limit(image_path)

            # 장면 리스트를 텍스트로
            scenes_text = "\n".join([f"{i+1}. {scene}" for i, scene in enumerate(scenes)])

            prompt = self._create_analysis_prompt(scenes_text)

            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=CLAUDE_MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            # 응답 파싱
            result_text = response.content[0].text
            result = self._parse_json_response(result_text)

            print(f"  ✓ 분석 완료: {len(result)}개 좌표 생성")

            return {
                "success": True,
                "coordinates": result,
                "raw_response": response.content[0].text
            }

        except Exception as e:
            print(f"  ✗ 분석 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _create_analysis_prompt(self, scenes_text: str) -> str:
        """
        Claude 분석용 프롬프트 생성

        Args:
            scenes_text: 장면 텍스트 (번호 포함)

        Returns:
            프롬프트 문자열
        """
        return f"""당신은 명화를 분석하여 숏폼 영상을 위한 최적의 확대 좌표를 찾는 전문가입니다.

# 분석할 장면들:
{scenes_text}

# 당신의 임무:
각 장면 텍스트에 가장 적합한 그림의 영역을 찾아 좌표를 제공하세요.

# 좌표 시스템 설명:
- **x, y**: 확대할 영역의 중심점 (0.0 ~ 1.0)
  - 0.0 = 왼쪽/위쪽 끝
  - 0.5 = 정중앙
  - 1.0 = 오른쪽/아래쪽 끝

- **zoom**: 확대 배율
  - 1.0 = 원본 크기 (전체 보기)
  - 1.5 = 1.5배 확대 (영역의 67% 표시)
  - 2.0 = 2배 확대 (영역의 50% 표시)
  - 2.5 = 2.5배 확대 (영역의 40% 표시)
  - 3.0 = 3배 확대 (영역의 33% 표시, 최대값)

# 분석 가이드라인:

1. **장면 매칭 정확도**
   - 각 텍스트가 설명하는 요소를 그림에서 정확히 찾으세요
   - 텍스트가 "눈", "입", "손" 등 구체적 신체 부위를 언급하면 해당 부위를 정확히 중심으로
   - 텍스트가 감정이나 분위기를 설명하면 그것을 가장 잘 표현하는 부분을 선택

2. **확대 비율 선택**
   - **디테일 장면** (눈, 손, 입술 등): zoom 2.0 ~ 3.0
   - **얼굴/인물 전체**: zoom 1.5 ~ 2.0
   - **구도/분위기**: zoom 1.0 ~ 1.5
   - **전체 맥락**: zoom 1.0

3. **여러 인물/요소가 있는 경우**
   - 2명 이상의 얼굴을 보여줘야 하면: 두 얼굴이 모두 잘 보이도록 중심점 조정
   - 여러 요소를 동시에 보여줘야 하면: zoom을 낮춰서 모든 요소 포함
   - 중심점은 모든 중요 요소의 기하학적 중심

4. **중심점 정밀 지정**
   - 인물의 얼굴: 눈 사이 또는 코 위치
   - 손: 손바닥 또는 손가락 중심
   - 입: 입술 중앙
   - 눈: 눈동자 중심
   - 정확한 소수점 값 사용 (0.1 단위보다 0.05 단위로 세밀하게)

5. **연속성 고려**
   - 첫 장면은 전체 맥락 파악을 위해 zoom 낮게 (1.0~1.3)
   - 중간 장면들은 디테일 강조 (1.5~3.0)
   - 마지막 장면은 강렬한 디테일 또는 전체 복귀

6. **주의사항**
   - 이미지 경계를 벗어나지 않도록 여유 확보
   - zoom이 높을수록 x, y는 0.2~0.8 범위 내에서 선택
   - 그림의 핵심 요소가 잘리지 않도록 확인

# 출력 형식:
반드시 아래 JSON 형식으로만 응답하세요. 다른 설명이나 주석은 일절 포함하지 마세요.

```json
[
  {{"scene": 1, "text": "첫 번째 장면 텍스트", "x": 0.5, "y": 0.5, "zoom": 1.0}},
  {{"scene": 2, "text": "두 번째 장면 텍스트", "x": 0.35, "y": 0.42, "zoom": 2.5}},
  ...
]
```

이제 위 그림을 분석하여 각 장면에 최적화된 좌표를 JSON으로만 제공하세요."""

    def _parse_json_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Claude 응답에서 JSON 추출 및 파싱

        Args:
            response_text: Claude 응답 텍스트

        Returns:
            파싱된 좌표 리스트

        Raises:
            json.JSONDecodeError: JSON 파싱 실패
        """
        # JSON 추출
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        return json.loads(response_text)
