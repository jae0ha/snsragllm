"""
다양한 스타일의 자연스러운 리뷰 생성 테스트
"""

from content_generator.enhanced_review_generator import EnhancedReviewGenerator
from data_sources.business_info import BusinessInfoManager

def test_diverse_reviews():
    """다양한 스타일의 리뷰 생성 테스트"""
    
    generator = EnhancedReviewGenerator()
    business_manager = BusinessInfoManager()
    
    businesses = business_manager.get_all_businesses()
    if businesses:
        business_id = list(businesses.keys())[0]
        business_name = businesses[business_id]['name']
        
        print(f'=== {business_name} 다양한 스타일 리뷰 테스트 ===\n')
        
        # 5개의 다양한 스타일 리뷰 생성
        for i in range(5):
            print(f'{i+1}번째 리뷰:')
            review = generator.create_improved_review_with_analysis(
                business_id=business_id,
                rating=5 if i < 3 else 4,
                customer_type='random'
            )
            
            if 'error' not in review:
                print(f'★★★★★ ({review["rating"]}점)')
                print(review['review_text'])
                
                # 자연스러움 분석 결과 출력
                analysis = review['metadata'].get('naturalness_analysis', {})
                print(f'자연스러움 점수: {analysis.get("score", 0)}/100')
                if analysis.get('issues'):
                    print(f'개선점: {analysis["issues"]}')
                print('-' * 50)
            else:
                print(f'오류: {review["error"]}')
                
    else:
        print('등록된 사업장이 없습니다.')

if __name__ == "__main__":
    test_diverse_reviews()
