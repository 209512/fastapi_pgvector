# Stage 1: 빌더 단계
FROM python:3.13.5 AS builder

WORKDIR /app

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 의존성 파일만 먼저 복사
COPY pyproject.toml .

# uv로 의존성 설치 (pip보다 10-100배 빠름)
RUN uv pip install --system .

# Stage 2: 최종 단계
FROM python:3.13.5-slim

WORKDIR /app

# 빌더에서 설치된 패키지와 실행 파일 복사
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 소스 코드는 마지막에 복사(코드 변경 시 의존성 재설치 방지)
COPY . .

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]