
# 꿈 일기 (Dream Diary)

pgvector를 활용한 시맨틱 검색 기반 꿈 일기 애플리케이션입니다. 사용자의 꿈 내용을 벡터로 변환하여 저장하고, 유사한 꿈을 검색할 수 있습니다.

---

## 데모

<img width="1000" height="1000" alt="dreamdiary" src="https://github.com/user-attachments/assets/0b319030-0610-47fc-976a-fde6eb66f690" />

---

## 주요 기능

- 꿈 내용과 감정을 기록
- 시맨틱 검색을 통한 유사한 꿈 찾기
- 사용자별 꿈 관리
- 코사인 거리 기반 유사도 측정

---

## 기술 스택

- **Backend**: FastAPI, Python 3.13
- **Database**: PostgreSQL 18 + pgvector
- **Vector Model**: sentence-transformers (all-MiniLM-L6-v2, 384차원)
- **Container**: Docker, Docker Compose
- **Package Manager**: uv

---

## 시스템 아키텍처

```
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

---

## 프로젝트 구조

```
.
├── Dockerfile              # 멀티 스테이지 빌드 설정
├── docker-compose.yaml     # 서비스 오케스트레이션
├── database.py             # DB 연결 및 초기화
├── main.py                 # FastAPI 엔드포인트
├── vectorizer.py           # 텍스트→벡터 변환
├── index.html              # 웹 UI
├── examples/               # 사용 예제
│   └── vector_demo.py      # 벡터 생성 데모
├── tests/                  # 테스트 코드
│   └── test_main.py        # API 엔드포인트 테스트
├── .github/                # CI/CD 워크플로우
│   └── workflows/
│       ├── ci.yml          # 지속적 통합
│       └── cd.yml          # 지속적 배포 (수동)
├── pyproject.toml          # 프로젝트 의존성
└── uv.lock                 # 의존성 락 파일
```

---

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

### 로컬 개발 환경

```bash
# uv로 의존성 설치
uv sync

# 개발 서버 실행
uv run uvicorn main:app --reload
```

---

## 예제 실행

벡터 생성 과정을 확인하려면:

```bash
python examples/vector_demo.py
```

이 스크립트는 `sentence-transformers` 모델을 사용하여 텍스트를 384차원 벡터로 변환하는 과정을 보여줍니다.

---

## API 문서

### 꿈 기록 추가

```http
POST /add_dream/
Content-Type: application/json

{
  "dream_text": "친구와 함께 여행하는 꿈",
  "dream_feeling": "즐거웠다",
  "user_id": 1
}
```

### 유사한 꿈 검색

```http
GET /search_dreams/?query=친구&user_id=1
```

응답:
```json
{
  "results": [
    {
      "dream_text": "친구와 함께 여행하는 꿈",
      "distance": 0.123
    }
  ]
}
```

---

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

---

## 성능 최적화

- **HNSW 인덱스**: 빠른 근사 최근접 이웃 검색
- **멀티 스테이지 빌드**: 최종 이미지 크기 최소화 (2.24GB)
- **레이어 캐싱**: 빠른 재빌드 (코드 변경 시 ~10초, 첫 빌드 시 ~50분)
- **uv 패키지 매니저**: pip 대비 10배 이상 빠른 의존성 설치

---

## 배포

### 로컬 빌드 및 배포

이 프로젝트는 대용량 ML 의존성(PyTorch, sentence-transformers)으로 인해 GitHub Actions에서 자동 배포가 제한됩니다. 로컬에서 빌드하고 배포하는 것을 권장합니다.

```bash
# 1. 로컬에서 빌드
docker compose build

# 2. Docker Hub에 태그 및 푸시
docker tag pgvector-app:latest your-username/dream-diary:latest
docker push your-username/dream-diary:latest

# 3. 프로덕션 서버에서 배포
docker pull your-username/dream-diary:latest
docker compose up -d
```

### CI/CD

- **CI (지속적 통합)**: 모든 푸시와 PR에 대해 자동으로 테스트 및 빌드 검증 실행
- **CD (지속적 배포)**: 수동 트리거 방식으로 설정 (GitHub Actions의 디스크 공간 제약)

---

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `DB_HOST` | `localhost` | PostgreSQL 호스트 |
| `DB_NAME` | `dream_db` | 데이터베이스 이름 |
| `DB_USER` | `user` | 데이터베이스 사용자 |
| `DB_PASSWORD` | `password` | 데이터베이스 비밀번호 |

---

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

---

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

**참고:** PostgreSQL 18은 `/var/lib/postgresql`에 데이터를 저장합니다. 이전 버전에서 업그레이드하는 경우 볼륨 마운트 경로를 확인하세요.

### 데이터베이스 연결 실패

앱이 데이터베이스에 연결하지 못하는 경우:
```bash
docker compose ps  # db가 "Healthy" 상태인지 확인
docker compose logs db  # 데이터베이스 로그 확인
```

헬스체크가 설정되어 있어 데이터베이스가 준비된 후 앱이 시작됩니다.

---

## 참고 자료  
  
- [pgvector 공식 문서](https://github.com/pgvector/pgvector)
- [sentence-transformers](https://www.sbert.net/)  
- [FastAPI 문서](https://fastapi.tiangolo.com/)

