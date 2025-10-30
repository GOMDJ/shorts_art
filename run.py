"""
대화형 메뉴 실행 파일
"""
import json
from pathlib import Path
import subprocess
from typing import List, Dict, Any


def load_paintings() -> List[Dict[str, Any]]:
    """
    작품 목록을 JSON 파일에서 로드

    Returns:
        작품 정보 딕셔너리 리스트

    Raises:
        FileNotFoundError: paintings.json 파일이 없는 경우
        json.JSONDecodeError: JSON 파싱 실패 시
    """
    paintings_file = Path(__file__).parent / "input" / "paintings.json"

    if not paintings_file.exists():
        raise FileNotFoundError(
            f"작품 목록 파일을 찾을 수 없습니다: {paintings_file}\n"
            "input/paintings.json 파일을 생성해주세요."
        )

    with open(paintings_file, 'r', encoding='utf-8') as f:
        paintings = json.load(f)

    print(f"✓ {len(paintings)}개 작품 로드 완료")
    return paintings


def show_menu(paintings: List[Dict[str, Any]]):
    """메뉴 출력"""
    print("\n" + "=" * 60)
    print("🎨 명화 숏폼 자동화 시스템")
    print("=" * 60)

    for p in paintings:
        print(f"{p['id']:2d}. {p['title']:<40s} - {p['artist']}")

    print("\n99. 전체 실행")
    print(" 0. 종료")
    print("=" * 60)


def run_painting(painting):
    """작품 실행"""
    print(f"\n▶️  실행 중: {painting['title']}")
    print(f"   작가: {painting['artist']}")
    print(f"   장면 파일: {painting['scenes_file']}")
    
    # main.py 실행
    cmd = [
        "python", "main.py",
        "--image-url", painting['url'],
        "--title", painting['title'].replace(' ', '_'),
        "--artist", painting['artist'],
        "--scenes-file", painting['scenes_file'],
        "--artwork-info", json.dumps(painting['artwork_info'], ensure_ascii=False)
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 완료: {painting['title']}")
    except subprocess.CalledProcessError as e:
        print(f"❌ 실패: {painting['title']}")
    except KeyboardInterrupt:
        print(f"\n⏹️  중단됨: {painting['title']}")
        raise


def main():
    """메인 루프"""
    try:
        # 작품 목록 로드
        paintings = load_paintings()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 오류: {e}")
        return

    while True:
        show_menu(paintings)

        try:
            choice = input("\n선택 (번호 입력): ").strip()

            if choice == '0':
                print("👋 종료합니다.")
                break

            elif choice == '99':
                # 전체 실행
                print(f"\n🚀 전체 {len(paintings)}개 작품 실행")
                confirm = input("계속하시겠습니까? (y/n): ").strip().lower()

                if confirm == 'y':
                    for i, painting in enumerate(paintings, 1):
                        print(f"\n[{i}/{len(paintings)}]")
                        run_painting(painting)
                    print("\n✅ 전체 실행 완료!")
                else:
                    print("취소됨")

            else:
                # 개별 실행
                try:
                    idx = int(choice)
                    painting = next((p for p in paintings if p['id'] == idx), None)

                    if painting:
                        run_painting(painting)
                    else:
                        print(f"❌ 잘못된 번호: {idx}")

                except ValueError:
                    print("❌ 숫자를 입력하세요")

        except KeyboardInterrupt:
            print("\n\n👋 종료합니다.")
            break

        except Exception as e:
            print(f"❌ 오류: {e}")


if __name__ == "__main__":
    main()
