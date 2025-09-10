# 🎯 SNS RAG LLM - 스마트 콘텐츠 생성기

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-green.svg)](https://openai.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com)

> **AI 기반 SNS 콘텐츠 및 리뷰 자동 생성 시스템**  
> RAG(Retrieval-Augmented Generation) 기술을 활용하여 사업장별 맞춤형 마케팅 콘텐츠를 생성합니다.

## 🌟 주요 기능

### 📱 **SNS 콘텐츠 생성**
- **Instagram, Facebook, Twitter/X, Blog** 포스트 자동 생성
- **업종별 맞춤형** 콘텐츠 (카페, 펜션, 레스토랑 등)
- **5가지 다양한 스타일** 지원 (캐주얼, 나열형, 강조형, 추천형, 간단형)

### ⭐ **리뷰 생성 시스템**
- **네이버 지도 리뷰** 자동 생성
- **구글 리뷰** 지원
- **실제 시설 정보 반영** (수영장, 카페 메뉴 등)
- **자연스러운 한국어 표현** 패턴 적용

### 🔧 **기술적 특징**
- **RAG 기술**: 사업장 정보 기반 정확한 콘텐츠 생성
- **업종별 프롬프트**: 카페 vs 숙박업소 등 차별화된 접근
- **자연스러움 분석**: 실제 리뷰 패턴 분석 및 점수화
- **배치 생성**: A/B 테스트용 다양한 버전 생성

## 🚀 빠른 시작

### 1. 설치

```bash
git clone https://github.com/yourusername/snsragllm.git
cd snsragllm
pip install -r requirements.txt
```

### 2. 환경 설정

```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 또는 config.yaml 수정
cp config.yaml config_local.yaml
# config_local.yaml에서 OpenAI API 키 설정
```

### 3. 실행

#### 🖥️ **웹 인터페이스 (Streamlit)**
```bash
streamlit run app.py
```

#### 🌐 **API 서버 (FastAPI)**
```bash
python api.py
```

#### ⚙️ **시스템 체크**
```bash
python start.py
```

## 📊 사용 예시

### SNS 콘텐츠 생성
```python
from content_generator.enhanced_review_generator import EnhancedReviewGenerator

generator = EnhancedReviewGenerator()

# 카페 Instagram 포스트 생성
result = generator.create_improved_review_with_analysis(
    business_id="cafe_001",
    rating=5
)

print(result['review_text'])
# 출력: "아메리카노 진짜 맛있어요~^^ 원두 직접 로스팅하는거 같던데 향이 좋더라고요 ㅋㅋ 재방문 의사 있어요👍"
```

### 다양한 스타일 리뷰
```python
# 5가지 스타일 자동 선택
for i in range(5):
    review = generator.create_naver_review_with_business_info("pension_001")
    print(f"스타일 {i+1}: {review['review_text']}")
```

## 🏗️ 프로젝트 구조

```
snsragllm/
├── 📁 content_generator/          # 콘텐츠 생성 엔진
│   ├── enhanced_review_generator.py  # 메인 생성기
│   ├── guide_generator.py           # 가이드 생성
│   └── ...
├── 📁 data_sources/               # 데이터 관리
│   ├── business_info.py            # 사업장 정보 관리
│   └── ...
├── 📁 data/                       # 사업장 데이터
│   └── business_profiles.json      # 사업장 프로필
├── 📁 tests/                      # 테스트 파일
├── 🖥️ app.py                     # Streamlit 웹앱
├── 🌐 api.py                     # FastAPI 서버
├── ⚙️ config.yaml               # 설정 파일
└── 📝 requirements.txt           # 의존성
```

## 🎨 지원하는 콘텐츠 유형

### **SNS 플랫폼별**
- **Instagram**: 해시태그, 이모티콘 최적화
- **Facebook**: 스토리텔링 중심
- **Twitter/X**: 140자 제한 최적화
- **Blog**: 상세한 정보 제공

### **업종별 특화**
- **☕ 카페**: 메뉴, 맛, 분위기 중심
- **🏨 숙박**: 시설, 뷰, 가족여행 경험
- **🍽️ 레스토랑**: 요리, 서비스, 가격
- **🛍️ 기타**: 범용 비즈니스 콘텐츠

### **스타일 다양성**
1. **캐주얼**: 이모티콘, 친근한 말투
2. **나열형**: 숫자로 정리된 체계적 정보
3. **강조형**: 감탄사, 강조 표현
4. **추천형**: 지인 추천, 경험 공유
5. **간단형**: 핵심만 간결하게

## 🔧 고급 기능

### **자연스러움 분석**
- 실제 리뷰 패턴 분석
- 자연스러운 표현 검증
- 100점 만점 점수화

### **실제 시설 정보 반영**
- 수영장 없는 펜션 → 수영장 언급 제외
- 실제 메뉴 정보 활용
- 부정확한 정보 방지

### **업종별 프롬프트**
```python
# 카페 전용 키워드
카페_키워드 = ["아메리카노", "라떼", "분위기", "원두"]

# 펜션 전용 키워드  
펜션_키워드 = ["객실", "수영장", "자쿠지", "가족여행"]
```

## 🧪 테스트

```bash
# 다양한 스타일 테스트
python test_diverse_reviews.py

# 숙박업소 테스트
python test_accommodation_reviews.py

# 시설 정보 반영 테스트
python test_pension_no_pool.py
```

## 📈 성능 지표

- **자연스러움 점수**: 평균 90+ / 100
- **스타일 다양성**: 5가지 스타일 랜덤 적용
- **업종 정확도**: 실제 시설 정보 100% 반영
- **생성 속도**: 평균 3-5초/리뷰

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 👨‍💻 개발자

**Jay** - [GitHub](https://github.com/yourusername)

## 🙏 감사인사

- OpenAI GPT-3.5-turbo API
- Streamlit 커뮤니티
- FastAPI 프레임워크

---

⭐ **이 프로젝트가 도움이 되었다면 Star를 눌러주세요!**
