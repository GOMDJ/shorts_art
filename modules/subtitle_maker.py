"""
자막 합성
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from typing import Dict, List, Any

from .utils import wrap_text


class SubtitleMaker:
    """자막 합성 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.font_path = config['subtitle']['font']
        self.font_size = config['subtitle']['size']
        self.color = config['subtitle']['color']
        self.stroke_width = config['subtitle'].get('stroke_width', 0)
        self.stroke_color = config['subtitle'].get('stroke_color', '#000000')
        self.shadow_offset = config['subtitle'].get('shadow_offset', [0, 0])
        self.shadow_color = config['subtitle'].get('shadow_color', '#000000')
        self.shadow_blur_radius = config['subtitle'].get('shadow_blur_radius', 0)

    def add_subtitles(
        self,
        image_files: List[Path],
        texts: List[str],
        output_dir: Path
    ) -> List[Path]:
        """
        이미지에 자막 합성 (중앙 배치, 자동 줄바꿈, 블러 그림자)

        Args:
            image_files: 이미지 파일 경로 리스트
            texts: 자막 텍스트 리스트
            output_dir: 출력 디렉토리

        Returns:
            자막 합성된 이미지 경로 리스트
        """
        output_dir.mkdir(exist_ok=True, parents=True)

        print("\n✍️  자막 합성 중...")

        # 폰트 로드
        font = self._load_font()

        subtitled_files = []

        for i, (image_path, text) in enumerate(zip(image_files, texts), 1):
            output_path = self._add_subtitle_to_image(
                image_path, text, font, output_dir, i
            )
            subtitled_files.append(output_path)

            # 줄바꿈 계산 (출력용)
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            max_width = img.width - 100
            lines = wrap_text(text, font, max_width, draw, self.stroke_width)

            print(f"  [{i:02d}] {text[:30]}... ({len(lines)}줄)")

        print(f"  ✓ {len(subtitled_files)}개 자막 합성 완료")
        return subtitled_files

    def _load_font(self) -> ImageFont.FreeTypeFont:
        """
        폰트 로드

        Returns:
            폰트 객체
        """
        try:
            return ImageFont.truetype(self.font_path, self.font_size)
        except Exception:
            print(f"  ⚠️  폰트를 찾을 수 없습니다: {self.font_path}")
            print("  기본 폰트 사용")
            return ImageFont.load_default()

    def _add_subtitle_to_image(
        self,
        image_path: Path,
        text: str,
        font: ImageFont.FreeTypeFont,
        output_dir: Path,
        index: int
    ) -> Path:
        """
        단일 이미지에 자막 추가

        Args:
            image_path: 이미지 경로
            text: 자막 텍스트
            font: 폰트 객체
            output_dir: 출력 디렉토리
            index: 인덱스 (파일명용)

        Returns:
            출력 파일 경로
        """
        img = Image.open(image_path)

        # 블러 그림자 레이어
        if self.shadow_blur_radius > 0:
            img = self._add_blurred_shadow(img, text, font)

        # 선명한 텍스트 그리기
        self._draw_text(img, text, font)

        # 저장
        output_path = output_dir / f"subtitled_{index:02d}.jpg"
        img.save(output_path, quality=95)

        return output_path

    def _add_blurred_shadow(
        self,
        img: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont
    ) -> Image.Image:
        """
        블러 그림자 추가

        Args:
            img: 이미지
            text: 텍스트
            font: 폰트

        Returns:
            그림자가 추가된 이미지
        """
        shadow_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)

        # 자동 줄바꿈 처리
        max_width = img.width - 100
        draw = ImageDraw.Draw(img)
        lines = wrap_text(text, font, max_width, draw, self.stroke_width)

        # 전체 텍스트 높이 계산
        line_height = self.font_size + 10
        total_height = len(lines) * line_height
        start_y = (img.height - total_height) // 2

        # 각 줄 그리기
        for j, line in enumerate(lines):
            bbox = shadow_draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]

            x = (img.width - text_width) // 2 + self.shadow_offset[0]
            y = start_y + j * line_height + self.shadow_offset[1]

            shadow_draw.text(
                (x, y),
                line,
                font=font,
                fill=self.shadow_color
            )

        # 블러 효과 적용 후 합성
        shadow_layer = shadow_layer.filter(
            ImageFilter.GaussianBlur(radius=self.shadow_blur_radius)
        )
        img.paste(shadow_layer, (0, 0), shadow_layer)

        return img

    def _draw_text(
        self,
        img: Image.Image,
        text: str,
        font: ImageFont.FreeTypeFont
    ) -> None:
        """
        이미지에 텍스트 그리기

        Args:
            img: 이미지
            text: 텍스트
            font: 폰트
        """
        draw = ImageDraw.Draw(img)

        # 자동 줄바꿈 처리
        max_width = img.width - 100
        lines = wrap_text(text, font, max_width, draw, self.stroke_width)

        # 전체 텍스트 높이 계산
        line_height = self.font_size + 10
        total_height = len(lines) * line_height
        start_y = (img.height - total_height) // 2

        # 각 줄 그리기
        for j, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font, stroke_width=self.stroke_width)
            text_width = bbox[2] - bbox[0]

            x = (img.width - text_width) // 2
            y = start_y + j * line_height

            if self.stroke_width > 0:
                # 외곽선 있을 때
                draw.text(
                    (x, y),
                    line,
                    font=font,
                    fill=self.color,
                    stroke_width=self.stroke_width,
                    stroke_fill=self.stroke_color
                )
            else:
                # 외곽선 없을 때
                draw.text(
                    (x, y),
                    line,
                    font=font,
                    fill=self.color
                )
