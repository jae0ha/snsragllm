"""
향상된 리뷰 생성기
저장된 사업장 정보를 기반으로 더 정확하고 현실적인 리뷰를 생성합니다.
리뷰 자연스러움 분석 및 개선 기능 포함
"""

import yaml
import random
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv
from data_sources.business_info import BusinessInfoManager, BusinessProfile

class EnhancedReviewGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        """향상된 리뷰 생성기 초기화"""
        # .env 파일 로드
        load_dotenv()
        
        # config.yaml 파일 로드
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)
        
        # 환경변수에서 API 키 가져오기
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        
        # OpenAI 클라이언트 설정
        self.client = OpenAI(api_key=api_key)
        self.model = self.config['openai']['model']
        self.temperature = 0.8  # 더 자연스러운 변화를 위해 온도 상승
        
        # 리뷰 설정 로드
        self.review_config = self.config['content_generation']['reviews']
        
        # 사업장 정보 관리자
        self.business_manager = BusinessInfoManager()
        
        # 고객 프로필 템플릿 (더 다양하고 자연스럽게)
        self.customer_profiles = [
            {"age_group": "20대", "style": "간단솔직", "interests": ["맛", "가성비", "인스타감", "분위기"], 
             "tone": "친근한 반말 섞인 존댓말", "length": "간결"},
            {"age_group": "30대", "style": "상세분석", "interests": ["서비스", "품질", "편의시설", "청결도"], 
             "tone": "정중한 존댓말", "length": "보통"},
            {"age_group": "40대", "style": "경험중심", "interests": ["분위기", "가족친화", "주차", "접근성", "안전"], 
             "tone": "차분한 존댓말", "length": "상세"},
            {"age_group": "50대이상", "style": "신중평가", "interests": ["친절함", "청결도", "전통", "서비스", "편안함"], 
             "tone": "정중하고 예의바른", "length": "적당히 상세"},
             
            # 특별한 상황별 프로필 추가
            {"age_group": "가족여행", "style": "실용적", "interests": ["아이친화", "안전", "편의시설", "가족시설"], 
             "tone": "부모 관점의 실용적", "length": "구체적"},
            {"age_group": "커플여행", "style": "감성적", "interests": ["분위기", "프라이버시", "로맨틱", "사진촬영"], 
             "tone": "감성적이고 따뜻한", "length": "감정 위주"},
            {"age_group": "혼행족", "style": "개인적", "interests": ["조용함", "프라이버시", "혼자만의 시간", "힐링"], 
             "tone": "개인적이고 솔직한", "length": "간결하고 솔직"},
            {"age_group": "친구모임", "style": "재미있게", "interests": ["즐거움", "단체활동", "가성비", "접근성"], 
             "tone": "활발하고 재미있게", "length": "생동감 있게"}
        ]
    
    def _build_detailed_business_context(self, business_info: Dict) -> Dict[str, str]:
        """사업장 정보를 리뷰 작성에 최적화된 형태로 구성"""
        context = {}
        
        # 기본 정보
        if business_info.get('basic_info'):
            basic = business_info['basic_info']
            context['description'] = basic.get('description', '')
            context['price_range'] = basic.get('price_range', '')
            context['operating_hours'] = basic.get('operating_hours', '')
        
        # 메뉴 정보 - 리뷰에서 언급할 구체적인 메뉴들
        if business_info.get('menu_info'):
            menu = business_info['menu_info']
            context['signature_dishes'] = menu.get('signature_dishes', [])
            context['popular_items'] = menu.get('popular_items', [])
            context['special_ingredients'] = menu.get('special_ingredients', [])
            context['price_examples'] = menu.get('price_examples', {})
        
        # 서비스 정보
        if business_info.get('service_info'):
            service = business_info['service_info']
            context['unique_features'] = service.get('unique_features', [])
            context['customer_service'] = service.get('customer_service_style', '')
            context['facilities'] = service.get('facilities', [])
        
        # 분위기 정보
        if business_info.get('atmosphere_info'):
            atmosphere = business_info['atmosphere_info']
            context['mood_keywords'] = atmosphere.get('mood_keywords', [])
            context['decoration'] = atmosphere.get('decoration_style', '')
            context['noise_level'] = atmosphere.get('noise_level', '')
            context['lighting'] = atmosphere.get('lighting', '')
            context['suitable_occasions'] = atmosphere.get('suitable_occasions', [])
        
        # 위치 정보
        if business_info.get('location_info'):
            location = business_info['location_info']
            context['accessibility'] = location.get('accessibility', '')
            context['parking'] = location.get('parking_info', '')
            context['nearby_landmarks'] = location.get('nearby_landmarks', [])
        
        # 고객 정보
        if business_info.get('customer_info'):
            customer = business_info['customer_info']
            context['peak_times'] = customer.get('peak_times', [])
            context['waiting_time'] = customer.get('average_waiting_time', '')
            context['reservation_info'] = customer.get('reservation_policy', '')
        
        return context
    
    def _select_review_details(self, business_context: Dict, customer_profile: Dict) -> Dict:
        """고객 프로필에 맞는 리뷰 디테일 선택"""
        details = {}
        
        # 관심사에 따른 메뉴 선택
        if "맛" in customer_profile['interests'] and business_context.get('signature_dishes'):
            details['mentioned_menu'] = random.choice(business_context['signature_dishes'])
        elif business_context.get('popular_items'):
            details['mentioned_menu'] = random.choice(business_context['popular_items'])
        
        # 관심사에 따른 강조점 선택
        if "가성비" in customer_profile['interests'] and business_context.get('price_range'):
            details['price_comment'] = business_context['price_range']
        
        if "분위기" in customer_profile['interests'] and business_context.get('mood_keywords'):
            details['atmosphere_comment'] = random.choice(business_context['mood_keywords'])
        
        if "서비스" in customer_profile['interests'] and business_context.get('unique_features'):
            details['service_comment'] = random.choice(business_context['unique_features'])
        
        # 방문 상황 설정
        if business_context.get('suitable_occasions'):
            details['visit_occasion'] = random.choice(business_context['suitable_occasions'])
        
        return details
    
    def create_naver_review_with_business_info(self,
                                             business_id: str,
                                             rating: int = None,
                                             review_type: str = "일반",
                                             customer_type: str = "random",
                                             specific_experience: str = None) -> Dict[str, any]:
        """사업장 정보를 활용한 네이버 지도 리뷰 생성"""
        
        business_info = self.business_manager.get_business(business_id)
        if not business_info:
            return {"error": f"사업장 정보를 찾을 수 없습니다: {business_id}"}
        
        business_context = self._build_detailed_business_context(business_info)
        business_name = business_info['name']
        business_type = business_info['type']
        
        # 고객 프로필 선택
        if customer_type == "random":
            customer_profile = random.choice(self.customer_profiles)
        else:
            customer_profile = next((p for p in self.customer_profiles if p['age_group'] == customer_type), 
                                  self.customer_profiles[0])
        
        # 평점 자동 설정
        if rating is None:
            rating = random.choices([3, 4, 5], weights=[10, 40, 50])[0]  # 대부분 긍정적
        
        # 리뷰 세부사항 선택
        review_details = self._select_review_details(business_context, customer_profile)
        
        # 업종별 맞춤 프롬프트 생성
        prompt = self._get_business_specific_prompt(business_name, business_type, rating, customer_profile)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.config['openai']['max_tokens']
            )
            
            content = response.choices[0].message.content
            
            result = {
                'review_text': content.replace('리뷰:', '').strip(),
                'rating': rating,
                'platform': 'naver_map',
                'business_id': business_id,
                'business_name': business_name,
                'review_type': review_type,
                'created_at': datetime.now().isoformat(),
                'metadata': {
                    'business_type': business_type,
                    'customer_profile': customer_profile,
                    'review_details': review_details,
                    'specific_experience': specific_experience,
                    'used_business_context': True,
                    'character_count': len(content.replace('리뷰:', '').strip()),
                    'authenticity_score': self._calculate_authenticity_score(business_context, content)
                }
            }
            
            return result
            
        except Exception as e:
            return {"error": f"리뷰 생성 실패: {str(e)}"}
        
    def _get_business_specific_prompt(self, business_name: str, business_type: str, rating: int, customer_profile: Dict) -> str:
        """업종별 맞춤 프롬프트 생성 (실제 시설 정보 반영)"""
        
        # 랜덤하게 스타일 선택 (1-5)
        import random
        style_number = random.randint(1, 5)
        
        # 사업장 실제 시설 정보 가져오기
        business_info = None
        # business_id로 찾기 (create_naver_review_with_business_info에서 전달된 business_id 활용)
        # 현재 business_name만 있으므로 모든 사업장에서 이름으로 찾기
        for biz_id in self.business_manager.get_all_businesses():
            biz = self.business_manager.get_business(biz_id)
            if biz and biz['name'] == business_name:
                business_info = biz
                break
        
        # 실제 시설 키워드 추출
        facility_keywords = []
        if business_info and 'service_info' in business_info and 'facilities' in business_info['service_info']:
            facilities = business_info['service_info']['facilities']
            facility_mapping = {
                '수영장': '수영장',
                '스파': '스파', 
                '자쿠지': '자쿠지',
                '바베큐장': '바베큐',
                '주차장': '주차',
                'Wi-Fi': 'Wi-Fi',
                '에어컨': '에어컨',
                'TV': 'TV',
                '냉장고': '냉장고'
            }
            
            for facility in facilities:
                for key, keyword in facility_mapping.items():
                    if key in facility:
                        facility_keywords.append(keyword)
        
        # 기본 숙박 키워드 + 실제 시설
        base_keywords = ['객실', '침대', '청결', '뷰', '서비스']
        actual_keywords = base_keywords + facility_keywords
        keywords_text = ', '.join(actual_keywords)
        
        # 숙박업종 프롬프트
        if any(keyword in business_type.lower() for keyword in ['펜션', '숙박', '호텔', '빌라', '리조트', '게스트하우스']):
            if style_number == 1:
                # 수영장이 있는 경우와 없는 경우 예시 분리
                if '수영장' in facility_keywords:
                    example = "가족이랑 2박3일 다녀왔는데 완전 좋았어요~^^ 아이들이 수영장에서 신나게 놀았어요 ㅋㅋ 추천드려용👍"
                else:
                    example = "가족이랑 2박3일 다녀왔는데 완전 좋았어요~^^ 객실도 깨끗하고 조용해서 푹 쉬었어요 ㅋㅋ 추천드려용👍"
                    
                return f"""다음 숙박시설에 대한 가족여행 캐주얼 스타일 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 가족이랑 함께한 여행 후기, 이모티콘 사용, 친근한 말투
예시: "{example}"

실제 이용 가능한 시설: {keywords_text}

리뷰만 출력:"""
            elif style_number == 2:
                # 시설 나열 시 실제 시설만 언급
                if '수영장' in facility_keywords:
                    example = "1.위치 조용하고 2.객실 깨끗하고 3.수영장 넓고 4.주차 편리하고.. 모든게 만족스러웠어요!"
                else:
                    example = "1.위치 조용하고 2.객실 깨끗하고 3.뷰 좋고 4.주차 편리하고.. 모든게 만족스러웠어요!"
                    
                return f"""다음 숙박시설에 대한 시설 나열형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 숫자로 시설별 평가 나열
예시: "{example}"

실제 이용 가능한 시설: {keywords_text}

리뷰만 출력:"""
            elif style_number == 3:
                # 강조형도 실제 시설에 맞게
                if '자쿠지' in facility_keywords:
                    example = "와~ 진짜 완벽한 숙소였어요!! 자쿠지 최고!! 다시 가고 싶어요!!"
                else:
                    example = "와~ 진짜 완벽한 숙소였어요!! 뷰 최고!! 다시 가고 싶어요!!"
                    
                return f"""다음 숙박시설에 대한 감탄사 강조형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 감탄사와 강조표현 사용, 특정시설 강조
예시: "{example}"

실제 이용 가능한 시설: {keywords_text}

리뷰만 출력:"""
            elif style_number == 4:
                return f"""다음 숙박시설에 대한 추천 공유형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 동반자와의 경험, 구체적 만족사항, 추천멘트
예시: "부모님 모시고 갔는데 모두 만족하셨어요. 특히 침대가 편안해서 푹 주무셨다고 하시네요. 가족여행지로 강추합니다!"

실제 이용 가능한 시설: {keywords_text}

리뷰만 출력:"""
            else:  # style_number == 5
                return f"""다음 숙박시설에 대한 간단 후기형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 핵심만 간단하게 표현
예시: "깨끗하고 편안했어요. 잘 쉬다 갑니다. 추천해요!"

실제 이용 가능한 시설: {keywords_text}

리뷰만 출력:"""
        
        # 카페/음식점 프롬프트  
        elif any(keyword in business_type.lower() for keyword in ['카페', '커피', '음식점', '레스토랑', '식당', '베이커리']):
            # 카페 메뉴 정보 추출
            menu_keywords = ['커피', '아메리카노', '라떼', '디저트', '맛', '향', '분위기', '인테리어', '서비스', '가격']
            if business_info and 'menu_info' in business_info:
                menu_info = business_info['menu_info']
                if 'popular_items' in menu_info:
                    menu_keywords.extend(menu_info['popular_items'][:3])  # 상위 3개 인기 메뉴
                if 'signature_dishes' in menu_info:
                    menu_keywords.extend(menu_info['signature_dishes'][:2])  # 상위 2개 시그니처
            
            menu_keywords_text = ', '.join(menu_keywords)
            
            if style_number == 1:
                return f"""다음 카페/음식점에 대한 메뉴 중심 캐주얼 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 구체적 메뉴 언급, 맛 평가, 이모티콘 사용
예시: "아메리카노 진짜 맛있어요~^^ 원두 직접 로스팅하는거 같던데 향이 좋더라고요 ㅋㅋ 재방문 의사 있어요👍"

실제 메뉴 및 특징: {menu_keywords_text}

리뷰만 출력:"""
            elif style_number == 2:
                return f"""다음 카페/음식점에 대한 요소별 나열형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 숫자로 각 요소별 평가 나열
예시: "1.커피맛 좋고 2.분위기 아늑하고 3.가격 적당하고 4.직원 친절하고.. 다 만족이에요!"

실제 메뉴 및 특징: {menu_keywords_text}

리뷰만 출력:"""
            elif style_number == 3:
                return f"""다음 카페/음식점에 대한 감탄사 맛집형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 감탄사 사용, 특별한 요소 강조
예시: "와~ 이 집 진짜 맛집이네요!! 라떼아트도 예쁘고!! 완전 강추해요!!"

카페/음식점 키워드: 커피, 라떼, 디저트, 맛, 향, 분위기, 인테리어, 서비스, 가격

리뷰만 출력:"""
            elif style_number == 4:
                return f"""다음 카페/음식점에 대한 모임/데이트 추천형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 방문 목적, 분위기 평가, 추천
예시: "친구들이랑 모임 장소로 갔는데 분위기도 좋고 메뉴도 다양해서 만족했어요. 데이트 장소로도 추천합니다!"

카페/음식점 키워드: 커피, 라떼, 디저트, 맛, 향, 분위기, 인테리어, 서비스, 가격

리뷰만 출력:"""
            else:  # style_number == 5
                return f"""다음 카페/음식점에 대한 간단 평가형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 핵심만 간단하게
예시: "맛있고 분위기 좋아요. 재방문할게요!"

카페/음식점 키워드: 커피, 라떼, 디저트, 맛, 향, 분위기, 인테리어, 서비스, 가격

리뷰만 출력:"""
        
        # 기타 업종 일반 프롬프트
        else:
            if style_number == 1:
                return f"""다음 사업장에 대한 친근 캐주얼 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 친근한 말투, 이모티콘 사용
예시: "서비스 정말 좋았어요~^^ 직원분들도 친절하시고 만족스러웠어요 ㅋㅋ 추천드려용👍"

리뷰만 출력:"""
            elif style_number == 2:
                return f"""다음 사업장에 대한 요소별 나열형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 숫자로 요소별 평가 나열
예시: "1.서비스 좋고 2.시설 깔끔하고 3.가격 적당하고.. 전반적으로 만족해요!"

리뷰만 출력:"""
            elif style_number == 3:
                return f"""다음 사업장에 대한 강조형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 감탄사와 강조표현 사용
예시: "와~ 정말 만족스러웠어요!! 다음에 또 이용할게요!!"

리뷰만 출력:"""
            elif style_number == 4:
                return f"""다음 사업장에 대한 추천형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 추천 멘트 포함
예시: "지인 추천으로 갔는데 정말 좋았어요. 다른 분들께도 추천하고 싶어요!"

리뷰만 출력:"""
            else:  # style_number == 5
                return f"""다음 사업장에 대한 간단형 리뷰를 작성하세요.

사업장: {business_name} ({business_type})
평점: {rating}점

스타일: 핵심만 간단하게
예시: "좋았어요. 추천합니다!"

리뷰만 출력:"""

        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.config['openai']['max_tokens']
            )
            
            content = response.choices[0].message.content
            
            result = {
                'review_text': content.replace('리뷰:', '').strip(),
                'rating': rating,
                'platform': 'naver_map',
                'business_id': business_id,
                'business_name': business_name,
                'review_type': review_type,
                'created_at': datetime.now().isoformat(),
                'metadata': {
                    'business_type': business_type,
                    'customer_profile': customer_profile,
                    'review_details': review_details,
                    'specific_experience': specific_experience,
                    'used_business_context': True,
                    'character_count': len(content.replace('리뷰:', '').strip()),
                    'authenticity_score': self._calculate_authenticity_score(business_context, content)
                }
            }
            
            return result
            
        except Exception as e:
            return {"error": f"리뷰 생성 실패: {str(e)}"}
    
    def create_google_review_with_business_info(self,
                                              business_id: str,
                                              rating: int = None,
                                              detailed_feedback: bool = True,
                                              focus_area: str = None) -> Dict[str, any]:
        """사업장 정보를 활용한 구글 리뷰 생성"""
        
        business_info = self.business_manager.get_business(business_id)
        if not business_info:
            return {"error": f"사업장 정보를 찾을 수 없습니다: {business_id}"}
        
        business_context = self._build_detailed_business_context(business_info)
        business_name = business_info['name']
        business_type = business_info['type']
        
        # 고객 프로필 선택 (구글 리뷰는 더 다양한 국적/배경)
        customer_profile = random.choice(self.customer_profiles)
        
        # 평점 자동 설정
        if rating is None:
            rating = random.choices([3, 4, 5], weights=[15, 35, 50])[0]
        
        # 포커스 영역 자동 설정
        if not focus_area:
            focus_areas = ['음식 품질', '서비스', '분위기', '가성비', '접근성']
            focus_area = random.choice(focus_areas)
        
        prompt = f"""
        다음 사업장의 실제 정보를 바탕으로 구글 리뷰를 작성해주세요:

        사업장 정보:
        - 이름: {business_name}
        - 업종: {business_type}
        - 설명: {business_context.get('description', '')}
        
        메뉴/서비스 세부사항:
        - 주요 메뉴: {', '.join(business_context.get('signature_dishes', []))}
        - 인기 항목: {', '.join(business_context.get('popular_items', []))}
        - 특별한 서비스: {', '.join(business_context.get('unique_features', []))}
        - 시설: {', '.join(business_context.get('facilities', []))}
        
        환경/접근성:
        - 분위기: {', '.join(business_context.get('mood_keywords', []))}
        - 소음 수준: {business_context.get('noise_level', '')}
        - 조명: {business_context.get('lighting', '')}
        - 주차 정보: {business_context.get('parking', '')}
        - 접근성: {business_context.get('accessibility', '')}
        
        운영 정보:
        - 가격대: {business_context.get('price_range', '')}
        - 운영시간: {business_context.get('operating_hours', '')}
        - 성수 시간: {', '.join(business_context.get('peak_times', []))}
        - 예약 정책: {business_context.get('reservation_info', '')}
        
        리뷰 설정:
        - 평점: {rating}점
        - 상세 피드백: {'예' if detailed_feedback else '간단히'}
        - 주요 포커스: {focus_area}
        - 리뷰어 스타일: {customer_profile['style']}
        
        요구사항:
        1. 구글 리뷰 특성에 맞는 국제적이고 객관적인 톤
        2. 위 사업장의 실제 정보를 구체적으로 반영
        3. {focus_area}에 특별히 주목한 평가
        4. 다른 방문객들에게 도움이 되는 실용적 정보 포함
        5. 평점에 맞는 균형잡힌 평가
        6. 구체적인 경험과 디테일 포함
        7. 이모지 사용하지 않고 텍스트만으로 작성
        8. {'상세한 분석과 조언' if detailed_feedback else '간결하고 핵심적인 평가'}
        
        응답 형식:
        리뷰: [리뷰 내용]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.config['openai']['max_tokens']
            )
            
            content = response.choices[0].message.content
            
            result = {
                'review_text': content.replace('리뷰:', '').strip(),
                'rating': rating,
                'platform': 'google_reviews',
                'business_id': business_id,
                'business_name': business_name,
                'focus_area': focus_area,
                'created_at': datetime.now().isoformat(),
                'metadata': {
                    'business_type': business_type,
                    'customer_profile': customer_profile,
                    'detailed_feedback': detailed_feedback,
                    'used_business_context': True,
                    'character_count': len(content.replace('리뷰:', '').strip()),
                    'authenticity_score': self._calculate_authenticity_score(business_context, content)
                }
            }
            
            return result
            
        except Exception as e:
            return {"error": f"리뷰 생성 실패: {str(e)}"}
    
    def _calculate_authenticity_score(self, business_context: Dict, review_text: str) -> float:
        """리뷰의 진정성 및 자연스러움 점수 계산 (0-1)"""
        score = 0.3  # 기본 점수
        
        # 구체적인 메뉴 언급
        mentioned_menus = business_context.get('signature_dishes', []) + business_context.get('popular_items', [])
        for menu in mentioned_menus:
            if menu.lower() in review_text.lower():
                score += 0.15
        
        # 특별한 서비스/시설 언급
        features = business_context.get('unique_features', []) + business_context.get('facilities', [])
        for feature in features:
            if feature.lower() in review_text.lower():
                score += 0.1
        
        # 자연스러운 표현 사용 (다양한 어미와 자연스러운 표현)
        natural_expressions = [
            # 실제 리뷰에서 자주 사용되는 자연스러운 어미들
            "네요", "더라고요", "더라구요", "거든요", "거예요", "한데요", "했는데", "하더군요", 
            "하더라구요", "드네요", "던데요", "했더니", "하니까", "해서", "하게 됐네요", 
            "나더라구요", "죠", "지요", "는 편이에요", "인 것 같네요", "한 것 같아", "다니까", "다니까요",
            
            # 펜션/숙박 특화 자연스러운 표현들 (예시에서 추출)
            "라 더욱 좋았습니다", "사용할 때 불편한 점 없이", "즐겁게 놀 수 있었고", "필요한건 다 있었어요",
            "편안해서 꿀잠잤습니다", "강력 추천할거예요", "각자 방.침대.화장실 따로라", "너무편햇어요",
            "빼고는", "너무좋앗습니다", "공기도단연최고고", "완벽하게놀다갑니다", "가족단위 추천드려용",
            "이용해서 너무나 즐거운 시간", "넉넉히 사용할 수 있어서", "조용하고 정원이 아름다웠어요",
            "다음에 또 방문하고 싶을만큼", "만족스러운 숙소였습니다", "걸맞게", "좋은 추억이 되었습니다",
            "쌓여있었는데", "비치되어있어", "상쾌하게 지낼수 있었습니다", "가족이라 마지막으로",
            "잠자리와 위생이 가장 신경쓰였는데", "푹 잘 주무셨다고", "마음에 든다고 하시더군요",
            "예민하던 저인데", "이역시도", "너무 깔끔했습니다", "마무리하게되어", "예쁜추억 만드세요",
            
            # 다양한 감정과 상황 표현
            "좋았네", "좋네", "괜찮네", "만족스럽네", "나쁘지 않네", "그럭저럭이네", "기대했는데", 
            "생각했는데", "아쉽네", "놀랐네", "감동이야", "실망이야", "만족스럽다", "후회된다", 
            "다행이다", "좋더라", "괜찮더라", "별로더라", "훌륭하다", "인상적이다", "신경쓰였는데",
            "마음에 든다고", "깔끔했습니다", "편안해서", "즐겁게", "만족스러운", "아름다웠어요",
            
            # 자연스러운 연결어와 부사
            "그런데", "다만", "하지만", "그래도", "근데", "아무튼", "어쨌든", "그나저나", "그치만", 
            "그러나", "사실", "솔직히", "정말", "진짜", "확실히", "역시", "역시나", "예상대로", 
            "의외로", "당연히", "물론", "빼고는", "걸맞게", "덕분에", "까지", "이역시도",
            
            # 정도와 강도 표현
            "좀", "약간", "조금", "살짝", "꽤", "상당히", "엄청", "많이", "너무", "정말", "진짜", 
            "완전", "대박", "심하게", "적당히", "은근히", "생각보다", "예상보다", "훨씬", "제법", 
            "꽤나", "상당히", "넉넉히", "아주", "매우", "단연", "완벽하게",
            
            # 방문 상황과 목적 표현들
            "가족이랑", "친구들이랑", "혼자 가서", "커플로", "아이들과", "부모님과", "지인과",
            "가족여행으로", "처음 방문", "재방문", "오랜만에", "급하게", "계획해서", "예약해서",
            "여행중에", "휴가로", "출장으로", "데이트로", "기념일로", "생일로", "결혼기념일로",
            
            # 추천과 의견 표현들
            "추천한다", "추천", "비추", "강추한다", "가볼만하다", "한번쯤은", "괜찮을 듯", 
            "별로일 듯", "갈만하다", "다시 갈 것 같다", "재방문할 것 같다", "다음에도", 
            "기회가 되면", "시간 나면", "강력 추천할거예요", "추천드려용", "추천드려요",
            
            # 시간과 비교 표현들
            "오랜만에", "처음엔", "나중엔", "결국엔", "마지막엔", "이번엔", "요즘엔", "최근엔", 
            "평소엔", "가끔씩", "자주", "종종", "항상", "보통", "일반적으로", "대체로", 
            "전반적으로", "개인적으론", "마지막으로", "처음으로",
            
            # 구체적인 경험 묘사 표현들
            "이용했는데", "사용할 때", "머무는동안", "지내면서", "갔다왔는데", "다녀왔는데",
            "체험해보니", "경험해보니", "써보니", "먹어보니", "마셔보니", "타보니", "걸어보니",
            "들어가니", "나와보니", "올라가니", "내려와니", "돌아보니", "비교해보니",
            
            # 감정 변화와 실감 표현들
            "실감나더라고요", "느껴지더라고요", "와닿더라고요", "다가오더라고요", "보이더라고요",
            "들리더라고요", "맛보이더라고요", "향기나더라고요", "촉감이 좋더라고요", "시원하더라고요",
            "따뜻하더라고요", "포근하더라고요", "편안하더라고요", "안전하더라고요", "깨끗하더라고요"
        ]
        natural_score = 0
        for expr in natural_expressions:
            if expr in review_text:
                natural_score += 0.05  # 여러 표현 사용 시 추가 점수
        score += min(natural_score, 0.2)  # 최대 0.2점까지
        
        # 균형감 (긍정+작은 아쉬운 점)
        balance_words = ["다만", "그런데", "아쉬운", "조금", "약간", "살짝", "좀"]
        for word in balance_words:
            if word in review_text:
                score += 0.15
                break
        
        # 적절한 길이 (너무 짧거나 길지 않음)
        length = len(review_text)
        if 80 <= length <= 200:
            score += 0.15
        elif 50 <= length <= 300:
            score += 0.1
        
        # 과도한 칭찬 표현 감점
        excessive_praise = ["최고", "완벽", "대박", "진짜 짱", "완전 추천"]
        for praise in excessive_praise:
            if praise in review_text:
                score -= 0.2
        
        # 광고성 문구 감점
        ad_phrases = ["강력히 추천", "적극 추천", "무조건", "반드시"]
        for phrase in ad_phrases:
            if phrase in review_text:
                score -= 0.15
        
        return min(max(score, 0.0), 1.0)
    
    def create_review_batch_with_business_info(self,
                                             business_id: str,
                                             count: int = 5,
                                             platform: str = "naver",
                                             rating_distribution: Dict[int, int] = None) -> List[Dict]:
        """사업장 정보를 기반으로 여러 리뷰를 일괄 생성 (자연스러움 분석 포함)"""
        
        if not rating_distribution:
            rating_distribution = {5: 3, 4: 2}  # 기본적으로 긍정적 분포
        
        reviews = []
        
        # 평점 분포에 따른 리뷰 생성
        for rating, review_count in rating_distribution.items():
            for _ in range(min(review_count, count - len(reviews))):
                if platform == "naver":
                    review = self.create_improved_review_with_analysis(
                        business_id=business_id,
                        rating=rating,
                        customer_type="random"
                    )
                else:  # google
                    review = self.create_google_review_with_business_info(
                        business_id=business_id,
                        rating=rating,
                        detailed_feedback=random.choice([True, False])
                    )
                    # 구글 리뷰에도 자연스러움 분석 추가
                    if 'error' not in review:
                        review_text = review['review_text']
                        naturalness_analysis = self.analyze_review_naturalness(review_text)
                        review['metadata']['naturalness_analysis'] = naturalness_analysis
                        review['metadata']['naturalness_score'] = naturalness_analysis['score']
                
                if 'error' not in review:
                    reviews.append(review)
                
                if len(reviews) >= count:
                    break
            
            if len(reviews) >= count:
                break
        
        return reviews
    
    def get_review_templates_for_business(self, business_id: str) -> List[Dict]:
        """사업장 유형에 맞는 리뷰 템플릿 제안"""
        business_info = self.business_manager.get_business(business_id)
        if not business_info:
            return []
        
        business_type = business_info['type']
        templates = []
        
        # 업종별 특화 템플릿
        if '음식점' in business_type or '카페' in business_type:
            templates.extend([
                {"type": "메뉴 중심", "focus": "시그니처 메뉴 체험"},
                {"type": "분위기 중심", "focus": "공간과 서비스 경험"},
                {"type": "가성비 중심", "focus": "가격 대비 만족도"}
            ])
        
        if '호텔' in business_type or '숙박' in business_type:
            templates.extend([
                {"type": "시설 중심", "focus": "객실과 부대시설"},
                {"type": "서비스 중심", "focus": "직원 서비스와 편의성"},
                {"type": "위치 중심", "focus": "접근성과 주변 환경"}
            ])
        
        # 공통 템플릿
        templates.extend([
            {"type": "종합 평가", "focus": "전반적인 경험"},
            {"type": "재방문 의사", "focus": "추천 여부와 이유"}
        ])
        
        return templates

    def analyze_review_naturalness(self, review_text: str) -> dict:
        """리뷰 자연스러움 분석 및 개선 제안 (더 엄격한 기준)"""
        analysis = {
            "score": 0,
            "issues": [],
            "suggestions": []
        }
        
        # 길이 체크
        length = len(review_text)
        if length < 50:
            analysis["issues"].append("너무 짧음")
            analysis["suggestions"].append("더 구체적인 경험을 추가하세요")
        elif length > 300:
            analysis["issues"].append("너무 김")
            analysis["suggestions"].append("핵심 내용으로 간결하게 정리하세요")
        else:
            analysis["score"] += 20
        
        # 다양한 스타일 점수 체크 (새로운 기준)
        style_indicators = [
            # 친근하고 캐주얼
            "^^", "~", "ㅋ", "ㅠ", "😊", "👍", "추천드려용", "좋았어요~",
            
            # 구체적 나열형
            "1.", "2.", "3.", "첫째", "둘째", "~하고", "~고",
            
            # 감탄사·강조형
            "!!", "와~", "정말!", "진짜", "완벽", "최고", "만족",
            
            # 가족/지인 경험
            "가족", "부모님", "아이", "지인", "친구", "모두", "추천합니다", "강추",
            
            # 짧고 간단형
            "좋았습니다", "추천해요", "만족해요", "편히"
        ]
        
        style_score = 0
        for indicator in style_indicators:
            if indicator in review_text:
                style_score += 1
        
        if style_score >= 3:
            analysis["score"] += 30  # 다양한 스타일 표현 사용
        elif style_score >= 1:
            analysis["score"] += 15
        else:
            analysis["suggestions"].append("더 다양하고 개성있는 표현을 사용해보세요")
        
        # 기본 자연스러움 점수
        analysis["score"] += 30
        
        # 자연스러운 표현 체크 (예시에서 추출한 실제 패턴들)
        natural_expressions = [
            # 실제 리뷰에서 자주 나타나는 자연스러운 패턴
            "더라고", "거든요", "한데요", "드네요", "죠", "했는데", "하니까", "다 보니",
            "라서", "빼고는", "걸맞게", "덕분에", "까지", "생각보다", "의외로", "예상보다",
            "괜찮네", "좋네", "만족스럽네", "아쉽네", "놀랐네", "감동", "실망",
            "가족이랑", "친구들이랑", "혼자", "커플로", "아이들과", "부모님과",
            "처음", "재방문", "오랜만에", "급하게", "또 가고 싶", "추천할 만해",
            "불편한 점 없이", "필요한건 다", "너무편햇", "좋앗습니다", "만족스러웠",
            "인 것 같네", "할 만해", "괜찮을 듯", "별로일 듯"
        ]
        
        natural_score = 0
        for expr in natural_expressions:
            if expr in review_text:
                natural_score += 1
        
        if natural_score >= 3:
            analysis["score"] += 25
        elif natural_score >= 1:
            analysis["score"] += 15
        else:
            analysis["issues"].append("자연스러운 표현 부족")
            analysis["suggestions"].append("실제 리뷰에서 사용하는 자연스러운 표현을 더 활용하세요")
        
        # 균형감 체크 (긍정+작은 아쉬운 점)
        balance_words = ["다만", "그런데", "아쉬운", "조금", "약간", "살짝", "좀", "빼고는", "하지만"]
        if any(word in review_text for word in balance_words):
            analysis["score"] += 15
        else:
            analysis["suggestions"].append("작은 아쉬운 점도 언급해보세요 (진정성 확보)")
        
        # 구체성 체크 (메뉴명, 시설명 등)
        specific_words = ["원", "맛", "메뉴", "서비스", "분위기", "가격", "시설", "직원", "주차"]
        specific_count = sum(1 for word in specific_words if word in review_text)
        if specific_count >= 3:
            analysis["score"] += 10
        elif specific_count >= 1:
            analysis["score"] += 5
        else:
            analysis["suggestions"].append("더 구체적인 내용을 포함하세요")
        
        # 과도한 칭찬은 이제 허용 (실제 리뷰 스타일이므로)
        positive_expressions = ["완벽", "최고", "정말", "진짜", "만족", "좋아", "추천"]
        positive_count = sum(1 for expr in positive_expressions if expr in review_text)
        if positive_count >= 2:
            analysis["score"] += 15  # 긍정적 표현 사용 시 보너스
        
        # 개성과 다양성 체크
        personality_indicators = ["^^", "ㅋ", "~", "!!", "😊", "👍"]
        personality_count = sum(1 for indicator in personality_indicators if indicator in review_text)
        if personality_count > 0:
            analysis["score"] += 10  # 개성있는 표현 보너스
        
        # 광고성 문구 감점
        ad_phrases = ["무조건", "반드시", "적극", "강력히"]
        for phrase in ad_phrases:
            if phrase in review_text:
                analysis["score"] -= 15
                analysis["issues"].append("광고성 문구")
                break
        
        analysis["score"] = min(max(analysis["score"], 0), 100)
        
        # 테스트 호환성을 위해 total_score도 추가
        analysis["total_score"] = analysis["score"]
        analysis["improvement_suggestions"] = analysis["suggestions"]
        
        return analysis

    def get_improvement_tips(self):
        """리뷰 개선 팁 반환"""
        tips = [
            "🎯 구체적 경험 포함: '아메리카노 맛있었어요' → '아메리카노가 진하고 좋더라고요. 다만 좀 비싼 편이에요'",
            "💬 자연스러운 어투: '최고입니다!' → '괜찮네요', '만족해요'",
            "⚖️ 균형잡힌 평가: 긍정적 의견 + 작은 아쉬운 점",
            "📏 적절한 길이: 100-200자 (너무 짧지도 길지도 않게)",
            "👥 방문 상황: 가족/커플/친구 등 구체적 상황 반영",
            "🔍 실제 디테일: 메뉴명, 가격, 서비스 등 구체적 정보",
            "🚫 광고성 금지: 과도한 추천, 홍보성 문구 피하기"
        ]
        return tips

    def demonstrate_review_improvements(self):
        """개선 전후 비교 예시"""
        examples = {
            "Before (부자연스러움)": [
                "정말 최고의 카페입니다! 모든 것이 완벽하고 강력히 추천드립니다!",
                "시설이 좋고 서비스가 만족스럽습니다. 재방문 의사 있습니다.",
                "맛있어요."
            ],
            "After (자연스러움)": [
                "아메리카노 마셨는데 진하니까 좋더라고요. 가격은 좀 비싼 편이지만 분위기 괜찮아요.",
                "가족이랑 왔는데 아이들도 좋아하네요. 다만 주차가 좀 불편했어요. 그래도 또 올 것 같아요.",
                "크로와상이 바삭하니 맛있었어요. 커피도 무난한 편이고요. 재방문 의사 있어요."
            ]
        }
        return examples

    def create_improved_review_with_analysis(self, business_id: str, rating: int = None, **kwargs) -> Dict[str, any]:
        """개선된 리뷰 생성 및 자연스러움 분석"""
        # 기본 리뷰 생성
        review_result = self.create_naver_review_with_business_info(
            business_id=business_id,
            rating=rating,
            **kwargs
        )
        
        if 'error' in review_result:
            return review_result
        
        # 자연스러움 분석 추가
        review_text = review_result['review_text']
        naturalness_analysis = self.analyze_review_naturalness(review_text)
        
        # 메타데이터에 분석 결과 추가
        review_result['metadata']['naturalness_analysis'] = naturalness_analysis
        review_result['metadata']['naturalness_score'] = naturalness_analysis['score']
        
        return review_result

if __name__ == "__main__":
    # 테스트 코드
    generator = EnhancedReviewGenerator()
    
    # 사업장 정보 확인
    business_manager = BusinessInfoManager()
    businesses = business_manager.get_all_businesses()
    
    if businesses:
        business_id = list(businesses.keys())[0]
        business_name = businesses[business_id]['name']
        
        print(f"테스트 대상: {business_name}")
        
        # 네이버 리뷰 생성 테스트
        naver_review = generator.create_naver_review_with_business_info(
            business_id=business_id,
            rating=5,
            review_type="상세후기"
        )
        
        print("\n=== 생성된 네이버 리뷰 ===")
        print(f"평점: {naver_review.get('rating', 0)}점")
        print(f"진정성 점수: {naver_review.get('metadata', {}).get('authenticity_score', 0):.2f}")
        print(naver_review.get('review_text', naver_review.get('error', ''))[:200] + "...")
        
        # 구글 리뷰 생성 테스트
        google_review = generator.create_google_review_with_business_info(
            business_id=business_id,
            rating=4,
            focus_area="음식 품질"
        )
        
        print("\n=== 생성된 구글 리뷰 ===")
        print(f"평점: {google_review.get('rating', 0)}점")
        print(f"포커스: {google_review.get('focus_area', '')}")
        print(google_review.get('review_text', google_review.get('error', ''))[:200] + "...")
        
    else:
        print("등록된 사업장이 없습니다. business_info.py를 먼저 실행하여 샘플 데이터를 생성하세요.")
