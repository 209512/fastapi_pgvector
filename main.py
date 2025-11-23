from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from database import get_db_connection, init_db
from vectorizer import get_vector


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작 시 데이터베이스 초기화
    init_db()
    yield
    # 종료 시 정리 작업 (필요시)


app = FastAPI(lifespan=lifespan)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class DreamRecord(BaseModel):
    dream_text: str
    dream_feeling: str
    user_id: int


@app.post("/add_dream/")
async def add_dream_record(dream: DreamRecord):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        combined_text = f"{dream.dream_text} {dream.dream_feeling}"
        embedding = get_vector(combined_text)

        # 벡터를 PostgreSQL 형식으로 변환
        vector_str = "[" + ",".join(map(str, embedding)) + "]"

        sql = "INSERT INTO dream_records (dream_text, dream_vector, user_id) VALUES (%s, %s, %s)"
        cur.execute(sql, (combined_text, vector_str, dream.user_id))

        conn.commit()
        cur.close()
        conn.close()

        return {"status": "success", "message": "꿈 기록이 성공적으로 추가되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search_dreams/")
async def search_dreams(query: str, user_id: int = None):
    if not query:
        raise HTTPException(status_code=400, detail="검색 쿼리를 입력해 주세요.")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query_embedding = get_vector(query)
        vector_str = "[" + ",".join(map(str, query_embedding)) + "]"

        if user_id is not None:
            sql = """
                  SELECT dream_text, dream_vector <=> %s AS distance
                  FROM dream_records
                  WHERE user_id = %s
                  ORDER BY dream_vector <=> %s
                      LIMIT 5 \
                  """
            cur.execute(sql, (vector_str, user_id, vector_str))
        else:
            sql = """
                  SELECT dream_text, dream_vector <=> %s AS distance
                  FROM dream_records
                  ORDER BY dream_vector <=> %s
                      LIMIT 5 \
                  """
            cur.execute(sql, (vector_str, vector_str))

        results = cur.fetchall()
        cur.close()
        conn.close()

        search_results = [{"dream_text": row[0], "distance": row[1]} for row in results]

        return {"results": search_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/", StaticFiles(directory=".", html=True), name="static")
