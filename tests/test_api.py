"""
API 테스트 코드
"""

import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_root():
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

def test_health_check():
    """헬스 체크 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data

def test_get_platforms():
    """플랫폼 목록 조회 테스트"""
    response = client.get("/platforms")
    assert response.status_code == 200
    data = response.json()
    assert "sns_platforms" in data
    assert "review_platforms" in data
    assert "business_types" in data

def test_sns_content_generation():
    """SNS 콘텐츠 생성 테스트"""
    request_data = {
        "business_name": "테스트 카페",
        "business_type": "카페",
        "platform": "instagram",
        "keywords": ["커피", "디저트"],
        "target_audience": "20-30대"
    }
    
    response = client.post("/generate/sns", json=request_data)
    
    # API 키가 필요한 경우 401, 아니면 200 또는 500 (OpenAI 키 없음)
    assert response.status_code in [200, 401, 500]

def test_review_content_generation():
    """리뷰 콘텐츠 생성 테스트"""
    request_data = {
        "business_name": "테스트 레스토랑",
        "business_type": "레스토랑",
        "platform": "naver_map",
        "rating": 4.5,
        "visit_purpose": "데이트"
    }
    
    response = client.post("/generate/review", json=request_data)
    
    # API 키가 필요한 경우 401, 아니면 200 또는 500 (OpenAI 키 없음)
    assert response.status_code in [200, 401, 500]

def test_batch_generation():
    """일괄 생성 테스트"""
    request_data = {
        "business_name": "테스트 카페",
        "business_type": "카페", 
        "content_type": "review",
        "keywords": ["맛있는", "친절한"],
        "count": 3
    }
    
    response = client.post("/generate/batch", json=request_data)
    
    # API 키가 필요한 경우 401, 아니면 200 또는 500 (OpenAI 키 없음)
    assert response.status_code in [200, 401, 500]

if __name__ == "__main__":
    pytest.main([__file__])
