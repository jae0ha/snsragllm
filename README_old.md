# SNS 및 네이버맵 리뷰 광고 콘텐츠 생성 시스템

**RAG 기반 마케팅 자동화 도구**

이 프로젝트는 기존 RAG 시스템을 확장하여 SNS 게시물과 네이버맵 리뷰 등 광고 콘텐츠를 자동 생성하는 마케팅 자동화 도구입니다.

## 🎯 주요 기능

### 1. SNS 콘텐츠 생성
- **인스타그램 게시물**: 해시태그 최적화, 시각적 매력적인 캡션
- **페이스북 포스트**: 참여도 높은 콘텐츠, 타겟 오디언스 맞춤
- **트위터/X 글**: 간결하고 임팩트 있는 메시지
- **블로그 포스트**: SEO 최적화된 장문 콘텐츠

### 2. 네이버맵 리뷰 생성
- **자연스러운 리뷰**: 실제 방문객처럼 작성된 리뷰
- **키워드 최적화**: 검색 노출 최대화
- **감정 분석**: 긍정적이면서 신뢰할 수 있는 톤
- **세부 평가**: 맛, 서비스, 분위기 등 항목별 평가

### 3. 광고 콘텐츠 최적화
- **타겟 맞춤**: 연령대, 성별, 관심사별 콘텐츠 커스터마이징
- **트렌드 반영**: 실시간 트렌드 키워드 반영
- **A/B 테스트**: 여러 버전의 콘텐츠 생성
- **성과 분석**: 콘텐츠 퍼포먼스 예측

## 📂 프로젝트 구조

```
snsRagLlm/
├── app.py                              # 메인 애플리케이션
├── api.py                              # FastAPI 서버
├── config.yaml                         # 설정 파일
├── requirements.txt                    # 의존성
├── content_generator/                  # 콘텐츠 생성 모듈
│   ├── sns_generator.py               # SNS 콘텐츠 생성기
│   ├── review_generator.py            # 리뷰 생성기
│   ├── hashtag_optimizer.py           # 해시태그 최적화
│   └── trend_analyzer.py              # 트렌드 분석
├── data_sources/                      # 데이터 소스 관리
│   ├── business_info.py               # 비즈니스 정보 처리
│   ├── competitor_analysis.py         # 경쟁사 분석
│   └── market_research.py             # 시장 조사 데이터
├── rag_system/                        # RAG 시스템 (기존 시스템 확장)
│   ├── vectorstore_manager.py         # 벡터 저장소
│   ├── retrieval_engine.py            # 검색 엔진
│   └── content_context.py             # 콘텐츠 컨텍스트 관리
├── templates/                         # 콘텐츠 템플릿
│   ├── sns_templates/                 # SNS 템플릿
│   └── review_templates/              # 리뷰 템플릿
├── utils/                             # 유틸리티
│   ├── text_processor.py              # 텍스트 처리
│   ├── keyword_extractor.py           # 키워드 추출
│   └── content_validator.py           # 콘텐츠 검증
└── tests/                             # 테스트 코드
    ├── test_generators.py
    └── test_api.py
```

## 🚀 시작하기

### 설치
```bash
pip install -r requirements.txt
```

### 실행
```bash
python app.py
```

### API 서버 실행
```bash
python api.py
```

## 📋 사용 예시

### SNS 포스트 생성
```python
from content_generator.sns_generator import SNSGenerator

generator = SNSGenerator()
post = generator.create_instagram_post(
    business_name="맛있는 카페",
    keywords=["커피", "디저트", "데이트"],
    target_audience="20-30대 여성"
)
```

### 네이버맵 리뷰 생성
```python
from content_generator.review_generator import ReviewGenerator

generator = ReviewGenerator()
review = generator.create_naver_review(
    business_name="맛있는 카페",
    business_type="카페",
    rating=4.5,
    visit_purpose="데이트"
)
```

## 🔧 설정

`config.yaml` 파일에서 다음 설정을 구성하세요:
- OpenAI API 키
- 생성 모델 설정
- 콘텐츠 가이드라인
- 타겟 플랫폼 설정

## ⚠️ 중요 고지사항

이 도구는 마케팅 목적으로 제작되었습니다. 사용 시 다음 사항을 준수해주세요:
- 각 플랫폼의 이용약관 준수
- 허위 정보 생성 금지
- 윤리적 마케팅 가이드라인 준수
- 관련 법규 및 규정 준수

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
