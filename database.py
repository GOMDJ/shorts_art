"""
DB 관리 스크립트
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import json


class ShortsDB:
    def __init__(self, db_path="shorts_art.db"):
        self.db_path = Path(db_path)
        self.conn = None
        self.init_db()
    
    def connect(self):
        """DB 연결"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # dict 형태로 반환
        return self.conn
    
    def close(self):
        """DB 연결 종료"""
        if self.conn:
            self.conn.close()
    
    def init_db(self):
        """DB 초기화"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # videos 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            image_url TEXT NOT NULL,
            image_path TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
        """)
        
        # scenes 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            scene_number INTEGER NOT NULL,
            text TEXT NOT NULL,
            x REAL,
            y REAL,
            zoom REAL,
            image_path TEXT,
            FOREIGN KEY (video_id) REFERENCES videos(id)
        )
        """)
        
        # outputs 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS outputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            coordinates_json TEXT,
            final_video_path TEXT,
            duration REAL,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos(id)
        )
        """)
        
        conn.commit()
        self.close()
        print(f"✅ DB 초기화 완료: {self.db_path}")
    
    def create_video(self, title, image_url, scenes):
        """
        새 비디오 프로젝트 생성
        
        Args:
            title: 제목
            image_url: 이미지 URL
            scenes: 장면 텍스트 리스트 (8개)
        
        Returns:
            video_id
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # video 레코드 생성
        cursor.execute("""
        INSERT INTO videos (title, image_url, status)
        VALUES (?, ?, 'pending')
        """, (title, image_url))
        
        video_id = cursor.lastrowid
        
        # scenes 레코드 생성
        for i, text in enumerate(scenes, 1):
            cursor.execute("""
            INSERT INTO scenes (video_id, scene_number, text)
            VALUES (?, ?, ?)
            """, (video_id, i, text))
        
        conn.commit()
        self.close()
        
        print(f"✅ 비디오 생성: ID={video_id}, 장면={len(scenes)}개")
        return video_id
    
    def update_video_status(self, video_id, status):
        """비디오 상태 업데이트"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
        UPDATE videos 
        SET status = ?, completed_at = ?
        WHERE id = ?
        """, (status, datetime.now() if status == 'completed' else None, video_id))
        
        conn.commit()
        self.close()
    
    def update_scene_coordinates(self, video_id, coordinates):
        """
        장면 좌표 업데이트
        
        Args:
            video_id: 비디오 ID
            coordinates: [{"scene": 1, "x": 0.5, "y": 0.5, "zoom": 1.5}, ...]
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        for coord in coordinates:
            cursor.execute("""
            UPDATE scenes 
            SET x = ?, y = ?, zoom = ?
            WHERE video_id = ? AND scene_number = ?
            """, (coord['x'], coord['y'], coord['zoom'], 
                  video_id, coord['scene']))
        
        conn.commit()
        self.close()
        
        print(f"✅ 좌표 업데이트: video_id={video_id}")
    
    def save_output(self, video_id, coordinates_json, final_video_path, duration, file_size):
        """최종 결과 저장"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO outputs (video_id, coordinates_json, final_video_path, duration, file_size)
        VALUES (?, ?, ?, ?, ?)
        """, (video_id, json.dumps(coordinates_json, ensure_ascii=False), 
              str(final_video_path), duration, file_size))
        
        conn.commit()
        self.close()
        
        print(f"✅ 결과 저장: video_id={video_id}")
    
    def get_video(self, video_id):
        """비디오 정보 조회"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        video = dict(cursor.fetchone())
        
        cursor.execute("SELECT * FROM scenes WHERE video_id = ? ORDER BY scene_number", (video_id,))
        video['scenes'] = [dict(row) for row in cursor.fetchall()]
        
        self.close()
        return video
    
    def list_videos(self, limit=10):
        """비디오 목록 조회"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM videos 
        ORDER BY created_at DESC 
        LIMIT ?
        """, (limit,))
        
        videos = [dict(row) for row in cursor.fetchall()]
        self.close()
        
        return videos


# 사용 예시
if __name__ == "__main__":
    # DB 초기화
    db = ShortsDB("shorts_art.db")
    
    # 새 프로젝트 생성
    video_id = db.create_video(
        title="Saturn Devouring His Son",
        image_url="https://upload.wikimedia.org/wikipedia/commons/8/82/Francisco_de_Goya.jpg",
        scenes=[
            "사투르누스가 아들을 움켜쥔다",
            "입을 크게 벌린다",
            "아들의 몸을 물어뜯는다",
            "손톱이 살을 파고든다",
            "피가 흐른다",
            "눈은 광기로 부릅뜬다",
            "머리는 이미 뜯겨나갔다",
            "팔 하나도 사라졌다"
        ]
    )
    
    # 상태 업데이트
    db.update_video_status(video_id, 'processing')
    
    # 좌표 저장
    db.update_scene_coordinates(video_id, [
        {"scene": 1, "x": 0.5, "y": 0.6, "zoom": 1.2},
        {"scene": 2, "x": 0.4, "y": 0.3, "zoom": 2.0},
        # ...
    ])
    
    # 완료
    db.update_video_status(video_id, 'completed')
    
    # 조회
    video = db.get_video(video_id)
    print(json.dumps(video, indent=2, ensure_ascii=False))
    
    # 목록
    videos = db.list_videos(10)
    for v in videos:
        print(f"{v['id']}. {v['title']} - {v['status']}")
