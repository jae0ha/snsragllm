"""
향상된 SNS 콘텐츠 생성기
저장된 사업장 정보를 기반으로 더 정확하고 맞춤화된 콘텐츠를 생성합니다.
"""

import yaml
import random
import os
from typing import Dict, List, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from data_sources.business_info import BusinessInfoManager, BusinessProfile

class EnhancedSNSGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        """향상된 SNS 콘텐츠 생성기 초기화"""
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
        self.temperature = self.config['openai']['temperature']
        
        # 플랫폼별 설정 로드
        self.platforms = self.config['content_generation']['platforms']
        
        # 사업장 정보 관리자
        self.business_manager = BusinessInfoManager()
    
    def _build_business_context(self, business_info: Dict) -> str:
        """사업장 정보를 기반으로 컨텍스트 문자열 생성"""
        context_parts = []
        
        # 기본 정보
        if business_info.get('basic_info'):
            basic = business_info['basic_info']
            if basic.get('description'):
                context_parts.append(f"사업장 설명: {basic['description']}")
            if basic.get('price_range'):
                context_parts.append(f"가격대: {basic['price_range']}")
            if basic.get('operating_hours'):
                context_parts.append(f"운영시간: {basic['operating_hours']}")
        
        # 메뉴 정보
        if business_info.get('menu_info'):
            menu = business_info['menu_info']
            if menu.get('signature_dishes'):
                context_parts.append(f"시그니처 메뉴: {', '.join(menu['signature_dishes'])}")
            if menu.get('popular_items'):
                context_parts.append(f"인기 메뉴: {', '.join(menu['popular_items'])}")
            if menu.get('special_ingredients'):
                context_parts.append(f"특별한 재료: {', '.join(menu['special_ingredients'])}")
        
        # 서비스 정보
        if business_info.get('service_info'):
            service = business_info['service_info']
            if service.get('unique_features'):
                context_parts.append(f"특별한 서비스: {', '.join(service['unique_features'])}")
        
        # 분위기 정보
        if business_info.get('atmosphere_info'):
            atmosphere = business_info['atmosphere_info']
            if atmosphere.get('mood_keywords'):
                context_parts.append(f"분위기: {', '.join(atmosphere['mood_keywords'])}")
            if atmosphere.get('suitable_occasions'):
                context_parts.append(f"적합한 방문 목적: {', '.join(atmosphere['suitable_occasions'])}")
        
        # 마케팅 정보
        if business_info.get('marketing_info'):
            marketing = business_info['marketing_info']
            if marketing.get('key_selling_points'):
                context_parts.append(f"주요 강점: {', '.join(marketing['key_selling_points'])}")
            if marketing.get('target_audience'):
                context_parts.append(f"주요 고객층: {', '.join(marketing['target_audience'])}")
        
        return "\n".join(context_parts)
    
    def create_instagram_post_with_business_info(self, 
                                               business_id: str,
                                               post_theme: str = "일반 홍보",
                                               specific_focus: str = None,
                                               target_audience: str = None,
                                               style: str = "친근한",
                                               include_hashtags: bool = True) -> Dict[str, str]:
        """사업장 정보를 활용한 인스타그램 게시물 생성"""
        
        business_info = self.business_manager.get_business(business_id)
        if not business_info:
            return {"error": f"사업장 정보를 찾을 수 없습니다: {business_id}"}
        
        business_context = self._build_business_context(business_info)
        business_name = business_info['name']
        business_type = business_info['type']
        
        # 타겟 오디언스 자동 설정
        if not target_audience and business_info.get('marketing_info', {}).get('target_audience'):
            target_audience = ', '.join(business_info['marketing_info']['target_audience'][:2])
        
        prompt = f"""
        다음 사업장 정보를 바탕으로 인스타그램 게시물을 작성해주세요:

        사업장 기본 정보:
        - 이름: {business_name}
        - 업종: {business_type}
        
        상세 정보:
        {business_context}
        
        게시물 설정:
        - 주제/테마: {post_theme}
        - 특별히 강조할 점: {specific_focus or '전반적인 매력'}
        - 타겟 오디언스: {target_audience or '일반 고객'}
        - 스타일: {style}
        
        요구사항:
        1. 위 사업장의 실제 정보를 반영한 매력적이고 참여를 유도하는 캡션 작성
        2. 이모지 사용하지 않고 텍스트만으로 작성
        3. 자연스러운 Call-to-Action 포함
        4. 최대 {self.platforms['instagram']['max_caption_length']}자 이내
        5. 사업장의 고유한 특징과 강점을 자연스럽게 어필
        
        응답 형식:
        캡션: [캡션 내용]
        """
        
        if include_hashtags:
            prompt += f"\n해시태그: [사업장과 관련된 해시태그 최대 {self.platforms['instagram']['max_hashtags']}개]"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.config['openai']['max_tokens']
            )
            
            content = response.choices[0].message.content
            
            # 응답 파싱
            lines = content.split('\n')
            result = {}
            
            for line in lines:
                if line.startswith('캡션:'):
                    result['caption'] = line.replace('캡션:', '').strip()
                elif line.startswith('해시태그:'):
                    result['hashtags'] = line.replace('해시태그:', '').strip()
            
            result.update({
                'platform': 'instagram',
                'business_id': business_id,
                'business_name': business_name,
                'post_theme': post_theme,
                'created_at': datetime.now().isoformat(),
                'metadata': {
                    'business_type': business_type,
                    'specific_focus': specific_focus,
                    'target_audience': target_audience,
                    'style': style,
                    'used_business_context': True
                }
            })
            
            return result
            
        except Exception as e:
            return {"error": f"콘텐츠 생성 실패: {str(e)}"}
    
    def create_facebook_post_with_business_info(self,
                                              business_id: str,
                                              post_type: str = "홍보",
                                              storytelling_angle: str = None,
                                              call_to_action: str = "방문 유도") -> Dict[str, str]:
        """사업장 정보를 활용한 페이스북 게시물 생성"""
        
        business_info = self.business_manager.get_business(business_id)
        if not business_info:
            return {"error": f"사업장 정보를 찾을 수 없습니다: {business_id}"}
        
        business_context = self._build_business_context(business_info)
        business_name = business_info['name']
        business_type = business_info['type']
        
        prompt = f"""
        다음 사업장 정보를 바탕으로 페이스북 게시물을 작성해주세요:

        사업장 기본 정보:
        - 이름: {business_name}
        - 업종: {business_type}
        
        상세 정보:
        {business_context}
        
        게시물 설정:
        - 게시물 타입: {post_type}
        - 스토리텔링 앵글: {storytelling_angle or '사업장의 특별함'}
        - 목표 행동: {call_to_action}
        
        요구사항:
        1. 사업장의 실제 정보를 기반으로 한 페이스북 사용자들의 참여를 유도하는 내용
        2. 스토리텔링 요소 포함하여 감정적 연결 만들기
        3. 공유하고 싶은 가치 있는 정보 제공
        4. 추천 길이 {self.platforms['facebook']['recommended_length']}자 내외
        5. 댓글이나 반응을 유도하는 질문 포함
        6. 이모지 사용하지 않고 텍스트만으로 작성
        7. 사업장의 독특한 이야기나 경험을 자연스럽게 어필
        
        응답 형식:
        게시물: [게시물 내용]
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
                'post_content': content.replace('게시물:', '').strip(),
                'platform': 'facebook',
                'business_id': business_id,
                'business_name': business_name,
                'post_type': post_type,
                'created_at': datetime.now().isoformat(),
                'metadata': {
                    'business_type': business_type,
                    'storytelling_angle': storytelling_angle,
                    'call_to_action': call_to_action,
                    'used_business_context': True
                }
            }
            
            return result
            
        except Exception as e:
            return {"error": f"콘텐츠 생성 실패: {str(e)}"}
    
    def create_blog_post_with_business_info(self,
                                          business_id: str,
                                          blog_topic: str,
                                          target_keywords: List[str] = None,
                                          target_length: int = 2000) -> Dict[str, str]:
        """사업장 정보를 활용한 블로그 포스트 생성"""
        
        business_info = self.business_manager.get_business(business_id)
        if not business_info:
            return {"error": f"사업장 정보를 찾을 수 없습니다: {business_id}"}
        
        business_context = self._build_business_context(business_info)
        business_name = business_info['name']
        business_type = business_info['type']
        
        # 기본 키워드 생성
        if not target_keywords:
            target_keywords = [business_name, business_type]
            if business_info.get('menu_info', {}).get('signature_dishes'):
                target_keywords.extend(business_info['menu_info']['signature_dishes'][:2])
        
        prompt = f"""
        다음 사업장 정보를 바탕으로 블로그 포스트를 작성해주세요:

        사업장 기본 정보:
        - 이름: {business_name}
        - 업종: {business_type}
        
        상세 정보:
        {business_context}
        
        블로그 설정:
        - 주제: {blog_topic}
        - SEO 키워드: {', '.join(target_keywords)}
        - 목표 길이: 약 {target_length}자
        
        요구사항:
        1. 사업장의 실제 정보를 기반으로 한 SEO 최적화된 제목과 구조
        2. 독자에게 가치 있는 정보 제공 (실제 메뉴, 서비스, 분위기 등)
        3. 자연스러운 사업장 소개 및 추천
        4. 읽기 쉬운 문단 구성
        5. 행동 유도 결론 포함 (방문, 문의 등)
        6. 이모지 사용하지 않고 텍스트만으로 작성
        7. 사업장의 독특한 특징과 경험을 구체적으로 설명
        
        응답 형식:
        제목: [SEO 최적화 제목]
        
        본문:
        [블로그 포스트 내용]
        
        요약: [한 줄 요약]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.config['openai']['max_tokens']
            )
            
            content = response.choices[0].message.content
            
            # 응답 파싱
            sections = content.split('\n\n')
            result = {
                'full_content': content,
                'platform': 'blog',
                'business_id': business_id,
                'business_name': business_name,
                'blog_topic': blog_topic,
                'created_at': datetime.now().isoformat(),
                'word_count': len(content.replace('\n', ' ').split()),
                'metadata': {
                    'business_type': business_type,
                    'target_keywords': target_keywords,
                    'target_length': target_length,
                    'used_business_context': True
                }
            }
            
            # 제목과 본문 분리 시도
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('제목:'):
                    result['title'] = line.replace('제목:', '').strip()
                elif line.startswith('요약:'):
                    result['summary'] = line.replace('요약:', '').strip()
            
            return result
            
        except Exception as e:
            return {"error": f"콘텐츠 생성 실패: {str(e)}"}
    
    def get_business_list(self) -> List[Dict]:
        """저장된 사업장 목록 반환"""
        businesses = self.business_manager.get_all_businesses()
        return [
            {
                'id': business_id,
                'name': info['name'],
                'type': info['type'],
                'description': info.get('basic_info', {}).get('description', ''),
                'updated_at': info.get('updated_at', '')
            }
            for business_id, info in businesses.items()
        ]
    
    def create_content_suggestions(self, business_id: str) -> List[Dict]:
        """사업장 정보를 기반으로 콘텐츠 제안 생성"""
        business_info = self.business_manager.get_business(business_id)
        if not business_info:
            return []
        
        suggestions = []
        
        # 메뉴 기반 제안
        if business_info.get('menu_info', {}).get('signature_dishes'):
            for dish in business_info['menu_info']['signature_dishes'][:2]:
                suggestions.append({
                    'platform': 'instagram',
                    'theme': f'{dish} 소개',
                    'description': f'{dish}의 특별함을 강조한 포스트'
                })
        
        # 분위기 기반 제안
        if business_info.get('atmosphere_info', {}).get('suitable_occasions'):
            for occasion in business_info['atmosphere_info']['suitable_occasions'][:2]:
                suggestions.append({
                    'platform': 'facebook',
                    'theme': f'{occasion}에 완벽한 장소',
                    'description': f'{occasion}을 위한 공간으로서의 매력 어필'
                })
        
        # 서비스 기반 제안
        if business_info.get('service_info', {}).get('unique_features'):
            for feature in business_info['service_info']['unique_features'][:1]:
                suggestions.append({
                    'platform': 'blog',
                    'theme': f'{feature} 체험 후기',
                    'description': f'{feature}에 대한 상세한 소개와 후기'
                })
        
        return suggestions
    
    def generate_content(self, business_profile, platform="Instagram", content_style="캐주얼", 
                        target_audience="일반 고객", custom_keywords=None, include_hashtags=True, **kwargs):
        """
        간단한 콘텐츠 생성 메서드 (Streamlit 앱용)
        business_profile: dict 형태의 사업장 정보
        """
        try:
            # dict 형태의 business_profile에서 정보 추출
            business_name = business_profile.get('name', '사업장')
            business_type = business_profile.get('type', '일반업종')
            description = business_profile.get('description', '')
            
            # 직접 프롬프트 기반 생성 (더 안정적)
            if platform == "Instagram":
                prompt = f"""
{business_name}의 Instagram 게시물을 작성해주세요.

사업장 정보:
- 이름: {business_name}
- 업종: {business_type}
- 설명: {description}

요구사항:
- 스타일: {content_style}
- 타겟 고객: {target_audience}
- Instagram에 적합한 매력적인 콘텐츠
- 150자 내외로 작성
- 자연스럽고 친근한 톤앤매너
- 절대로 이모지를 사용하지 마세요 (😊, 🎉, ❤️, 👍 등 모든 이모티콘 금지)
- 오직 한글과 영문, 숫자, 기본 문장부호만 사용하세요
"""
                if custom_keywords:
                    prompt += f"- 다음 키워드 활용: {', '.join(custom_keywords)}\n"
                
                if include_hashtags:
                    prompt += "- 관련 해시태그 5-8개 포함\n"
                
                prompt += "\n응답 형식: [게시물 내용]"
                
            elif platform == "Facebook":
                prompt = f"""
{business_name}의 Facebook 게시물을 작성해주세요.

사업장 정보:
- 이름: {business_name}
- 업종: {business_type}
- 설명: {description}

요구사항:
- 스타일: {content_style}
- 타겟 고객: {target_audience}
- Facebook 사용자들의 참여를 유도하는 내용
- 200-300자 내외로 작성
- 댓글이나 반응을 유도하는 질문 포함
- 절대로 이모지를 사용하지 마세요 (😊, 🎉, ❤️, 👍 등 모든 이모티콘 금지)
- 오직 한글과 영문, 숫자, 기본 문장부호만 사용하세요
"""
                if custom_keywords:
                    prompt += f"- 다음 키워드 활용: {', '.join(custom_keywords)}\n"
                
                prompt += "\n응답 형식: [게시물 내용]"
                
            else:
                # 기타 플랫폼
                prompt = f"""
{business_name}의 {platform} 콘텐츠를 생성해주세요.

사업장 정보:
- 이름: {business_name}
- 업종: {business_type}
- 설명: {description}

요구사항:
- 스타일: {content_style}
- 타겟 고객: {target_audience}
- {platform}에 적합한 콘텐츠
- 절대로 이모지를 사용하지 마세요 (😊, 🎉, ❤️, 👍 등 모든 이모티콘 금지)
- 오직 한글과 영문, 숫자, 기본 문장부호만 사용하세요
"""
                if custom_keywords:
                    prompt += f"- 다음 키워드 활용: {', '.join(custom_keywords)}\n"
                
                prompt += f"\n자연스럽고 매력적인 {platform} 콘텐츠를 작성해주세요."
            
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # 이모지 제거 후처리 (안전한 버전)
            content = self._remove_emojis_safe(content)
            
            return content
                
        except Exception as e:
            return f"콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _remove_emojis_safe(self, text):
        """텍스트에서 이모지만 안전하게 제거하는 함수"""
        import re
        
        try:
            # 가장 일반적인 이모지만 제거 (보수적 접근)
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # 감정 이모지
                "\U0001F300-\U0001F5FF"  # 심볼 & 그림
                "\U0001F680-\U0001F6FF"  # 교통 & 지도
                "\U0001F1E0-\U0001F1FF"  # 국기
                "\U00002600-\U000026FF"  # 기타 심볼
                "\U0001F900-\U0001F9FF"  # 추가 심볼
                "]+", 
                flags=re.UNICODE
            )
            
            # 이모지만 제거하고 공백 정리
            cleaned_text = emoji_pattern.sub('', text)
            
            # 연속된 공백만 정리 (다른 특수문자는 건드리지 않음)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            return cleaned_text
            
        except Exception as e:
            # 오류 발생시 원본 텍스트 반환
            print(f"이모지 제거 중 오류: {e}")
            return text
    
    def _remove_emojis(self, text):
        """텍스트에서 이모지를 제거하는 함수"""
        import re
        
        # 이모지 패턴 정의 (유니코드 범위)
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001F900-\U0001F9FF"  # supplemental symbols
            u"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
            "]+", flags=re.UNICODE)
        
        # 이모지 제거
        text = emoji_pattern.sub('', text)
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

if __name__ == "__main__":
    # 테스트 코드
    generator = EnhancedSNSGenerator()
    
    # 사업장 목록 확인
    businesses = generator.get_business_list()
    print(f"등록된 사업장 수: {len(businesses)}")
    
    if businesses:
        business_id = businesses[0]['id']
        print(f"\n테스트 대상: {businesses[0]['name']}")
        
        # 인스타그램 포스트 생성 테스트
        result = generator.create_instagram_post_with_business_info(
            business_id=business_id,
            post_theme="시그니처 메뉴 소개",
            style="전문적인"
        )
        
        print("=== 생성된 인스타그램 포스트 ===")
        print(result.get('caption', result.get('error', ''))[:200] + "...")
    else:
        print("등록된 사업장이 없습니다. business_info.py를 먼저 실행하여 샘플 데이터를 생성하세요.")
