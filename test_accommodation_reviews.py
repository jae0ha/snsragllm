#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_generator.enhanced_review_generator import EnhancedReviewGenerator

def test_accommodation_diverse_reviews():
    """숙박업소 다양한 스타일 리뷰 테스트"""
    generator = EnhancedReviewGenerator()
    
    print("=== 더쉼팡풀빌라 다양한 스타일 리뷰 테스트 ===\n")
    
    # 5번 생성하여 다양한 스타일 확인
    for i in range(5):
        try:
            result = generator.create_improved_review_with_analysis(
                business_id="pension_001",  # 더쉼팡풀빌라
                rating=None  # 랜덤 평점
            )
            
            if 'error' in result:
                print(f"오류: {result['error']}")
                continue
                
            print(f"{i+1}번째 리뷰:")
            rating_stars = "★" * result['rating']
            print(f"{rating_stars} ({result['rating']}점)")
            print(f'"{result["review_text"]}"')
            
            naturalness = result['metadata']['naturalness_analysis']
            print(f"자연스러움 점수: {naturalness['total_score']}/100")
            if naturalness['improvement_suggestions']:
                print(f"개선점: {naturalness['improvement_suggestions']}")
            print("-" * 50)
            
        except Exception as e:
            print(f"리뷰 생성 중 오류: {e}")

if __name__ == "__main__":
    test_accommodation_diverse_reviews()
