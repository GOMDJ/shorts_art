# 명화 숏폼 자동화 시스템

명화 이미지를 분석하여 자동으로 숏폼 영상을 생성하는 시스템입니다.

## 주요 기능

- **자동 이미지 분석**: Claude AI를 활용하여 명화의 주요 부분을 자동으로 분석하고 좌표 추출
- **확대 이미지 생성**: 분석된 좌표를 기반으로 명화의 세부 부분을 확대한 이미지 생성
- **자막 합성**: 각 장면에 맞는 자막을 자동으로 합성
- **미술관 스타일 연출**: 마지막 장면에 작품 정보를 포함한 미술관 스타일 이미지 생성
- **🎵 배경음악 리듬 동기화**: 음악의 비트와 강조 지점에 맞춰 장면 전환 (NEW!)
- **숏폼 비디오 제작**: 모든 장면을 조합하여 최종 숏폼 영상 생성

## 요구사항

- **Python**: 3.13.2 (권장) 또는 3.11+
- **FFmpeg**: 영상 처리용 (필수)
- **API Keys**: Anthropic Claude API (필수), OpenAI API (TTS 사용 시)

## 빠른 시작

### 1. 설치

```bash
# 저장소 클론 (또는 다운로드)
cd shorts_art

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# FFmpeg 설치 (macOS)
brew install ffmpeg
```

자세한 설치 가이드는 [INSTALL.md](INSTALL.md)를 참고하세요.

### 2. 환경 설정

```bash
# API 키 설정 파일 생성
touch ~/Desktop/.env.shorts

# .env.shorts 파일에 추가
echo "ANTHROPIC_API_KEY=your_key_here" >> ~/Desktop/.env.shorts
echo "OPENAI_API_KEY=your_key_here" >> ~/Desktop/.env.shorts
```

### 3. 폰트 파일 준비

```bash
mkdir -p fonts
# NanumGothicBold.ttf를 fonts/ 디렉토리에 복사
```

## 프로젝트 구조

```
shorts_art/
├── main.py              # 메인 실행 파일
├── run.py               # 대화형 메뉴 실행 파일
├── database.py          # SQLite DB 관리
├── config.json          # 설정 파일
├── shorts_art.db        # SQLite 데이터베이스
├── HOW_TO_ADD.md        # 새 명화 추가 가이드
├── modules/             # 핵심 처리 모듈
│   ├── claude_analyzer.py    # Claude AI 이미지 분석
│   ├── image_processor.py    # 이미지 처리 및 확대
│   ├── subtitle_maker.py     # 자막 생성
│   ├── video_maker.py        # 비디오 생성
│   ├── audio_analyzer.py     # 오디오 분석 (리듬 동기화)
│   ├── tts_generator.py      # TTS 생성
│   ├── utils.py              # 공통 유틸리티
│   └── constants.py          # 상수 정의
├── scenes/              # 장면 텍스트 파일
├── fonts/               # 자막용 폰트 파일
├── input/               # 입력 파일
│   ├── paintings.json   # 작품 목록 데이터
│   ├── image/           # 명화 이미지 저장
│   └── sounds/          # 배경 음악 파일 저장
├── output/              # 출력 영상 저장
├── requirements.txt     # Python 패키지 목록
├── INSTALL.md           # 설치 가이드
├── setup.sh             # 초기 설정 스크립트
└── .gitignore           # Git 무시 파일
```

## 사용 방법

### 1. 대화형 메뉴 실행 (권장)

```bash
python run.py
```

20개의 사전 설정된 명화 중에서 선택하여 실행할 수 있습니다:

- The Scream (절규) - Edvard Munch
- Medusa (메두사) - Caravaggio
- Saturn Devouring His Son (아들을 잡아먹는 사투르누스) - Francisco Goya
- The Starry Night (별이 빛나는 밤) - Vincent van Gogh
- 그 외 16개 명화

### 2. 직접 실행

**기본 사용법:**
```bash
python main.py \
  --image-url "https://example.com/painting.jpg" \
  --title "작품명" \
  --artist "작가명" \
  --scenes-file "scenes/01_example.txt" \
  --artwork-info '["작품명", "작가(연도)", "제작년도, 재료", "크기", "소장처"]'
```

**배경음악 포함 (리듬 동기화):**
```bash
# 먼저 음악 파일을 input/sounds/ 폴더에 복사
cp background_music.mp3 input/sounds/

# 파일명만 지정하면 자동으로 input/sounds/에서 찾음
python main.py \
  --image-url "https://example.com/painting.jpg" \
  --title "작품명" \
  --artist "작가명" \
  --scenes-file "scenes/01_example.txt" \
  --audio "background_music.mp3"
```

**파라미터 설명:**
- `--image-url`: 명화 이미지 URL (필수)
- `--title`: 작품 제목 (필수)
- `--artist`: 작가명 (선택, 기본값: "Unknown Artist")
- `--scenes-file`: 장면 텍스트 파일 경로 (필수)
- `--artwork-info`: 작품 정보 JSON (선택)
- `--audio`: 배경 음악 파일명 (선택, `input/sounds/` 폴더에서 자동 검색)

## 처리 과정

1. **이미지 다운로드** - 지정된 URL에서 명화 이미지 다운로드
2. **Claude 분석** - AI가 이미지를 분석하여 각 장면의 최적 좌표 추출
3. **확대 이미지 생성** - 추출된 좌표를 기반으로 확대 이미지 생성
4. **자막 합성** - 각 확대 이미지에 장면 텍스트 자막 합성
5. **원본 장면 생성** - 작품 정보가 포함된 미술관 스타일 마지막 장면 생성
6. **오디오 분석** (선택) - 배경음악의 비트/강조 지점 추출하여 장면 타이밍 계산
7. **영상 생성** - 모든 장면을 조합하여 최종 MP4 영상 생성
   - 리듬 동기화 모드: 음악의 비트에 맞춰 장면 전환
   - 기본 모드: 텍스트 길이 기반 장면 시간 계산

## 출력 파일

각 작품별로 `output/작품명/` 디렉토리에 다음 파일들이 생성됩니다:

- `coordinates.json` - Claude가 분석한 좌표 데이터
- `zoomed/` - 확대 이미지들
- `subtitled/` - 자막이 합성된 이미지들
- `final_scene.jpg` - 작품 정보가 포함된 마지막 장면
- `작품명.mp4` - 최종 숏폼 영상

## 데이터베이스

프로젝트는 SQLite를 사용하여 작업 내역을 관리합니다:

- **videos** 테이블: 비디오 프로젝트 정보
- **scenes** 테이블: 각 장면의 텍스트 및 좌표
- **outputs** 테이블: 최종 결과물 정보

## 새로운 명화 추가하기

새로운 명화를 추가하려면 `HOW_TO_ADD.md`를 참고하세요.

간단 요약:
1. `scenes/XX_작품명.txt` 파일 생성
2. `input/paintings.json` 파일에 작품 정보 추가
3. Wikimedia Commons에서 고해상도 이미지 URL 찾기

## 🎵 배경음악 리듬 동기화 기능

### 작동 방식

1. **오디오 분석**: librosa를 사용하여 음악 파일 분석
   - BPM(템포) 계산
   - 비트(박자) 타이밍 추출
   - 강조 지점(드럼 킥, 베이스 등) 감지

2. **장면 배치 전략** (`config.json`에서 설정)
   - `auto`: 비트와 강조 지점을 결합하여 자동 선택 (기본값)
   - `beats`: 비트에 맞춰 장면 전환
   - `onsets`: 강조 지점에 맞춰 전환
   - `evenly`: 균등 분할

3. **동기화 결과**
   - 음악의 강렬한 순간에 장면 전환
   - 자연스러운 리듬감
   - 시청자 몰입도 향상

### 사용 예시

```bash
# 1. 음악 파일을 input/sounds/ 폴더에 넣기
cp epic_music.mp3 input/sounds/

# 2. 파일명만 지정 (경로는 자동)
python main.py \
  --image-url "https://..." \
  --title "The_Scream" \
  --scenes-file "scenes/01_the_scream.txt" \
  --audio "epic_music.mp3"
```

### 설정 예시 (config.json)

```json
{
  "audio": {
    "enabled": true,
    "sync_strategy": "auto",
    "min_scene_interval": 0.5
  }
}
```

## 개발 예정 기능

다음 기능들이 개발 예정입니다:

1. 자막 타이밍 랜덤화 (1.0~1.2초)
2. 명사 하이라이트 (1~3문장마다 랜덤 색상 변경)
3. 다중 인물 확대 시 중앙값 개선
4. 확대 좌표 미세 랜덤화 (±0.02 픽셀)
5. ✅ ~~배경음악 리듬에 맞춘 장면 전환~~ (완료!)
6. ✅ ~~음악 강조 타이밍과 자막/이미지 동기화~~ (완료!)

## 기술 스택

### 핵심 라이브러리
- **Python 3.13.2** - 프로그래밍 언어
- **Anthropic Claude API** - AI 이미지 분석
- **Pillow** - 이미지 처리
- **moviepy** - 비디오 생성 및 편집
- **librosa** - 오디오 분석 (리듬 동기화)
- **FFmpeg** - 비디오/오디오 인코딩

### 선택적 라이브러리
- **OpenAI API** - TTS 음성 생성
- **SQLite** - 데이터베이스 관리

### 전체 의존성
자세한 패키지 목록은 [requirements.txt](requirements.txt) 참고

## 라이선스

이 프로젝트는 개인 프로젝트입니다.

## 작성자

nam-yuseong
