# 명화 숏폼 추가 가이드

## 📝 새로운 명화 추가 방법

### 1️⃣ 장면 텍스트 파일 생성

**위치:** `scenes/` 폴더

**파일명 규칙:** `XX_작품명.txt`
- 예: `12_nighthawks.txt`

**내용:** 한 줄에 장면 하나씩
```
첫 번째 장면 텍스트
두 번째 장면 텍스트
세 번째 장면 텍스트
...
```

---

### 2️⃣ paintings.json에 작품 정보 추가

**위치:** `input/paintings.json` 파일

**형식:**
```json
{
    "id": 21,
    "title": "Nighthawks",
    "artist": "Edward Hopper",
    "scenes_file": "scenes/21_nighthawks.txt",
    "url": "https://upload.wikimedia.org/wikipedia/commons/...",
    "artwork_info": [
        "밤을 지새우는 사람들",
        "에드워드 호퍼(1882~1967)",
        "1942, 캔버스에 유채",
        "84.1 X 152.4 cm",
        "시카고 미술관"
    ]
}
```

**추가 위치:** JSON 배열 맨 아래에 추가

---

### 3️⃣ 이미지 URL 찾는 법

1. Wikimedia Commons 접속
2. 작품명 검색
3. 이미지 클릭 → "Use this file" → "Original file" 링크 복사
4. **주의:** `/thumb/` 없는 원본 URL 사용

---

## ✅ 예시: The Starry Night 추가

### 1. 장면 파일 생성
**파일:** `scenes/12_starry_night.txt`
```
밤하늘이 소용돌이친다
별들이 춤을 춘다
마을은 고요하다
교회 첨탑이 하늘을 찌른다
사이프러스 나무가 불꽃처럼 타오른다
달이 모든 것을 비춘다
광기와 아름다움이 공존한다
고흐는 정신병원 창문 너머를 그렸다
이것은 악몽이 아니라 꿈이다
혼돈 속에서 발견한 질서
절망 속에서 피어난 희망
```

### 2. paintings.json 수정
```json
[
  ... 기존 작품들 ...,
  {
    "id": 21,
    "title": "The Starry Night",
    "artist": "Vincent van Gogh",
    "scenes_file": "scenes/21_starry_night.txt",
    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/2560px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
    "artwork_info": [
      "별이 빛나는 밤",
      "빈센트 반 고흐(1853~1890)",
      "1889, 캔버스에 유채",
      "73.7 X 92.1 cm",
      "뉴욕 현대미술관"
    ]
  }
]
```

---

## 🎯 요약

**추가할 때 필요한 것:**
1. `scenes/XX_작품명.txt` - 장면 텍스트
2. `input/paintings.json` - 작품 정보 추가
3. Wikimedia URL - 이미지 링크

끝!

추가할거
1. 자막타이밍 랜덤 값으로 수정 : 현재 한 단어당 1.2초, 1.0초~1.2초 중 랜덤값으로 선택. 모든 단어가 랜덤으로 설정.
2. 1~3문장마다 랜덤 값으로 명사 하나에 하이라이트(색깔 변경). 하이라이트 추가 후 1~3 랜덤 초기화
3. 확대 수정. 인물 2개 잡으면 그 중앙 값을 확대해서 얼굴이 반|반 쪼개져서 나옴. 2명 얼굴 다 나오게 프롬프트 변경.
4. 확대하는것도 랜덤값 아주 조그맣게 집어 넣기. +-0.02 픽셀 정도
5. 이미지 확대를 할 떄 2번 연속 확대할게 없으면 둘 다 같은 이미지 사용(이건 어려울듯 근데)
6. 배경음 리듬감 맞게 확대 및 자막 삽입
    영상길이만큼 음악 자른 후 음악 부호화시 강조되는 타이밍에 자막삽입/이미지 변경
    
