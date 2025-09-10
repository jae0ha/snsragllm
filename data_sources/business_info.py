"""
사업장 정보 관리 모듈
특정 사업장의 상세 정보를 저장하고 관리합니다.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import yaml

class BusinessInfoManager:
    def __init__(self, data_file: str = "data/business_profiles.json"):
        """사업장 정보 관리자 초기화"""
        self.data_file = data_file
        self.businesses = self.load_businesses()
        
        # 데이터 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
    
    def load_businesses(self) -> Dict[str, Dict]:
        """저장된 사업장 정보 로드"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_businesses(self):
        """사업장 정보 저장"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.businesses, f, ensure_ascii=False, indent=2)
    
    def add_business(self, business_id: str, business_info: Dict[str, Any]):
        """새 사업장 정보 추가"""
        business_info['created_at'] = datetime.now().isoformat()
        business_info['updated_at'] = datetime.now().isoformat()
        self.businesses[business_id] = business_info
        self.save_businesses()
        return business_id
    
    def add_business_profile(self, business_profile: 'BusinessProfile') -> str:
        """BusinessProfile 객체를 사용하여 사업장 추가"""
        import uuid
        business_id = str(uuid.uuid4())[:8]  # 8자리 ID 생성
        business_data = business_profile.to_dict()
        return self.add_business(business_id, business_data)
    
    def update_business(self, business_id: str, updates: Dict[str, Any]):
        """사업장 정보 업데이트"""
        if business_id in self.businesses:
            self.businesses[business_id].update(updates)
            self.businesses[business_id]['updated_at'] = datetime.now().isoformat()
            self.save_businesses()
            return True
        return False
    
    def get_business(self, business_id: str) -> Optional[Dict[str, Any]]:
        """사업장 정보 조회"""
        return self.businesses.get(business_id)
    
    def get_all_businesses(self) -> Dict[str, Dict]:
        """모든 사업장 정보 조회"""
        return self.businesses
    
    def delete_business(self, business_id: str) -> bool:
        """사업장 정보 삭제"""
        if business_id in self.businesses:
            del self.businesses[business_id]
            self.save_businesses()
            return True
        return False
    
    def search_businesses(self, query: str) -> List[Dict[str, Any]]:
        """사업장 검색"""
        results = []
        query_lower = query.lower()
        
        for business_id, info in self.businesses.items():
            if (query_lower in info.get('name', '').lower() or 
                query_lower in info.get('type', '').lower() or
                query_lower in info.get('location', '').lower()):
                results.append({
                    'id': business_id,
                    **info
                })
        
        return results

class BusinessProfile:
    """사업장 프로필 클래스"""
    
    def __init__(self, business_id: str = None, name: str = None, business_type: str = None,
                 basic_info: Dict = None, menu_info: Dict = None, service_info: Dict = None,
                 atmosphere_info: Dict = None, location_info: Dict = None, 
                 marketing_info: Dict = None, customer_info: Dict = None):
        self.business_id = business_id
        self.name = name
        self.type = business_type
        self.basic_info = basic_info or {}
        self.menu_info = menu_info or {}
        self.service_info = service_info or {}
        self.atmosphere_info = atmosphere_info or {}
        self.location_info = location_info or {}
        self.marketing_info = marketing_info or {}
        self.customer_info = customer_info or {}
        
    def set_basic_info(self, **kwargs):
        """기본 정보 설정"""
        allowed_fields = [
            'description', 'established_year', 'phone', 'website', 
            'operating_hours', 'price_range', 'capacity'
        ]
        for key, value in kwargs.items():
            if key in allowed_fields:
                self.basic_info[key] = value
    
    def set_menu_info(self, signature_dishes: List[str] = None, 
                     popular_items: List[str] = None,
                     price_examples: Dict[str, str] = None,
                     special_ingredients: List[str] = None):
        """메뉴 정보 설정"""
        self.menu_info = {
            'signature_dishes': signature_dishes or [],
            'popular_items': popular_items or [],
            'price_examples': price_examples or {},
            'special_ingredients': special_ingredients or []
        }
    
    def set_service_info(self, services: List[str] = None,
                        staff_specialties: List[str] = None,
                        unique_features: List[str] = None):
        """서비스 정보 설정"""
        self.service_info = {
            'services': services or [],
            'staff_specialties': staff_specialties or [],
            'unique_features': unique_features or []
        }
    
    def set_atmosphere_info(self, interior_style: str = None,
                           mood_keywords: List[str] = None,
                           best_time_to_visit: List[str] = None,
                           suitable_occasions: List[str] = None):
        """분위기 정보 설정"""
        self.atmosphere_info = {
            'interior_style': interior_style,
            'mood_keywords': mood_keywords or [],
            'best_time_to_visit': best_time_to_visit or [],
            'suitable_occasions': suitable_occasions or []
        }
    
    def set_location_info(self, address: str = None,
                         nearby_landmarks: List[str] = None,
                         parking_info: str = None,
                         transportation: Dict[str, str] = None):
        """위치 정보 설정"""
        self.location_info = {
            'address': address,
            'nearby_landmarks': nearby_landmarks or [],
            'parking_info': parking_info,
            'transportation': transportation or {}
        }
    
    def set_marketing_info(self, target_audience: List[str] = None,
                          key_selling_points: List[str] = None,
                          competitive_advantages: List[str] = None,
                          brand_personality: List[str] = None):
        """마케팅 정보 설정"""
        self.marketing_info = {
            'target_audience': target_audience or [],
            'key_selling_points': key_selling_points or [],
            'competitive_advantages': competitive_advantages or [],
            'brand_personality': brand_personality or []
        }
    
    def set_customer_info(self, regular_customer_types: List[str] = None,
                         peak_hours: List[str] = None,
                         customer_feedback_themes: List[str] = None):
        """고객 정보 설정"""
        self.customer_info = {
            'regular_customer_types': regular_customer_types or [],
            'peak_hours': peak_hours or [],
            'customer_feedback_themes': customer_feedback_themes or []
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """프로필을 딕셔너리로 변환"""
        return {
            'business_id': self.business_id,
            'name': self.name,
            'type': self.type,
            'basic_info': self.basic_info,
            'menu_info': self.menu_info,
            'service_info': self.service_info,
            'atmosphere_info': self.atmosphere_info,
            'location_info': self.location_info,
            'marketing_info': self.marketing_info,
            'customer_info': self.customer_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """딕셔너리에서 프로필 생성"""
        profile = cls(
            business_id=data['business_id'],
            name=data['name'],
            business_type=data['type']
        )
        
        profile.basic_info = data.get('basic_info', {})
        profile.menu_info = data.get('menu_info', {})
        profile.service_info = data.get('service_info', {})
        profile.atmosphere_info = data.get('atmosphere_info', {})
        profile.location_info = data.get('location_info', {})
        profile.marketing_info = data.get('marketing_info', {})
        profile.customer_info = data.get('customer_info', {})
        
        return profile

def create_sample_business():
    """샘플 사업장 생성"""
    profile = BusinessProfile("cafe_001", "모던 브루 카페", "카페")
    
    profile.set_basic_info(
        description="로스팅부터 브루잉까지 모든 과정을 직접 하는 스페셜티 커피 전문점",
        established_year=2020,
        phone="02-1234-5678",
        operating_hours="07:00-22:00 (연중무휴)",
        price_range="5,000-12,000원",
        capacity="30석"
    )
    
    profile.set_menu_info(
        signature_dishes=["시그니처 블렌드", "콜드브루", "플랫화이트"],
        popular_items=["아메리카노", "카페라떼", "크로와상", "치즈케이크"],
        price_examples={"아메리카노": "5,000원", "카페라떼": "6,000원", "디저트": "6,000-8,000원"},
        special_ingredients=["직접 로스팅 원두", "유기농 우유", "수제 시럽"]
    )
    
    profile.set_service_info(
        services=["테이크아웃", "딜리버리", "단체 주문", "원두 판매"],
        staff_specialties=["바리스타 자격증 보유", "커피 원두 상담"],
        unique_features=["원두 로스팅 구경 가능", "커피 클래스 운영"]
    )
    
    profile.set_atmosphere_info(
        interior_style="모던 인더스트리얼",
        mood_keywords=["아늑한", "세련된", "조용한", "집중하기 좋은"],
        best_time_to_visit=["오전 시간대", "오후 2-4시"],
        suitable_occasions=["업무 미팅", "데이트", "혼자 시간", "친구 모임"]
    )
    
    profile.set_location_info(
        address="서울시 강남구 테헤란로 123",
        nearby_landmarks=["강남역 2번 출구", "삼성전자 빌딩", "코엑스"],
        parking_info="건물 지하 주차장 이용 가능 (2시간 무료)",
        transportation={"지하철": "강남역 도보 5분", "버스": "강남역 정류장"}
    )
    
    profile.set_marketing_info(
        target_audience=["직장인", "카페 애호가", "커플", "프리랜서"],
        key_selling_points=["신선한 직접 로스팅", "프리미엄 원두", "전문 바리스타"],
        competitive_advantages=["합리적 가격", "접근성 좋은 위치", "일관된 품질"],
        brand_personality=["전문적", "친근한", "신뢰할 수 있는"]
    )
    
    profile.set_customer_info(
        regular_customer_types=["근처 직장인", "카페 마니아", "대학생"],
        peak_hours=["07:30-09:00", "12:00-13:00", "15:00-17:00"],
        customer_feedback_themes=["커피 맛이 좋다", "분위기가 좋다", "직원이 친절하다"]
    )
    
    # BusinessInfoManager를 사용하여 저장하고 ID 반환
    manager = BusinessInfoManager()
    business_id = manager.add_business(profile.business_id, profile.to_dict())
    return business_id

if __name__ == "__main__":
    # 테스트 코드
    manager = BusinessInfoManager()
    
    # 기존 카페 샘플 생성
    sample_business = create_sample_business()
    manager.add_business("cafe_001", sample_business.to_dict())
    
    # 펜션 샘플 생성
    pension_profile = BusinessProfile("pension_001", "바다뷰 펜션", "펜션")
    
    pension_profile.set_basic_info(
        description="바다가 보이는 전망 좋은 펜션으로 가족 단위 여행객에게 인기",
        established_year=2018,
        phone="033-1234-5678",
        operating_hours="체크인 15:00, 체크아웃 11:00",
        price_range="80,000-150,000원/박",
        capacity="8개 객실 (최대 32명)"
    )
    
    pension_profile.set_menu_info(
        signature_dishes=["바베큐 세트", "해물라면", "조식 서비스"],
        popular_items=["객실 바베큐", "수영장 이용", "자쿠지"],
        price_examples={"바베큐 세트": "30,000원", "조식": "10,000원/인", "추가 침구": "15,000원"},
        special_ingredients=["신선한 해산물", "지역 특산품"]
    )
    
    pension_profile.set_service_info(
        services=["바베큐장 제공", "수영장", "자쿠지", "주차장"],
        staff_specialties=["24시간 관리사 상주", "짐 운반 서비스"],
        unique_features=["오션뷰 전 객실", "프라이빗 수영장", "반려동물 동반 가능"]
    )
    
    pension_profile.set_atmosphere_info(
        interior_style="모던 리조트",
        mood_keywords=["힐링", "바다뷰", "가족친화적", "로맨틱"],
        best_time_to_visit=["일몰 시간", "새벽 일출"],
        suitable_occasions=["가족여행", "커플여행", "친구모임", "워크숍"]
    )
    
    pension_profile.set_location_info(
        address="강원도 양양군 현남면 해안로 456",
        nearby_landmarks=["낙산해수욕장", "설악산국립공원", "양양국제공항"],
        parking_info="무료 주차장 15대 가능",
        transportation={"버스": "양양터미널에서 20분", "자차": "서울에서 2시간"}
    )
    
    pension_profile.set_marketing_info(
        target_audience=["가족 여행객", "커플", "친구 그룹", "워크숍 단체"],
        key_selling_points=["오션뷰", "깨끗한 시설", "합리적 가격"],
        competitive_advantages=["바다 바로 앞", "다양한 부대시설", "친절한 서비스"],
        brand_personality=["편안한", "가족적", "신뢰할 수 있는"]
    )
    
    pension_profile.set_customer_info(
        regular_customer_types=["가족 단위", "연인", "친구 그룹"],
        peak_hours=["체크인 시간", "바베큐 시간", "일몰 시간"],
        customer_feedback_themes=["뷰가 좋다", "깨끗하다", "친절하다", "시설이 좋다"]
    )
    
    manager.add_business("pension_001", pension_profile.to_dict())
    
    print("샘플 사업장 정보가 생성되었습니다!")
    print(f"저장된 사업장 수: {len(manager.get_all_businesses())}")
    
    # 생성된 데이터 확인
    for biz_id in manager.get_all_businesses():
        biz = manager.get_business(biz_id)
        print(f"- {biz_id}: {biz['name']} ({biz['type']})")
