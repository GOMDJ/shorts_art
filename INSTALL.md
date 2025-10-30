# 설치 가이드

## Python 버전 확인

이 프로젝트는 **Python 3.13.2**에서 테스트되었습니다.

```bash
python --version
# Python 3.13.2
```

## 1. 가상환경 생성 (권장)

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

## 2. 패키지 설치

```bash
pip install -r requirements.txt
```

## 3. FFmpeg 설치 (필수)

moviepy는 FFmpeg를 사용하므로 시스템에 FFmpeg가 설치되어 있어야 합니다.

### macOS (Homebrew)
```bash
brew install ffmpeg
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows
1. [FFmpeg 공식 사이트](https://ffmpeg.org/download.html)에서 다운로드
2. 압축 해제 후 `bin` 폴더를 시스템 PATH에 추가

### FFmpeg 설치 확인
```bash
ffmpeg -version
```

## 4. 환경 변수 설정

1. `.env.shorts` 파일 생성 (홈 디렉토리의 Desktop 폴더)
   ```bash
   # macOS/Linux
   touch ~/Desktop/.env.shorts

   # Windows
   type nul > %USERPROFILE%\Desktop\.env.shorts
   ```

2. API 키 추가
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## 5. 폰트 파일 준비

`fonts/` 디렉토리에 자막용 폰트 파일을 배치하세요.

권장 폰트:
- **NanumGothicBold.ttf** (한글)
- [다운로드](https://hangeul.naver.com/font)

```bash
# fonts 디렉토리 생성
mkdir -p fonts

# 폰트 파일을 fonts/ 디렉토리로 복사
cp /path/to/NanumGothicBold.ttf fonts/
```

## 6. 디렉토리 구조 확인

프로젝트 루트에서 다음 디렉토리들이 생성되어 있는지 확인:

```
shorts_art/
├── fonts/           # 폰트 파일
├── scenes/          # 장면 텍스트 파일
├── input/           # 입력 파일
│   ├── image/       # 명화 이미지 (자동 생성)
│   └── sounds/      # 배경 음악 파일 (선택적)
└── output/          # 출력 영상 (자동 생성)
```

## 7. 배경음악 추가 (선택적)

배경음악을 사용하려면 음악 파일을 `input/sounds/` 폴더에 넣으세요.

```bash
# 음악 파일 복사
cp your_music.mp3 input/sounds/

# 실행 시 파일명만 지정
python main.py \
  --image-url "..." \
  --title "작품명" \
  --scenes-file "scenes/01.txt" \
  --audio "your_music.mp3"
```

## 8. 테스트 실행

```bash
# 도움말 확인
python main.py --help

# 대화형 메뉴 실행
python run.py
```

## 문제 해결

### librosa 설치 오류
```bash
# numba 먼저 설치
pip install numba

# 그 다음 librosa
pip install librosa
```

### moviepy 오류
```bash
# decorator 버전 다운그레이드
pip install decorator==5.1.1

# moviepy 재설치
pip install --upgrade moviepy
```

### PIL/Pillow 오류
```bash
# Pillow 재설치
pip uninstall Pillow
pip install Pillow
```

### Python 3.13 호환성 문제

일부 라이브러리가 Python 3.13에서 아직 완전히 테스트되지 않았을 수 있습니다.
문제가 발생하면 Python 3.11 또는 3.12 사용을 권장합니다.

```bash
# pyenv로 다른 Python 버전 설치
pyenv install 3.12.0
pyenv local 3.12.0
```

## 의존성 업데이트

```bash
# 모든 패키지 업데이트
pip install --upgrade -r requirements.txt

# 특정 패키지만 업데이트
pip install --upgrade anthropic
```

## 개발 환경 설정 (선택적)

코드 수정 및 개발을 위한 추가 도구:

```bash
# 코드 포맷팅
pip install black

# 타입 체크
pip install mypy

# 린팅
pip install pylint
```
