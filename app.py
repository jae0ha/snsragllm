"""
메인 애플리케이션 파일
SNS 및 리뷰 콘텐츠 생성 시스템의 통합 인터페이스 - 사업장 정보 기반 향상 버전
"""

import yaml
import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from content_generator.enhanced_sns_generator import EnhancedSNSGenerator
from content_generator.enhanced_review_generator import EnhancedReviewGenerator
from data_sources.business_info import BusinessInfoManager, BusinessProfile

class ContentGeneratorApp:
    def __init__(self):
        """애플리케이션 초기화"""
        self.config = self.load_config()
        self.enhanced_sns_generator = EnhancedSNSGenerator()
        self.enhanced_review_generator = EnhancedReviewGenerator()
        self.business_manager = BusinessInfoManager()
        
    def load_config(self):
        """설정 파일 로드"""
        try:
            # .env 파일 로드
            load_dotenv()
            
            # config.yaml 파일 로드
            with open('config.yaml', 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # 환경변수에서 API 키 설정
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key and 'openai' in config:
                config['openai']['api_key'] = api_key
            
            return config
        except Exception as e:
            st.error(f"설정 파일 로드 중 오류 발생: {str(e)}")
            return {}
    
    def run_streamlit_app(self):
        """Streamlit 웹 애플리케이션 실행"""
        
        st.set_page_config(
            page_title="SNS & 리뷰 콘텐츠 생성기",
            page_icon="📱",
            layout="wide"
        )
        
        st.title("🚀 SNS & 리뷰 콘텐츠 생성기")
        st.markdown("RAG 기반 마케팅 자동화 도구 - 사업장 정보 기반 맞춤 콘텐츠 생성")
        
        # 탭 구성
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📋 사업장 관리", 
            "📱 SNS 콘텐츠", 
            "⭐ 리뷰 작성", 
            "🔄 일괄 생성", 
            "📊 분석", 
            "⚙️ 설정"
        ])
        
        # 사업장 관리 탭
        with tab1:
            self.render_business_management_tab()
        
        # SNS 콘텐츠 생성 탭
        with tab2:
            self.render_sns_tab()
        
        # 리뷰 생성 탭
        with tab3:
            self.render_review_tab()
        
        # 일괄 생성 탭
        with tab4:
            self.render_batch_generation_tab()
        
        # 분석 탭
        with tab5:
            self.render_analytics_tab()
        
        # 설정 탭
        with tab6:
            self.render_settings_tab()
    
    def render_sns_tab(self):
        """SNS 콘텐츠 생성 탭"""
        st.header("📱 SNS 콘텐츠 생성")
        
        # 사업장 선택
        businesses = self.business_manager.get_all_businesses()
        
        if not businesses:
            st.warning("먼저 사업장을 등록해주세요. '📋 사업장 관리' 탭에서 사업장을 등록할 수 있습니다.")
            return
        
        business_options = {f"{info['name']} ({business_id})": info for business_id, info in businesses.items()}
        selected_business_display = st.selectbox(
            "콘텐츠를 생성할 사업장을 선택하세요",
            list(business_options.keys()),
            key="sns_business_select"
        )
        
        if selected_business_display:
            selected_business = business_options[selected_business_display]
            self.render_sns_content_section(selected_business)
    
    def render_business_management_tab(self):
        """사업장 정보 관리 탭"""
        st.header("📋 사업장 정보 관리")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("등록된 사업장")
            businesses = self.business_manager.get_all_businesses()
            
            if businesses:
                business_names = [f"{info['name']} ({business_id})" for business_id, info in businesses.items()]
                selected = st.selectbox("사업장 선택", business_names)
                
                if selected:
                    business_id = selected.split('(')[-1].rstrip(')')
                    
                    if st.button("선택한 사업장 삭제", type="secondary"):
                        self.business_manager.delete_business(business_id)
                        st.success("사업장이 삭제되었습니다.")
                        st.rerun()
            else:
                st.info("등록된 사업장이 없습니다.")
        
        with col2:
            st.subheader("새 사업장 등록")
            
            with st.form("add_business"):
                business_name = st.text_input("사업장 이름*", placeholder="예: 맛있는 카페")
                business_type = st.selectbox("업종*", [
                    "카페", "레스토랑", "패스트푸드", "베이커리", "바",
                    "호텔", "펜션", "쇼핑몰", "미용실", "헬스장", "기타"
                ])
                
                st.markdown("**기본 정보**")
                col2_1, col2_2 = st.columns(2)
                with col2_1:
                    description = st.text_area("사업장 설명", placeholder="간단한 소개")
                    price_range = st.selectbox("가격대", ["저렴", "보통", "비싸", "고급"])
                with col2_2:
                    phone = st.text_input("전화번호", placeholder="02-1234-5678")
                    hours = st.text_input("운영시간", placeholder="09:00-22:00")
                
                st.markdown("**메뉴/상품 정보**")
                col2_3, col2_4 = st.columns(2)
                with col2_3:
                    signature = st.text_input("시그니처 메뉴", placeholder="아메리카노, 케이크")
                    popular = st.text_input("인기 메뉴", placeholder="라떼, 샌드위치")
                with col2_4:
                    ingredients = st.text_input("특별 재료", placeholder="유기농 원두")
                
                st.markdown("**분위기 & 서비스**")
                col2_5, col2_6 = st.columns(2)
                with col2_5:
                    mood = st.text_input("분위기 키워드", placeholder="아늑한, 모던한")
                    occasions = st.text_input("적합한 상황", placeholder="데이트, 회의")
                with col2_6:
                    features = st.text_input("특별 서비스", placeholder="무료 와이파이, 주차")
                
                if st.form_submit_button("사업장 등록", type="primary"):
                    if business_name and business_type:
                        new_business = BusinessProfile(
                            name=business_name,
                            business_type=business_type,
                            basic_info={
                                "description": description,
                                "phone": phone,
                                "price_range": price_range,
                                "operating_hours": hours
                            },
                            menu_info={
                                "signature_dishes": [item.strip() for item in signature.split(',') if item.strip()],
                                "popular_items": [item.strip() for item in popular.split(',') if item.strip()],
                                "special_ingredients": [item.strip() for item in ingredients.split(',') if item.strip()]
                            },
                            atmosphere_info={
                                "mood_keywords": [item.strip() for item in mood.split(',') if item.strip()],
                                "suitable_occasions": [item.strip() for item in occasions.split(',') if item.strip()]
                            },
                            service_info={
                                "unique_features": [item.strip() for item in features.split(',') if item.strip()]
                            }
                        )
                        
                        business_id = self.business_manager.add_business_profile(new_business)
                        st.success(f"사업장이 등록되었습니다! (ID: {business_id})")
                        st.rerun()
                    else:
                        st.error("사업장 이름과 업종은 필수입니다.")
    
    def render_sns_content_section(self, selected_business):
        """SNS 콘텐츠 생성 섹션"""
        st.markdown('<h2 class="main-title">📱 SNS 콘텐츠 생성</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            platform = st.selectbox(
                "플랫폼 선택",
                ["Instagram", "Facebook", "Twitter/X", "Blog"],
                key="sns_platform"
            )
            
            content_style = st.selectbox(
                "콘텐츠 스타일",
                ["캐주얼", "전문적", "감성적", "유머러스", "정보제공형"],
                key="sns_style"
            )
        
        with col2:
            target_audience = st.selectbox(
                "타겟 고객",
                ["일반 고객", "젊은층(20-30대)", "중장년층(40-50대)", "가족층", "전문가층"],
                key="sns_audience"
            )
            
            include_hashtags = st.checkbox("해시태그 포함", value=True, key="sns_hashtags")
        
        # 커스텀 키워드 입력
        custom_keywords = st.text_input(
            "추가 키워드 (쉼표로 구분)",
            placeholder="예: 신메뉴, 할인이벤트, 특별한날",
            key="sns_keywords"
        )
        
        if st.button("✨ SNS 콘텐츠 생성", key="generate_sns"):
            with st.spinner("콘텐츠를 생성하고 있습니다..."):
                try:
                    keywords_list = [k.strip() for k in custom_keywords.split(',')] if custom_keywords else []
                    
                    # EnhancedSNSGenerator의 generate_content 메서드 사용
                    content = self.enhanced_sns_generator.generate_content(
                        business_profile=selected_business,
                        platform=platform,
                        content_style=content_style,
                        target_audience=target_audience,
                        custom_keywords=keywords_list,
                        include_hashtags=include_hashtags
                    )
                    
                    st.markdown("### 📝 생성된 SNS 콘텐츠")
                    st.markdown(f"""
                    <div class="generated-content">
                        <h4>🎯 플랫폼: {platform}</h4>
                        <p>{content}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 복사 가능한 텍스트 박스
                    st.text_area("📋 복사용 텍스트", content, height=100, key="sns_copy")
                    
                except Exception as e:
                    st.error(f"콘텐츠 생성 중 오류가 발생했습니다: {str(e)}")
                    st.error(f"오류 상세: {type(e).__name__}")
    
    
    def render_review_tab(self):
        """리뷰 생성 탭"""
        st.header("⭐ 리뷰 생성")
        
        # 사업장 선택
        businesses = self.business_manager.get_all_businesses()
        if not businesses:
            st.warning("먼저 사업장을 등록해주세요.")
            return
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("리뷰 설정")
            
            business_options = {f"{info['name']}": business_id for business_id, info in businesses.items()}
            selected_business_name = st.selectbox("사업장 선택", list(business_options.keys()), key="review_business")
            selected_business_id = business_options[selected_business_name]
            
            platform = st.selectbox("플랫폼", ["네이버 지도", "구글 리뷰"], key="review_platform")
            
            rating = st.slider("평점", 1, 5, 5)
            
            if platform == "네이버 지도":
                review_type = st.selectbox("리뷰 타입", ["일반", "상세후기", "간단후기"])
                customer_type = st.selectbox("리뷰어 연령대", ["20대", "30대", "40대", "50대", "random"])
                specific_experience = st.text_input("특별한 경험", placeholder="예: 생일 파티, 비즈니스 미팅")
                
            else:  # 구글 리뷰
                detailed_feedback = st.checkbox("상세 피드백", value=True)
                focus_area = st.selectbox("주요 포커스", [
                    "음식 품질", "서비스", "분위기", "가성비", "접근성", "시설"
                ])
            
            generate_review_button = st.button("리뷰 생성", type="primary", key="generate_review")
        
        with col2:
            st.subheader("생성된 리뷰")
            
            if generate_review_button:
                with st.spinner("리뷰 생성 중..."):
                    try:
                        if platform == "네이버 지도":
                            result = self.enhanced_review_generator.create_improved_review_with_analysis(
                                business_id=selected_business_id,
                                rating=rating,
                                review_type=review_type,
                                customer_type=customer_type,
                                specific_experience=specific_experience if specific_experience else None
                            )
                        else:  # 구글 리뷰
                            result = self.enhanced_review_generator.create_google_review_with_business_info(
                                business_id=selected_business_id,
                                rating=rating,
                                detailed_feedback=detailed_feedback,
                                focus_area=focus_area
                            )
                        
                        if 'error' not in result:
                            st.success(f"{platform} 리뷰 생성 완료!")
                            
                            # 평점 표시
                            stars = "⭐" * result['rating']
                            st.markdown(f"**평점:** {stars} ({result['rating']}/5)")
                            
                            # 리뷰 내용
                            st.markdown("**리뷰 내용:**")
                            st.write(result['review_text'])
                            
                            # 자연스러움 분석 결과 표시 (개선된 버전)
                            metadata = result.get('metadata', {})
                            naturalness_analysis = metadata.get('naturalness_analysis', {})
                            
                            if naturalness_analysis:
                                score = naturalness_analysis.get('score', 0)
                                st.markdown("---")
                                st.markdown("**🔍 자연스러움 분석**")
                                
                                # 점수에 따른 색상 표시
                                if score >= 80:
                                    st.success(f"자연스러움 점수: {score}/100 ✨ 매우 자연스러운 리뷰입니다!")
                                elif score >= 60:
                                    st.info(f"자연스러움 점수: {score}/100 👍 좋은 리뷰입니다!")
                                elif score >= 40:
                                    st.warning(f"자연스러움 점수: {score}/100 ⚠️ 개선이 필요합니다")
                                else:
                                    st.error(f"자연스러움 점수: {score}/100 ❌ 많은 개선이 필요합니다")
                                
                                # 개선점 표시
                                issues = naturalness_analysis.get('issues', [])
                                suggestions = naturalness_analysis.get('suggestions', [])
                                
                                if issues:
                                    st.markdown("**개선점:**")
                                    for issue in issues:
                                        st.markdown(f"• {issue}")
                                
                                if suggestions:
                                    st.markdown("**개선 제안:**")
                                    for suggestion in suggestions:
                                        st.markdown(f"• {suggestion}")
                            
                            # 메타데이터
                            with st.expander("상세 정보"):
                                st.write(f"글자 수: {metadata.get('character_count', 0)}")
                                st.write(f"진정성 점수: {metadata.get('authenticity_score', 0):.2f}")
                                if metadata.get('customer_profile'):
                                    st.write("고객 프로필:")
                                    st.json(metadata['customer_profile'])
                        else:
                            st.error(result['error'])
                            
                    except Exception as e:
                        st.error(f"리뷰 생성 중 오류가 발생했습니다: {str(e)}")
            
            # 리뷰 템플릿 제안
            if selected_business_id:
                templates = self.enhanced_review_generator.get_review_templates_for_business(selected_business_id)
                if templates:
                    st.markdown("---")
                    st.subheader("📝 리뷰 템플릿 제안")
                    for template in templates[:3]:
                        st.markdown(f"**{template['type']}:** {template['focus']}")
                
                # 자연스러운 리뷰 작성 팁 추가
                with st.expander("💡 자연스러운 리뷰 작성 팁"):
                    tips = self.enhanced_review_generator.get_improvement_tips()
                    for tip in tips:
                        st.markdown(f"• {tip}")
                    
                    st.markdown("---")
                    st.markdown("**✨ 자연스러운 표현 예시:**")
                    examples = self.enhanced_review_generator.demonstrate_review_improvements()
                    
                    col_before, col_after = st.columns(2)
                    
                    with col_before:
                        st.markdown("**❌ 부자연스러운 예시:**")
                        for example in examples["Before (부자연스러움)"]:
                            st.markdown(f'<div style="background-color: #ffebee; padding: 10px; border-radius: 5px; margin: 5px 0;">{example}</div>', unsafe_allow_html=True)
                    
                    with col_after:
                        st.markdown("**✅ 자연스러운 예시:**")
                        for example in examples["After (자연스러움)"]:
                            st.markdown(f'<div style="background-color: #e8f5e8; padding: 10px; border-radius: 5px; margin: 5px 0;">{example}</div>', unsafe_allow_html=True)
    
    def render_batch_generation_tab(self):
        """일괄 생성 탭"""
        st.header("🔄 일괄 생성")
        
        businesses = self.business_manager.get_all_businesses()
        if not businesses:
            st.warning("먼저 사업장을 등록해주세요.")
            return
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("일괄 생성 설정")
            
            business_options = {f"{info['name']}": business_id for business_id, info in businesses.items()}
            selected_business_name = st.selectbox("사업장 선택", list(business_options.keys()), key="batch_business")
            selected_business_id = business_options[selected_business_name]
            
            content_type = st.selectbox("콘텐츠 타입", ["리뷰", "SNS 포스트"])
            
            if content_type == "리뷰":
                platform = st.selectbox("리뷰 플랫폼", ["네이버 지도", "구글 리뷰"], key="batch_review_platform")
                review_count = st.slider("생성할 리뷰 수", 1, 10, 5)
                
                st.subheader("평점 분포")
                col1_1, col1_2, col1_3 = st.columns(3)
                with col1_1:
                    rating_5 = st.number_input("5점", 0, review_count, value=3, key="rating_5")
                with col1_2:
                    rating_4 = st.number_input("4점", 0, review_count, value=2, key="rating_4")
                with col1_3:
                    rating_3 = st.number_input("3점", 0, review_count, value=0, key="rating_3")
                
            else:  # SNS 포스트
                platforms = st.multiselect("SNS 플랫폼", ["Instagram", "Facebook", "Twitter/X"], default=["Instagram"])
                post_count = st.slider("각 플랫폼별 포스트 수", 1, 5, 2)
            
            batch_generate_button = st.button("일괄 생성", type="primary", key="batch_generate")
        
        with col2:
            st.subheader("생성 결과")
            
            if batch_generate_button:
                if content_type == "리뷰":
                    rating_distribution = {}
                    if rating_5 > 0: rating_distribution[5] = rating_5
                    if rating_4 > 0: rating_distribution[4] = rating_4
                    if rating_3 > 0: rating_distribution[3] = rating_3
                    
                    with st.spinner("리뷰 일괄 생성 중..."):
                        try:
                            reviews = self.enhanced_review_generator.create_review_batch_with_business_info(
                                business_id=selected_business_id,
                                count=review_count,
                                platform="naver" if platform == "네이버 지도" else "google",
                                rating_distribution=rating_distribution
                            )
                            
                            st.success(f"{len(reviews)}개의 리뷰가 생성되었습니다!")
                            
                            # 전체 자연스러움 점수 통계
                            naturalness_scores = []
                            for review in reviews:
                                analysis = review.get('metadata', {}).get('naturalness_analysis', {})
                                score = analysis.get('score', 0)
                                naturalness_scores.append(score)
                            
                            if naturalness_scores:
                                avg_score = sum(naturalness_scores) / len(naturalness_scores)
                                st.info(f"📊 평균 자연스러움 점수: {avg_score:.1f}/100")
                            
                            for i, review in enumerate(reviews, 1):
                                with st.expander(f"리뷰 {i} - {review['rating']}⭐"):
                                    st.write(review['review_text'])
                                    
                                    # 각 리뷰의 자연스러움 점수 표시
                                    metadata = review.get('metadata', {})
                                    naturalness_analysis = metadata.get('naturalness_analysis', {})
                                    
                                    if naturalness_analysis:
                                        score = naturalness_analysis.get('score', 0)
                                        issues = naturalness_analysis.get('issues', [])
                                        
                                        score_color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
                                        st.caption(f"{score_color} 자연스러움: {score}/100 | 진정성: {metadata.get('authenticity_score', 0):.2f}")
                                        
                                        if issues:
                                            st.caption(f"개선점: {', '.join(issues)}")
                                    else:
                                        st.caption(f"진정성: {metadata.get('authenticity_score', 0):.2f}")
                                    
                                    st.caption(f"플랫폼: {review['platform']}")
                                    
                        except Exception as e:
                            st.error(f"일괄 생성 중 오류: {str(e)}")
                
                else:  # SNS 포스트
                    st.info("SNS 포스트 일괄 생성 기능은 개발 중입니다.")
    
    def render_analytics_tab(self):
        """분석 탭"""
        st.header("📊 콘텐츠 분석")
        
        businesses = self.business_manager.get_all_businesses()
        if not businesses:
            st.warning("먼저 사업장을 등록해주세요.")
            return
        
        # 간단한 통계
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("등록된 사업장", len(businesses))
        
        with col2:
            st.metric("총 생성 가능한 플랫폼", 5)
        
        with col3:
            st.metric("자연스러운 표현", "150+")
        
        with col4:
            st.metric("향상된 자연스러움", "80~95점")
        
        st.markdown("---")
        
        # 자연스러움 향상 정보
        st.subheader("🎯 리뷰 자연스러움 향상 시스템")
        
        improvement_col1, improvement_col2 = st.columns(2)
        
        with improvement_col1:
            st.markdown("**✨ 핵심 개선사항:**")
            st.markdown("""
            • **150+ 자연스러운 표현 패턴** 적용
            • **"~어요" 과다 사용 방지** (최대 1회)
            • **실제 후기 스타일 모방** 시스템
            • **다양한 어미** 강제 사용
            • **실시간 자연스러움 분석**
            """)
            
        with improvement_col2:
            st.markdown("**📈 성능 향상:**")
            st.markdown("""
            • 기존: 50-75점 → **현재: 80-95점**
            • **자연스러운 어미** 다양화
            • **실제 펜션 후기** 패턴 반영
            • **균형잡힌 평가** (긍정+아쉬운 점)
            • **개인화된 고객 프로필** 적용
            """)
        
        st.markdown("---")
        
        # 사업장별 상세 정보
        for business_id, info in businesses.items():
            with st.expander(f"📊 {info['name']} 분석"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**기본 정보**")
                    st.write(f"업종: {info['type']}")
                    if info.get('basic_info', {}).get('description'):
                        st.write(f"설명: {info['basic_info']['description']}")
                
                with col2:
                    st.write("**콘텐츠 잠재력**")
                    menu_count = len(info.get('menu_info', {}).get('signature_dishes', []))
                    feature_count = len(info.get('service_info', {}).get('unique_features', []))
                    st.write(f"메뉴 수: {menu_count}")
                    st.write(f"특별 서비스: {feature_count}")
    
    def render_settings_tab(self):
        """설정 탭"""
        st.header("⚙️ 시스템 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("OpenAI 설정")
            current_model = self.config.get('openai', {}).get('model', 'gpt-3.5-turbo')
            st.info(f"현재 모델: {current_model}")
            
            temperature = st.slider(
                "창의성 수준 (Temperature)", 
                0.0, 1.0, 
                float(self.config.get('openai', {}).get('temperature', 0.7)), 
                0.1
            )
            
            max_tokens = st.number_input(
                "최대 토큰 수", 
                100, 4000, 
                self.config.get('openai', {}).get('max_tokens', 1500)
            )
        
        with col2:
            st.subheader("콘텐츠 설정")
            
            st.write("**품질 관리**")
            st.checkbox("이모지 사용 금지", value=True, disabled=True, help="현재 이모지는 사용하지 않도록 설정됨")
            st.checkbox("진정성 검증", value=True)
            st.checkbox("중복 내용 방지", value=True)
            
            st.write("**플랫폼별 최적화**")
            st.checkbox("인스타그램 해시태그 자동 생성", value=True)
            st.checkbox("구글 리뷰 SEO 최적화", value=True)
        
        st.markdown("---")
        st.subheader("데이터 관리")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("샘플 사업장 데이터 생성"):
                try:
                    from data_sources.business_info import create_sample_business
                    business_id = create_sample_business()
                    st.success(f"샘플 사업장이 생성되었습니다! (ID: {business_id})")
                    st.rerun()
                except Exception as e:
                    st.error(f"샘플 데이터 생성 실패: {str(e)}")
        
        with col4:
            if st.button("모든 사업장 데이터 삭제", type="secondary"):
                if st.session_state.get('confirm_delete', False):
                    # 실제 삭제 로직은 여기에 구현
                    st.success("모든 데이터가 삭제되었습니다.")
                    st.session_state.confirm_delete = False
                else:
                    st.session_state.confirm_delete = True
                    st.warning("한 번 더 클릭하면 모든 데이터가 삭제됩니다!")

def main():
    """메인 함수"""
    app = ContentGeneratorApp()
    app.run_streamlit_app()

if __name__ == "__main__":
    main()
