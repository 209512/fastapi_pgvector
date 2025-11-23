import psycopg2
import os

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "dream_db"),
            user=os.getenv("DB_USER", "user"),
            password=os.getenv("DB_PASSWORD", "password")
        )
        return conn
    except psycopg2.Error as e:
        print(f"데이터베이스 연결 오류: {e}")
        raise

def init_db():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = get_db_connection()
    cur = conn.cursor()

    # pgvector 확장 활성화  
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 테이블 생성  
    cur.execute("""
                CREATE TABLE IF NOT EXISTS dream_records (
                                                             id SERIAL PRIMARY KEY,
                                                             dream_text TEXT NOT NULL,
                                                             dream_vector vector(384),
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

    # HNSW 인덱스 생성  
    cur.execute("""
                CREATE INDEX IF NOT EXISTS dream_vector_idx
                    ON dream_records
                    USING hnsw (dream_vector vector_cosine_ops)
                    WITH (m = 16, ef_construction = 64);
                """)

    conn.commit()
    cur.close()
    conn.close()