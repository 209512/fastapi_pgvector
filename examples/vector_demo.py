"""벡터 생성 데모 스크립트

사용법:
    python examples/vector_demo.py
"""
from vectorizer import get_vector

# 검색하고 싶은 새로운 꿈 텍스트를 입력하세요.
texts_to_encode = [
    '새로운 친구를 만나는 꿈을 꿨다. 설렜다.'
]

if __name__ == "__main__":
    print("--- 생성된 벡터 (384차원) ---")
    for text in texts_to_encode:
        embedding = get_vector(text)
        print(f"'{text}'의 벡터:")
        print(embedding)
        print("-" * 20)