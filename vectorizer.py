from sentence_transformers import SentenceTransformer

# 모델을 한 번만 로드하여 재사용
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_vector(text: str):
    """주어진 텍스트를 벡터로 변환합니다."""
    return model.encode(text).tolist()
