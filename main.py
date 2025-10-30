"""
메인 실행 파일
"""
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from modules.claude_analyzer import ClaudeAnalyzer
from modules.image_processor import ImageProcessor
from modules.subtitle_maker import SubtitleMaker
from modules.video_maker import VideoMaker
from modules.audio_analyzer import AudioAnalyzer
from modules.utils import load_config, ensure_directory
from modules.constants import (
    SEPARATOR_LINE,
    TITLE_EMOJI,
    DOWNLOAD_EMOJI,
    ANALYSIS_EMOJI,
    ZOOM_EMOJI,
    SUBTITLE_EMOJI,
    MUSEUM_EMOJI,
    VIDEO_EMOJI,
    SUCCESS_EMOJI,
    ERROR_EMOJI,
    DEFAULT_ARTIST
)


def parse_arguments() -> argparse.Namespace:
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(description='명화 숏폼 자동화')
    parser.add_argument('--image-url', required=True, help='이미지 URL')
    parser.add_argument('--title', required=True, help='작품 제목')
    parser.add_argument('--artist', default=DEFAULT_ARTIST, help='작가명')
    parser.add_argument('--scenes-file', required=True, help='장면 텍스트 파일 (필수)')
    parser.add_argument('--artwork-info', required=False, help='작품 정보 JSON')
    parser.add_argument('--audio', required=False, help='배경 음악 파일명 (input/sounds/ 폴더에서 자동 검색, 선택)')

    return parser.parse_args()


def load_scenes(scenes_file: str) -> List[str]:
    """
    장면 텍스트 파일 로드

    Args:
        scenes_file: 장면 파일 경로

    Returns:
        장면 텍스트 리스트

    Raises:
        ValueError: 장면 텍스트가 비어있는 경우
    """
    with open(scenes_file, 'r', encoding='utf-8') as f:
        scenes = [line.strip() for line in f if line.strip()]

    if not scenes:
        raise ValueError("장면 텍스트가 비어있습니다.")

    return scenes


def parse_artwork_info(args: argparse.Namespace) -> List[str]:
    """
    작품 정보 파싱

    Args:
        args: 명령행 인자

    Returns:
        작품 정보 리스트
    """
    if args.artwork_info:
        return json.loads(args.artwork_info)
    else:
        return [
            args.title.replace('_', ' '),
            args.artist
        ]


def print_header(args: argparse.Namespace, scenes: List[str], artwork_info: List[str]) -> None:
    """
    실행 정보 출력

    Args:
        args: 명령행 인자
        scenes: 장면 리스트
        artwork_info: 작품 정보
    """
    print(SEPARATOR_LINE)
    print(f"{TITLE_EMOJI} 명화 숏폼 자동화 시스템")
    print(SEPARATOR_LINE)
    print(f"작품: {args.title}")
    print(f"작가: {args.artist}")
    print(f"장면: {len(scenes)}개")
    print(f"작품 정보: {len(artwork_info)}줄")
    print(f"시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEPARATOR_LINE)


def setup_directories(config: Dict[str, Any], title: str) -> tuple:
    """
    작업 디렉토리 설정

    Args:
        config: 설정 딕셔너리
        title: 작품 제목

    Returns:
        (base_dir, input_image_dir, input_sounds_dir, output_dir, zoomed_dir, subtitled_dir)
    """
    base_dir = Path(__file__).parent
    input_image_dir = base_dir / config['paths']['input_image_dir']
    input_sounds_dir = base_dir / config['paths']['input_sounds_dir']
    output_dir = base_dir / config['paths']['output_dir'] / title.replace(' ', '_')

    ensure_directory(input_image_dir)
    ensure_directory(input_sounds_dir)
    ensure_directory(output_dir)

    zoomed_dir = output_dir / "zoomed"
    subtitled_dir = output_dir / "subtitled"

    return base_dir, input_image_dir, input_sounds_dir, output_dir, zoomed_dir, subtitled_dir


def process_artwork(
    config: Dict[str, Any],
    args: argparse.Namespace,
    scenes: List[str],
    artwork_info: List[str],
    input_image_dir: Path,
    input_sounds_dir: Path,
    output_dir: Path,
    zoomed_dir: Path,
    subtitled_dir: Path
) -> Path:
    """
    명화 처리 파이프라인

    Args:
        config: 설정 딕셔너리
        args: 명령행 인자
        scenes: 장면 리스트
        artwork_info: 작품 정보
        input_image_dir: 입력 이미지 디렉토리
        input_sounds_dir: 입력 음악 디렉토리
        output_dir: 출력 디렉토리
        zoomed_dir: 확대 이미지 디렉토리
        subtitled_dir: 자막 이미지 디렉토리

    Returns:
        최종 영상 경로
    """
    # 1. 이미지 다운로드
    print(f"\n[1/6] {DOWNLOAD_EMOJI} 이미지 다운로드")
    processor = ImageProcessor(config)

    image_path = input_image_dir / f"{args.title.replace(' ', '_')}.jpg"
    if not processor.download_image(args.image_url, image_path):
        raise Exception("이미지 다운로드 실패")

    # 2. Claude 분석
    print(f"\n[2/6] {ANALYSIS_EMOJI} Claude 좌표 분석")
    analyzer = ClaudeAnalyzer(config)
    result = analyzer.analyze(image_path, scenes)

    if not result['success']:
        raise Exception(f"Claude 분석 실패: {result['error']}")

    coordinates = result['coordinates']

    # 좌표 저장
    coords_file = output_dir / "coordinates.json"
    with open(coords_file, 'w', encoding='utf-8') as f:
        json.dump(coordinates, f, ensure_ascii=False, indent=2)

    # 3. 확대 이미지 생성
    print(f"\n[3/6] {ZOOM_EMOJI} 확대 이미지 생성")
    zoomed_files = processor.generate_zoomed_images(
        image_path, coordinates, zoomed_dir
    )

    # 4. 자막 합성
    print(f"\n[4/6] {SUBTITLE_EMOJI} 자막 합성")
    subtitle_maker = SubtitleMaker(config)
    subtitle_texts = [coord['text'] for coord in coordinates]
    subtitled_files = subtitle_maker.add_subtitles(
        zoomed_files, subtitle_texts, subtitled_dir
    )

    # 5. 마지막 장면 - 원본 이미지 (미술관 스타일)
    print(f"\n[5/6] {MUSEUM_EMOJI} 원본 이미지 장면 생성")
    final_scene = processor.create_museum_view(
        image_path,
        artwork_info,
        output_dir / "final_scene.jpg"
    )

    # 자막 없이 추가
    subtitled_files.append(final_scene)

    # 6. 오디오 분석 (선택적)
    scene_timings = None
    audio_file_path = None

    if args.audio:
        # 오디오 파일 경로 설정 (input/sounds/ 폴더 하드코딩)
        if Path(args.audio).is_absolute():
            # 절대 경로가 주어진 경우 그대로 사용
            audio_file_path = Path(args.audio)
        else:
            # 파일명만 주어진 경우 input/sounds/ 경로 추가
            audio_file_path = input_sounds_dir / args.audio

        if not audio_file_path.exists():
            print(f"  ⚠️  오디오 파일을 찾을 수 없습니다: {audio_file_path}")
            print(f"  파일을 input/sounds/ 폴더에 넣어주세요.")
            audio_file_path = None  # 파일이 없으면 None으로 설정
        else:
            print(f"\n[6/7] 🎵 오디오 분석")
            print(f"  파일: {audio_file_path.name}")

            if config.get('audio', {}).get('enabled', False):
                audio_analyzer = AudioAnalyzer(config)

                # 장면 수 계산 (자막 장면 + 마지막 원본 장면)
                num_scenes = len(scenes) + 1

                # 오디오 분석
                audio_analysis = audio_analyzer.analyze(audio_file_path)

                if audio_analysis:
                    # 장면을 타이밍에 맞춰 배치
                    sync_strategy = config.get('audio', {}).get('sync_strategy', 'auto')
                    scene_timings = audio_analyzer.distribute_scenes_to_timings(
                        num_scenes, audio_analysis, sync_strategy
                    )
                    print(f"  ✓ {len(scene_timings)}개 장면을 음악 리듬에 동기화")
                else:
                    print("  ⚠️  오디오 분석 실패, 텍스트 길이 기반으로 진행")
            else:
                print("  ⚠️  오디오 동기화 비활성화 (config.json에서 활성화 가능)")

    # 7. 영상 생성
    step_num = "[7/7]" if args.audio else "[6/6]"
    print(f"\n{step_num} {VIDEO_EMOJI} 영상 생성")
    video_maker = VideoMaker(config)
    final_video = output_dir / f"{args.title.replace(' ', '_')}.mp4"

    # 텍스트 리스트 (마지막 장면은 None)
    all_texts = subtitle_texts + [None]

    if not video_maker.create_video(
        subtitled_files,
        all_texts,
        audio_file_path,
        final_video,
        scene_timings
    ):
        raise Exception("영상 생성 실패")

    return final_video


def print_summary(final_video: Path) -> None:
    """
    완료 요약 출력

    Args:
        final_video: 최종 영상 경로
    """
    file_size = final_video.stat().st_size / (1024 * 1024)

    print("\n" + SEPARATOR_LINE)
    print(f"{SUCCESS_EMOJI} 완료!")
    print(SEPARATOR_LINE)
    print(f"최종 영상: {final_video}")
    print(f"크기: {file_size:.2f}MB")
    print(SEPARATOR_LINE)


def main():
    """메인 함수"""
    try:
        # 인자 파싱
        args = parse_arguments()

        # 설정 로드
        config = load_config()

        # 장면 텍스트 로드
        scenes = load_scenes(args.scenes_file)

        # 작품 정보 파싱
        artwork_info = parse_artwork_info(args)

        # 헤더 출력
        print_header(args, scenes, artwork_info)

        # 디렉토리 설정
        _, input_image_dir, input_sounds_dir, output_dir, zoomed_dir, subtitled_dir = setup_directories(
            config, args.title
        )

        # 처리 파이프라인 실행
        final_video = process_artwork(
            config, args, scenes, artwork_info,
            input_image_dir, input_sounds_dir, output_dir, zoomed_dir, subtitled_dir
        )

        # 완료 요약
        print_summary(final_video)

    except Exception as e:
        print(f"\n{ERROR_EMOJI} 오류 발생: {e}")
        raise


if __name__ == "__main__":
    main()
