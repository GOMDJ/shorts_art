"""
오디오 분석 - 비트 및 강조 타이밍 추출
"""
import librosa
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple


class AudioAnalyzer:
    """오디오 분석 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        초기화

        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.audio_config = config.get('audio', {})
        self.hop_length = self.audio_config.get('hop_length', 512)
        self.onset_threshold = self.audio_config.get('onset_threshold', 0.5)
        self.beat_threshold = self.audio_config.get('beat_threshold', 0.3)

    def analyze(self, audio_path: Path, target_duration: float = None) -> Dict[str, Any]:
        """
        오디오 파일 분석하여 비트 및 강조 타이밍 추출

        Args:
            audio_path: 오디오 파일 경로
            target_duration: 목표 길이 (None이면 전체 사용)

        Returns:
            {
                "duration": float,  # 오디오 길이
                "tempo": float,  # BPM
                "beats": List[float],  # 비트 타이밍 (초)
                "onsets": List[float],  # 강조 타이밍 (초)
                "scene_timings": List[float],  # 장면 전환 타이밍 (초)
                "sr": int  # 샘플링 레이트
            }
        """
        print("\n🎵 오디오 분석 중...")
        print(f"  파일: {audio_path.name}")

        try:
            # 오디오 로드
            y, sr = librosa.load(str(audio_path), sr=None)
            duration = librosa.get_duration(y=y, sr=sr)

            # 목표 길이가 지정되면 잘라내기
            if target_duration and target_duration < duration:
                y = y[:int(target_duration * sr)]
                duration = target_duration

            print(f"  길이: {duration:.2f}초")
            print(f"  샘플링 레이트: {sr}Hz")

            # 템포 및 비트 감지
            tempo, beats = self._detect_beats(y, sr)
            print(f"  템포: {tempo:.1f} BPM")
            print(f"  비트: {len(beats)}개")

            # 강조 지점 감지 (onset detection)
            onsets = self._detect_onsets(y, sr)
            print(f"  강조 지점: {len(onsets)}개")

            # 장면 전환 타이밍 계산
            scene_timings = self._calculate_scene_timings(beats, onsets, duration)
            print(f"  장면 전환 타이밍: {len(scene_timings)}개")

            return {
                "duration": duration,
                "tempo": tempo,
                "beats": beats,
                "onsets": onsets,
                "scene_timings": scene_timings,
                "sr": sr
            }

        except Exception as e:
            print(f"  ✗ 오디오 분석 실패: {e}")
            return None

    def _detect_beats(self, y: np.ndarray, sr: int) -> Tuple[float, List[float]]:
        """
        비트 감지

        Args:
            y: 오디오 신호
            sr: 샘플링 레이트

        Returns:
            (tempo, beat_times)
        """
        # 템포 및 비트 프레임 추출
        tempo, beat_frames = librosa.beat.beat_track(
            y=y,
            sr=sr,
            hop_length=self.hop_length
        )

        # 프레임을 시간으로 변환
        beat_times = librosa.frames_to_time(
            beat_frames,
            sr=sr,
            hop_length=self.hop_length
        )

        return float(tempo), beat_times.tolist()

    def _detect_onsets(self, y: np.ndarray, sr: int) -> List[float]:
        """
        강조 지점 감지 (onset detection)

        Args:
            y: 오디오 신호
            sr: 샘플링 레이트

        Returns:
            onset_times
        """
        # Onset strength envelope 계산
        onset_env = librosa.onset.onset_strength(
            y=y,
            sr=sr,
            hop_length=self.hop_length
        )

        # Onset 감지
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            hop_length=self.hop_length,
            backtrack=True,
            normalize=True
        )

        # 프레임을 시간으로 변환
        onset_times = librosa.frames_to_time(
            onset_frames,
            sr=sr,
            hop_length=self.hop_length
        )

        return onset_times.tolist()

    def _calculate_scene_timings(
        self,
        beats: List[float],
        onsets: List[float],
        duration: float
    ) -> List[float]:
        """
        장면 전환 타이밍 계산 (비트와 강조 지점 결합)

        Args:
            beats: 비트 타이밍
            onsets: 강조 타이밍
            duration: 전체 길이

        Returns:
            scene_timings
        """
        # 비트와 강조 지점을 합치고 정렬
        all_timings = sorted(set(beats + onsets))

        # 너무 가까운 타이밍 필터링 (최소 간격)
        min_interval = self.audio_config.get('min_scene_interval', 0.5)
        filtered_timings = []
        last_time = -min_interval

        for time in all_timings:
            if time - last_time >= min_interval:
                filtered_timings.append(time)
                last_time = time

        # 0.0이 없으면 추가
        if not filtered_timings or filtered_timings[0] > 0.1:
            filtered_timings.insert(0, 0.0)

        return filtered_timings

    def distribute_scenes_to_timings(
        self,
        num_scenes: int,
        audio_analysis: Dict[str, Any],
        strategy: str = "auto"
    ) -> List[Tuple[int, float, float]]:
        """
        장면들을 오디오 타이밍에 맞춰 배치

        Args:
            num_scenes: 장면 개수
            audio_analysis: 오디오 분석 결과
            strategy: 배치 전략
                - "auto": 자동 (장면 수에 맞춰)
                - "evenly": 균등 배치
                - "beats": 비트에 맞춰
                - "onsets": 강조 지점에 맞춰

        Returns:
            [(scene_index, start_time, duration), ...]
        """
        scene_timings = audio_analysis['scene_timings']
        duration = audio_analysis['duration']

        if strategy == "evenly":
            # 균등 분할
            scene_duration = duration / num_scenes
            return [
                (i, i * scene_duration, scene_duration)
                for i in range(num_scenes)
            ]

        elif strategy == "beats":
            # 비트에 맞춰
            timings = audio_analysis['beats']
        elif strategy == "onsets":
            # 강조 지점에 맞춰
            timings = audio_analysis['onsets']
        else:
            # auto: scene_timings 사용
            timings = scene_timings

        # 장면 수에 맞춰 타이밍 선택
        if len(timings) < num_scenes:
            # 타이밍이 부족하면 균등 분할
            print(f"  ⚠️  타이밍({len(timings)}개)이 장면({num_scenes}개)보다 적어 균등 분할 사용")
            scene_duration = duration / num_scenes
            return [
                (i, i * scene_duration, scene_duration)
                for i in range(num_scenes)
            ]

        # 타이밍이 많으면 균등 간격으로 샘플링
        selected_indices = np.linspace(0, len(timings) - 1, num_scenes, dtype=int)
        selected_timings = [timings[i] for i in selected_indices]

        # 각 장면의 시작 시간과 길이 계산
        result = []
        for i in range(num_scenes):
            start_time = selected_timings[i]

            # 다음 장면이 있으면 그 시작 시간까지, 없으면 끝까지
            if i < num_scenes - 1:
                end_time = selected_timings[i + 1]
            else:
                end_time = duration

            scene_duration = end_time - start_time
            result.append((i, start_time, scene_duration))

        return result

    def trim_audio(
        self,
        audio_path: Path,
        output_path: Path,
        target_duration: float
    ) -> bool:
        """
        오디오 파일을 목표 길이로 자르기

        Args:
            audio_path: 입력 오디오 경로
            output_path: 출력 오디오 경로
            target_duration: 목표 길이 (초)

        Returns:
            성공 여부
        """
        try:
            import soundfile as sf

            # 오디오 로드
            y, sr = librosa.load(str(audio_path), sr=None)

            # 목표 길이로 자르기
            target_samples = int(target_duration * sr)
            y_trimmed = y[:target_samples]

            # 저장
            sf.write(str(output_path), y_trimmed, sr)

            print(f"  ✓ 오디오 트리밍 완료: {target_duration:.2f}초")
            return True

        except Exception as e:
            print(f"  ✗ 오디오 트리밍 실패: {e}")
            return False
