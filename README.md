
# 꿈 일기 (Dream Diary)

pgvector를 활용한 시맨틱 검색 기반 꿈 일기 애플리케이션입니다. <cite /> 사용자의 꿈 내용을 벡터로 변환하여 저장하고, 유사한 꿈을 검색할 수 있습니다.

## 주요 기능

- 꿈 내용과 감정을 기록
- 시맨틱 검색을 통한 유사한 꿈 찾기
- 사용자별 꿈 관리
- 코사인 거리 기반 유사도 측정

## 기술 스택

- **Backend**: FastAPI, Python 3.13
- **Database**: PostgreSQL 18 + pgvector
- **Vector Model**: sentence-transformers (all-MiniLM-L6-v2, 384차원)
- **Container**: Docker, Docker Compose
- **Package Manager**: uv

## 시스템 아키텍처

```markdown
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  index.html │────▶│  FastAPI     │────▶│  PostgreSQL     │
│  (Frontend) │     │  (Backend)   │     │  + pgvector     │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Sentence     │
                    │ Transformers │
                    └──────────────┘
```

## 설치 및 실행

### 사전 요구사항

- Docker & Docker Compose
- Python 3.13+ (로컬 개발 시)

### Docker로 실행

```bash
# 빌드 및 실행
docker compose up -d

# 로그 확인
docker compose logs -f app

# 종료
docker compose down
```

애플리케이션은 `http://localhost:8000`에서 실행됩니다.

**참고:** PostgreSQL 18은 `/var/lib/postgresql`에 데이터를 저장합니다. 이전 버전에서 업그레이드하는 경우 `docker compose down -v`로 기존 볼륨을 삭제해야 할 수 있습니다.


## 문제 해결

### PostgreSQL 18 볼륨 오류

PostgreSQL 18 이미지로 업그레이드 시 다음 오류가 발생할 수 있습니다:
```
Error: in 18+, these Docker images are configured to store database data...
```

**해결 방법:**
```bash
# 기존 볼륨 삭제 후 재시작
docker compose down -v
docker compose up -d
```

### 데이터베이스 연결 실패

앱이 데이터베이스에 연결하지 못하는 경우, 헬스체크가 제대로 작동하는지 확인하세요:
```bash
docker compose ps  # db가 "Healthy" 상태인지 확인
docker compose logs db  # 데이터베이스 로그 확인
```

## 프로젝트 구조

```text
.
├── Dockerfile              # 멀티 스테이지 빌드 설정
├── docker-compose.yaml     # 서비스 오케스트레이션
├── database.py             # DB 연결 및 초기화
├── main.py                 # FastAPI 엔드포인트
├── vectorizer.py           # 텍스트→벡터 변환
├── index.html              # 웹 UI
├── pyproject.toml          # 프로젝트 의존성
└── uv.lock                 # 의존성 락 파일
```

## API 엔드포인트

### POST /add_dream/
꿈 기록 추가

**Request Body:**
```json
{
  "dream_text": "새로운 친구를 만나는 꿈",
  "dream_feeling": "설렜다",
  "user_id": 1
}
```

### GET /search_dreams/
유사한 꿈 검색

**Query Parameters:**
- `query` (required): 검색어
- `user_id` (optional): 특정 사용자의 꿈만 검색

**Response:**
```json
{
  "results": [
    {
      "dream_text": "친구와 함께 여행하는 꿈",
      "distance": 0.1234
    }
  ]
}
```

## 데이터베이스 스키마

```sql
CREATE TABLE dream_records (
    id SERIAL PRIMARY KEY,
    dream_text TEXT NOT NULL,
    dream_vector vector(384),
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HNSW 인덱스 (코사인 거리)
CREATE INDEX dream_vector_idx 
ON dream_records 
USING hnsw (dream_vector vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

## 성능 최적화

- **HNSW 인덱스**: 빠른 근사 최근접 이웃 검색
- **멀티 스테이지 빌드**: 최종 이미지 크기 최소화
- **레이어 캐싱**: 빠른 재빌드 (코드 변경 시 ~10초)

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `DB_HOST` | `localhost` | PostgreSQL 호스트 |
| `DB_NAME` | `dream_db` | 데이터베이스 이름 |
| `DB_USER` | `user` | 데이터베이스 사용자 |
| `DB_PASSWORD` | `password` | 데이터베이스 비밀번호 |

## 개발 팁

### 빠른 빌드를 위한 캐시 활용

```bash
# --no-cache 사용하지 말 것
docker compose build
```

### 데이터베이스 확인

```bash
# 확장 확인
docker compose exec db psql -U user -d dream_db -c "\dx"

# 테이블 확인
docker compose exec db psql -U user -d dream_db -c "\d dream_records"
```
