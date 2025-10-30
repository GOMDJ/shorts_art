# 명화 숏폼 장면 모음

## 사용법
```bash
python main.py --image-url "이미지URL" --title "작품명" --scenes-file scenes/파일명.txt --no-tts
```

## 장면 리스트

### 01. The Slave Ship (J.M.W. Turner, 1840)
- 파일: `01_slave_ship.txt`
- 주제: 폭풍우 속 생존 의지
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Slave-ship.jpg/1280px-Slave-ship.jpg

### 02. Ophelia (John Everett Millais, 1851-1852)
- 파일: `02_ophelia.txt`
- 주제: 광기와 익사
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/John_Everett_Millais_-_Ophelia_-_Google_Art_Project.jpg/1280px-John_Everett_Millais_-_Ophelia_-_Google_Art_Project.jpg

### 03. Cardinals (Jean-Georges Vibert, 1870s)
- 파일: `03_cardinals.txt`
- 주제: 종교적 위선과 탐욕
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Jean-Georges_Vibert_-_The_Diet_of_Worms.jpg/1280px-Jean-Georges_Vibert_-_The_Diet_of_Worms.jpg

### 04. Vanitas Still Life (Various Artists, 17th century)
- 파일: `04_vanitas.txt`
- 주제: 삶의 덧없음
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Pieter_Claesz_-_Vanitas_-_WGA04974.jpg/1280px-Pieter_Claesz_-_Vanitas_-_WGA04974.jpg

### 05. The Despair (Edvard Munch, 1892)
- 파일: `05_despair.txt`
- 주제: 절망과 자살 충동
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Edvard_Munch_-_Despair_%281892%29.jpg/1280px-Edvard_Munch_-_Despair_%281892%29.jpg

### 06. The Death Bed (Edvard Munch, 1895)
- 파일: `06_deathbed.txt`
- 주제: 고독한 죽음
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Edvard_Munch_-_Death_in_the_Sickroom_-_Google_Art_Project.jpg/1280px-Edvard_Munch_-_Death_in_the_Sickroom_-_Google_Art_Project.jpg

### 07. The Scholar (Rembrandt, 1631)
- 파일: `07_scholar.txt`
- 주제: 지식과 죽음
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Rembrandt_-_The_Scholar_in_his_Study.jpg/1280px-Rembrandt_-_The_Scholar_in_his_Study.jpg

### 08. Judith and Holofernes (Artemisia Gentileschi, 1620)
- 파일: `08_heroine.txt`
- 주제: 여전사의 복수
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Gentileschi_Artemisia_Judith_Beheading_Holofernes_Naples.jpg/1280px-Gentileschi_Artemisia_Judith_Beheading_Holofernes_Naples.jpg

### 09. The Death of Caesar (Vincenzo Camuccini, 1804-1805)
- 파일: `09_betrayal.txt`
- 주제: 배신과 죽음
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Death_of_Caesar_by_Vincenzo_Camuccini.jpg/1280px-Death_of_Caesar_by_Vincenzo_Camuccini.jpg

### 10. The Last Letter (James Tissot, 1870s)
- 파일: `10_waiting.txt`
- 주제: 돌아오지 않는 사랑
- URL: https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/James_Tissot_-_Bad_News_%28The_Parting%29.jpg/1280px-James_Tissot_-_Bad_News_%28The_Parting%29.jpg

## 실행 예시
```bash
# Ophelia
python main.py --image-url "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/John_Everett_Millais_-_Ophelia_-_Google_Art_Project.jpg/1280px-John_Everett_Millais_-_Ophelia_-_Google_Art_Project.jpg" --title "Ophelia" --scenes-file scenes/02_ophelia.txt --no-tts

# Vanitas
python main.py --image-url "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Pieter_Claesz_-_Vanitas_-_WGA04974.jpg/1280px-Pieter_Claesz_-_Vanitas_-_WGA04974.jpg" --title "Vanitas" --scenes-file scenes/04_vanitas.txt --no-tts
```
