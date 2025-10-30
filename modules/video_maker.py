"""
영상 생성
"""
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from pathlib import Path
from typing import Dict, List, Any, Optional

from .constants import (
    VIDEO_CODEC,
    AUDIO_CODEC,
    TEMP_AUDIO_FILE,
    DEFAULT_FINAL_SCENE_DURATION
)
from .utils import format_file_size


class VideoMaker:
    """비디오 생성 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.fps = config['video']['fps']
        self.base_duration = config['video'].get('base_duration', 1.5)
        self.duration_per_char = config['video'].get('duration_per_char', 0.08)

    def calculate_duration(self, text: str) -> float:
        """
        텍스트 길이 기반 시간 계산

        Args:
            text: 텍스트

        Returns:
            시간 (초)
        """
        char_count = len(text)
        duration = self.base_duration + (char_count * self.duration_per_char)
        return round(duration, 1)

    def create_video(
        self,
        image_files: List[Path],
        texts: List[Optional[str]],
        audio_path: Optional[Path],
        output_path: Path,
        scene_timings: Optional[List[tuple]] = None
    ) -> bool:
        """
        이미지 + 오디오 → 영상 생성

        Args:
            image_files: 이미지 파일 경로 리스트
            texts: 각 이미지에 대응하는 텍스트 리스트 (시간 계산용, None 가능)
            audio_path: 오디오 파일 경로 (None 가능)
            output_path: 출력 영상 경로
            scene_timings: 장면 타이밍 [(scene_idx, start_time, duration), ...]
                          None이면 텍스트 길이 기반으로 계산

        Returns:
            성공 여부
        """
        print("\n🎬 영상 생성 중...")
        print(f"  이미지 수: {len(image_files)}개")

        if scene_timings:
            print(f"  모드: 🎵 리듬 동기화")
        else:
            print(f"  모드: 📝 텍스트 길이 기반")

        try:
            # 이미지 클립 생성
            if scene_timings:
                clips, total_duration = self._create_image_clips_with_timings(
                    image_files, texts, scene_timings
                )
            else:
                clips, total_duration = self._create_image_clips(image_files, texts)

            # 클립 연결
            video = concatenate_videoclips(clips, method="compose")

            # 오디오 합성
            if audio_path and audio_path.exists():
                video = self._add_audio(video, audio_path)

            # 저장
            self._save_video(video, output_path)

            # 정리
            self._cleanup(video, audio_path)

            # 결과 출력
            file_size = format_file_size(output_path.stat().st_size)
            print(f"\n  ✓ 영상 생성 완료!")
            print(f"  파일: {output_path.name}")
            print(f"  크기: {file_size}")
            print(f"  길이: {total_duration:.1f}초")

            return True

        except Exception as e:
            print(f"  ✗ 영상 생성 실패: {e}")
            return False

    def _create_image_clips(
        self,
        image_files: List[Path],
        texts: List[Optional[str]]
    ) -> tuple:
        """
        이미지 클립 생성

        Args:
            image_files: 이미지 파일 경로 리스트
            texts: 텍스트 리스트

        Returns:
            (클립 리스트, 총 시간)
        """
        clips = []
        total_duration = 0

        for i, img_path in enumerate(image_files):
            # 텍스트가 있으면 길이 기반 계산, 없으면 기본값
            if texts and i < len(texts) and texts[i] is not None:
                duration = self.calculate_duration(texts[i])
            else:
                # 마지막 장면 (원본 이미지)은 기본 시간
                duration = DEFAULT_FINAL_SCENE_DURATION

            clip = ImageClip(str(img_path), duration=duration)
            clips.append(clip)
            total_duration += duration

            if texts and i < len(texts) and texts[i] is not None:
                print(f"  [{i+1:02d}] {texts[i][:20]}... ({duration}초)")
            else:
                print(f"  [마지막] 원본 이미지 ({duration}초)")

        return clips, total_duration

    def _add_audio(
        self,
        video: concatenate_videoclips,
        audio_path: Path
    ) -> concatenate_videoclips:
        """
        비디오에 오디오 추가

        Args:
            video: 비디오 클립
            audio_path: 오디오 파일 경로

        Returns:
            오디오가 추가된 비디오
        """
        audio = AudioFileClip(str(audio_path))
        video = video.set_audio(audio)
        print("  ✓ 오디오 합성")
        return video

    def _save_video(self, video: concatenate_videoclips, output_path: Path) -> None:
        """
        비디오 저장

        Args:
            video: 비디오 클립
            output_path: 출력 경로
        """
        video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC,
            temp_audiofile=TEMP_AUDIO_FILE,
            remove_temp=True
        )

    def _create_image_clips_with_timings(
        self,
        image_files: List[Path],
        texts: List[Optional[str]],
        scene_timings: List[tuple]
    ) -> tuple:
        """
        타이밍 기반 이미지 클립 생성 (리듬 동기화)

        Args:
            image_files: 이미지 파일 경로 리스트
            texts: 텍스트 리스트
            scene_timings: [(scene_idx, start_time, duration), ...]

        Returns:
            (클립 리스트, 총 시간)
        """
        clips = []
        total_duration = 0

        for scene_idx, start_time, duration in scene_timings:
            if scene_idx >= len(image_files):
                print(f"  ⚠️  장면 {scene_idx}가 이미지 수를 초과합니다")
                continue

            img_path = image_files[scene_idx]
            clip = ImageClip(str(img_path), duration=duration)
            clips.append(clip)
            total_duration += duration

            # 텍스트 정보 출력
            if texts and scene_idx < len(texts) and texts[scene_idx] is not None:
                text_preview = texts[scene_idx][:20]
                print(f"  [{scene_idx+1:02d}] {text_preview}... ({duration:.2f}초, 시작: {start_time:.2f}초)")
            else:
                print(f"  [{scene_idx+1:02d}] 원본 이미지 ({duration:.2f}초, 시작: {start_time:.2f}초)")

        return clips, total_duration

    def _cleanup(
        self,
        video: concatenate_videoclips,
        audio_path: Optional[Path]
    ) -> None:
        """
        리소스 정리

        Args:
            video: 비디오 클립
            audio_path: 오디오 파일 경로
        """
        video.close()
        if audio_path and audio_path.exists():
            try:
                audio = AudioFileClip(str(audio_path))
                audio.close()
            except Exception:
                pass
