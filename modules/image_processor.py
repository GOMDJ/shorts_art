"""
이미지 처리 - 다운로드, 크롭, 리사이즈
"""
import requests
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Dict, List, Any, Tuple

from .constants import (
    USER_AGENT,
    HTTP_TIMEOUT_SECONDS,
    DEFAULT_MUSEUM_PADDING,
    DEFAULT_MUSEUM_TEXT_HEIGHT
)
from .utils import wrap_text, clamp, format_file_size


class ImageProcessor:
    """이미지 처리 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.video_width = config['video']['width']
        self.video_height = config['video']['height']

    def download_image(self, url: str, save_path: Path) -> bool:
        """
        이미지 다운로드

        Args:
            url: 이미지 URL
            save_path: 저장 경로

        Returns:
            성공 여부
        """
        print(f"  URL: {url}")

        try:
            headers = {'User-Agent': USER_AGENT}

            print("  연결 중...")
            response = requests.get(
                url,
                timeout=HTTP_TIMEOUT_SECONDS,
                headers=headers,
                allow_redirects=True
            )

            print(f"  상태 코드: {response.status_code}")

            if response.status_code != 200:
                print(f"  ✗ HTTP 에러: {response.status_code}")
                print(f"  응답: {response.text[:200]}")
                return False

            # 이미지 타입 확인
            content_type = response.headers.get('Content-Type', '')
            print(f"  Content-Type: {content_type}")

            if 'image' not in content_type:
                print(f"  ✗ 이미지가 아님: {content_type}")
                return False

            # 저장
            with open(save_path, 'wb') as f:
                f.write(response.content)

            file_size = format_file_size(save_path.stat().st_size)
            print(f"  ✓ 다운로드 완료: {save_path.name} ({file_size})")
            return True

        except requests.exceptions.Timeout:
            print(f"  ✗ 타임아웃: {HTTP_TIMEOUT_SECONDS}초 초과")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"  ✗ 연결 실패: {e}")
            return False
        except Exception as e:
            print(f"  ✗ 다운로드 실패: {type(e).__name__}: {e}")
            return False

    def create_museum_view(
        self,
        image_path: Path,
        artwork_info: List[str],
        output_path: Path
    ) -> Path:
        """
        원본 이미지를 미술관 스타일로 보여주기

        Args:
            image_path: 이미지 경로
            artwork_info: 작품 정보 리스트 (제목, 작가, 제작정보, 크기, 소장처)
            output_path: 출력 경로

        Returns:
            출력 파일 경로
        """
        # 원본 이미지 로드
        img = Image.open(image_path)

        # 검은 배경 생성
        canvas = Image.new('RGB', (self.video_width, self.video_height), (0, 0, 0))

        # 이미지 크기 계산
        img_size = self._calculate_museum_image_size(img.size)
        resized_img = img.resize(img_size, Image.Resampling.LANCZOS)

        # 중앙 배치
        x, y = self._calculate_museum_image_position(img_size)
        canvas.paste(resized_img, (x, y))

        # 작품 정보 추가
        self._draw_artwork_info(canvas, artwork_info)

        # 저장
        canvas.save(output_path, quality=self.config['image']['quality'])

        print(f"  ✓ 원본 이미지 장면 생성: {output_path.name}")
        return output_path

    def generate_zoomed_images(
        self,
        image_path: Path,
        coordinates: List[Dict[str, Any]],
        output_dir: Path
    ) -> List[Path]:
        """
        좌표를 기반으로 확대 이미지 생성 (9:16 비율)

        Args:
            image_path: 이미지 경로
            coordinates: 좌표 리스트
            output_dir: 출력 디렉토리

        Returns:
            생성된 이미지 경로 리스트
        """
        output_dir.mkdir(exist_ok=True, parents=True)

        img = Image.open(image_path)
        width, height = img.size

        print("\n📐 이미지 처리 중...")
        print(f"  원본: {width}x{height}")
        print(f"  출력: {self.video_width}x{self.video_height} (9:16)")

        generated_files = []

        for coord in coordinates:
            scene = coord['scene']
            x = coord['x']
            y = coord['y']
            zoom = coord['zoom']
            text = coord['text']

            # 크롭 영역 계산
            crop_box = self._calculate_crop_box(width, height, x, y, zoom)

            # 크롭
            cropped = img.crop(crop_box)

            # 9:16 비율로 조정
            final = self._fit_to_aspect_ratio(cropped)

            # 저장
            filename = f"scene_{scene:02d}.jpg"
            output_path = output_dir / filename
            final.save(output_path, quality=self.config['image']['quality'])

            generated_files.append(output_path)

            print(f"  [{scene:02d}] {text[:20]}... → {filename}")

        print(f"  ✓ {len(generated_files)}개 이미지 생성 완료")
        return generated_files

    def _calculate_museum_image_size(self, img_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        미술관 뷰에서 이미지 크기 계산

        Args:
            img_size: 원본 이미지 크기 (width, height)

        Returns:
            새로운 크기 (width, height)
        """
        img_width, img_height = img_size
        img_ratio = img_width / img_height

        # 양옆 여백 및 텍스트 공간
        max_width = self.video_width - DEFAULT_MUSEUM_PADDING
        max_height = self.video_height - DEFAULT_MUSEUM_TEXT_HEIGHT

        if img_ratio > (max_width / max_height):
            # 너비 기준
            new_width = max_width
            new_height = int(max_width / img_ratio)
        else:
            # 높이 기준
            new_height = max_height
            new_width = int(max_height * img_ratio)

        return new_width, new_height

    def _calculate_museum_image_position(self, img_size: Tuple[int, int]) -> Tuple[int, int]:
        """
        미술관 뷰에서 이미지 위치 계산

        Args:
            img_size: 이미지 크기 (width, height)

        Returns:
            위치 (x, y)
        """
        new_width, new_height = img_size
        x = (self.video_width - new_width) // 2
        y = (self.video_height - new_height - DEFAULT_MUSEUM_TEXT_HEIGHT) // 2
        return x, y

    def _draw_artwork_info(self, canvas: Image.Image, artwork_info: List[str]) -> None:
        """
        캔버스에 작품 정보 그리기

        Args:
            canvas: 캔버스 이미지
            artwork_info: 작품 정보 리스트
        """
        draw = ImageDraw.Draw(canvas)

        try:
            font_title = ImageFont.truetype(self.config['subtitle']['font'], 60)
            font_info = ImageFont.truetype(self.config['subtitle']['font'], 42)
        except Exception:
            font_title = ImageFont.load_default()
            font_info = ImageFont.load_default()

        # 작품 정보 그리기
        max_text_width = self.video_width - DEFAULT_MUSEUM_PADDING
        start_y = self.video_height - 480

        for i, info_line in enumerate(artwork_info):
            if i == 0:
                # 첫 줄 (작품명) - 크게, 흰색
                font = font_title
                color = '#FFFFFF'
                line_spacing = 70
            else:
                # 나머지 (작가, 제작정보 등) - 작게, 회색
                font = font_info
                color = '#AAAAAA'
                line_spacing = 55

            # 줄바꿈 처리
            wrapped_lines = wrap_text(info_line, font, max_text_width, draw)

            for line in wrapped_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_x = (self.video_width - line_width) // 2

                draw.text(
                    (line_x, start_y),
                    line,
                    font=font,
                    fill=color
                )

                start_y += line_spacing

    def _calculate_crop_box(
        self,
        img_width: int,
        img_height: int,
        x: float,
        y: float,
        zoom: float
    ) -> Tuple[int, int, int, int]:
        """
        크롭 박스 계산

        Args:
            img_width: 이미지 너비
            img_height: 이미지 높이
            x: 중심점 x (0.0~1.0)
            y: 중심점 y (0.0~1.0)
            zoom: 확대 배율

        Returns:
            크롭 박스 (left, top, right, bottom)
        """
        # 줌 영역 계산
        crop_width = img_width / zoom
        crop_height = img_height / zoom

        # 중심점 계산
        center_x = img_width * x
        center_y = img_height * y

        # 크롭 박스 계산
        left = center_x - crop_width / 2
        top = center_y - crop_height / 2
        right = center_x + crop_width / 2
        bottom = center_y + crop_height / 2

        # 경계 처리
        if left < 0:
            right -= left
            left = 0
        if top < 0:
            bottom -= top
            top = 0
        if right > img_width:
            left -= (right - img_width)
            right = img_width
        if bottom > img_height:
            top -= (bottom - img_height)
            bottom = img_height

        # 최종 클램핑
        left = clamp(left, 0, img_width)
        top = clamp(top, 0, img_height)
        right = clamp(right, 0, img_width)
        bottom = clamp(bottom, 0, img_height)

        return int(left), int(top), int(right), int(bottom)

    def _fit_to_aspect_ratio(self, img: Image.Image) -> Image.Image:
        """
        이미지를 9:16 비율로 조정

        Args:
            img: 입력 이미지

        Returns:
            9:16 비율로 조정된 이미지
        """
        cropped_width, cropped_height = img.size
        target_ratio = self.video_width / self.video_height
        current_ratio = cropped_width / cropped_height

        if current_ratio > target_ratio:
            # 너무 넓음 - 좌우 자르기
            new_width = int(cropped_height * target_ratio)
            crop_left = (cropped_width - new_width) // 2
            img = img.crop((crop_left, 0, crop_left + new_width, cropped_height))
        else:
            # 너무 좁음 - 상하 자르기
            new_height = int(cropped_width / target_ratio)
            crop_top = (cropped_height - new_height) // 2
            img = img.crop((0, crop_top, cropped_width, crop_top + new_height))

        # 최종 리사이즈
        return img.resize((self.video_width, self.video_height), Image.Resampling.LANCZOS)
