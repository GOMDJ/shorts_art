#!/bin/bash

# 명화 숏폼 자동화 시스템 초기 설정 스크립트

echo "🎨 명화 숏폼 자동화 시스템 설정 시작..."

# 필요한 디렉토리 생성
echo "📁 디렉토리 생성 중..."
mkdir -p input/image
mkdir -p input/sounds
mkdir -p output
mkdir -p fonts
mkdir -p scenes

echo "✅ 디렉토리 생성 완료"
echo "   - input/image/  : 명화 이미지 저장"
echo "   - input/sounds/ : 배경음악 파일 저장"

# 환경 변수 파일 생성 (존재하지 않는 경우)
ENV_FILE="$HOME/Desktop/.env.shorts"

if [ ! -f "$ENV_FILE" ]; then
    echo "🔑 환경 변수 파일 생성 중..."
    cat > "$ENV_FILE" << EOF
# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
EOF
    echo "✅ 환경 변수 파일 생성 완료: $ENV_FILE"
    echo "⚠️  API 키를 입력해주세요!"
else
    echo "✓ 환경 변수 파일이 이미 존재합니다: $ENV_FILE"
fi

# Python 버전 확인
echo ""
echo "🐍 Python 버전 확인 중..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "현재 Python 버전: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" < "3.11" ]]; then
    echo "⚠️  Python 3.11 이상이 필요합니다!"
    echo "현재 버전: $PYTHON_VERSION"
fi

# 가상환경 확인
echo ""
if [ -d "venv" ]; then
    echo "✓ 가상환경이 이미 존재합니다"
else
    echo "📦 가상환경 생성 중..."
    python -m venv venv
    echo "✅ 가상환경 생성 완료"
fi

# 활성화 안내
echo ""
echo "🚀 다음 단계:"
echo ""
echo "1. 가상환경 활성화:"
echo "   source venv/bin/activate"
echo ""
echo "2. 패키지 설치:"
echo "   pip install -r requirements.txt"
echo ""
echo "3. FFmpeg 설치 (아직 안 했다면):"
echo "   brew install ffmpeg  # macOS"
echo "   sudo apt install ffmpeg  # Ubuntu/Debian"
echo ""
echo "4. 폰트 파일 복사:"
echo "   fonts/ 디렉토리에 NanumGothicBold.ttf 복사"
echo ""
echo "5. API 키 설정:"
echo "   $ENV_FILE 파일 편집"
echo ""
echo "6. 실행:"
echo "   python run.py"
echo ""
echo "✨ 설정 완료!"
