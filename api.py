"""
FastAPI 서버 - RESTful API 엔드포인트 제공
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import yaml
from datetime import datetime
import uvicorn

from content_generator.sns_generator import SNSGenerator
from content_generator.review_generator import ReviewGenerator

# Pydantic 모델 정의
class SNSRequest(BaseModel):
    business_name: str
    business_type: str
    platform: str  # instagram, facebook, twitter, blog
    keywords: List[str]
    target_audience: Optional[str] = "20-30대"
    style: Optional[str] = "친근한"
    include_hashtags: Optional[bool] = True
    topic: Optional[str] = None  # blog용
    target_length: Optional[int] = 2000  # blog용

class ReviewRequest(BaseModel):
    business_name: str
    business_type: str
    platform: str  # naver_map, google_review, detailed
    rating: float
    visit_purpose: Optional[str] = None
    specific_menu: Optional[str] = None
    cuisine_type: Optional[str] = None  # detailed용
    price_range: Optional[str] = None  # detailed용
    visited_menu: Optional[List[str]] = None  # detailed용

class BatchRequest(BaseModel):
    business_name: str
    business_type: str
    content_type: str  # sns, review
    platform: Optional[str] = None
    keywords: List[str]
    count: int = 3

class ContentResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: str

# FastAPI 앱 초기화
app = FastAPI(
    title="SNS & 리뷰 콘텐츠 생성 API",
    description="RAG 기반 마케팅 자동화 도구 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 설정 로드
try:
    with open('config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    config = {}

# 생성기 인스턴스
sns_generator = SNSGenerator()
review_generator = ReviewGenerator()

# API 키 검증 (선택사항)
async def verify_api_key(x_api_key: str = Header(None)):
    """API 키 검증"""
    if config.get('security', {}).get('api_key_required', False):
        if not x_api_key:
            raise HTTPException(status_code=401, detail="API 키가 필요합니다")
        # 여기에 실제 API 키 검증 로직 추가
    return x_api_key

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "SNS & 리뷰 콘텐츠 생성 API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "sns_generator": "available",
            "review_generator": "available"
        }
    }

@app.post("/generate/sns", response_model=ContentResponse)
async def generate_sns_content(
    request: SNSRequest,
    api_key: str = Depends(verify_api_key)
):
    """SNS 콘텐츠 생성"""
    try:
        if request.platform.lower() == "instagram":
            result = sns_generator.create_instagram_post(
                business_name=request.business_name,
                business_type=request.business_type,
                keywords=request.keywords,
                target_audience=request.target_audience,
                style=request.style,
                include_hashtags=request.include_hashtags
            )
        elif request.platform.lower() == "facebook":
            result = sns_generator.create_facebook_post(
                business_name=request.business_name,
                business_type=request.business_type,
                keywords=request.keywords,
                target_audience=request.target_audience
            )
        elif request.platform.lower() in ["twitter", "x"]:
            result = sns_generator.create_twitter_post(
                business_name=request.business_name,
                keywords=request.keywords
            )
        elif request.platform.lower() == "blog":
            if not request.topic:
                raise HTTPException(status_code=400, detail="블로그 포스트에는 주제가 필요합니다")
            result = sns_generator.create_blog_post(
                business_name=request.business_name,
                business_type=request.business_type,
                topic=request.topic,
                keywords=request.keywords,
                target_length=request.target_length
            )
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 플랫폼입니다")
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ContentResponse(
            success=True,
            data=result,
            message="SNS 콘텐츠가 성공적으로 생성되었습니다",
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.post("/generate/review", response_model=ContentResponse)
async def generate_review_content(
    request: ReviewRequest,
    api_key: str = Depends(verify_api_key)
):
    """리뷰 콘텐츠 생성"""
    try:
        if request.platform.lower() == "naver_map":
            result = review_generator.create_naver_review(
                business_name=request.business_name,
                business_type=request.business_type,
                rating=request.rating,
                visit_purpose=request.visit_purpose,
                specific_menu=request.specific_menu
            )
        elif request.platform.lower() == "google_review":
            result = review_generator.create_google_review(
                business_name=request.business_name,
                business_type=request.business_type,
                rating=request.rating
            )
        elif request.platform.lower() == "detailed":
            if request.business_type not in ["카페", "레스토랑", "패스트푸드", "베이커리"]:
                raise HTTPException(status_code=400, detail="상세 리뷰는 음식점만 지원됩니다")
            
            result = review_generator.create_detailed_restaurant_review(
                restaurant_name=request.business_name,
                cuisine_type=request.cuisine_type or "일반",
                price_range=request.price_range or "보통",
                rating=request.rating,
                visited_menu=request.visited_menu or []
            )
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 플랫폼입니다")
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ContentResponse(
            success=True,
            data=result,
            message="리뷰 콘텐츠가 성공적으로 생성되었습니다",
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.post("/generate/batch", response_model=ContentResponse)
async def generate_batch_content(
    request: BatchRequest,
    api_key: str = Depends(verify_api_key)
):
    """일괄 콘텐츠 생성"""
    try:
        if request.content_type.lower() == "sns":
            if not request.platform:
                raise HTTPException(status_code=400, detail="SNS 일괄 생성에는 플랫폼이 필요합니다")
            
            results = sns_generator.generate_multiple_versions(
                content_type=request.platform.lower(),
                business_name=request.business_name,
                business_type=request.business_type,
                keywords=request.keywords
            )
        
        elif request.content_type.lower() == "review":
            results = review_generator.generate_review_batch(
                business_name=request.business_name,
                business_type=request.business_type,
                count=request.count
            )
        
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 콘텐츠 타입입니다")
        
        # 에러가 있는 결과 필터링
        successful_results = [r for r in results if "error" not in r]
        
        return ContentResponse(
            success=True,
            data={
                "results": successful_results,
                "total_generated": len(successful_results),
                "total_requested": request.count
            },
            message=f"{len(successful_results)}개의 콘텐츠가 성공적으로 생성되었습니다",
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@app.get("/platforms")
async def get_supported_platforms():
    """지원되는 플랫폼 목록"""
    return {
        "sns_platforms": ["instagram", "facebook", "twitter", "blog"],
        "review_platforms": ["naver_map", "google_review", "detailed"],
        "business_types": [
            "카페", "레스토랑", "패스트푸드", "베이커리", "바", 
            "호텔", "펜션", "쇼핑몰", "미용실", "헬스장", "기타"
        ]
    }

@app.get("/config")
async def get_config_info():
    """설정 정보 (민감한 정보 제외)"""
    safe_config = {
        "app": config.get("app", {}),
        "platforms": config.get("content_generation", {}).get("platforms", {}),
        "target_audience": config.get("target_audience", {}),
        "quality_control": config.get("quality_control", {})
    }
    return safe_config

if __name__ == "__main__":
    # 개발 서버 실행
    uvicorn.run(
        "api:app",
        host=config.get("app", {}).get("host", "0.0.0.0"),
        port=config.get("app", {}).get("port", 8000),
        reload=config.get("app", {}).get("debug", True)
    )
