#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_generator.enhanced_review_generator import EnhancedReviewGenerator

def test_pension_without_pool():
    """수영장이 없는 펜션 리뷰 테스트"""
    generator = EnhancedReviewGenerator()
    
    print("=== 조용한 산속 펜션 (수영장 없음) 리뷰 테스트 ===\n")
    
    # 5번 생성하여 수영장 언급 여부 확인
    for i in range(5):
        try:
            result = generator.create_improved_review_with_analysis(
                business_id="pension_002",  # 수영장이 없는 펜션
                rating=None  # 랜덤 평점
            )
            
            if 'error' in result:
                print(f"오류: {result['error']}")
                continue
                
            print(f"{i+1}번째 리뷰:")
            rating_stars = "★" * result['rating']
            print(f"{rating_stars} ({result['rating']}점)")
            print(f'"{result["review_text"]}"')
            
            # 수영장/자쿠지 언급 여부 체크
            review_text = result["review_text"]
            pool_mentions = []
            if "수영장" in review_text:
                pool_mentions.append("수영장")
            if "자쿠지" in review_text:
                pool_mentions.append("자쿠지")
            if "스파" in review_text:
                pool_mentions.append("스파")
                
            if pool_mentions:
                print(f"⚠️  없는 시설 언급됨: {', '.join(pool_mentions)}")
            else:
                print("✅ 적절한 시설만 언급됨")
            
            naturalness = result['metadata']['naturalness_analysis']
            print(f"자연스러움 점수: {naturalness['total_score']}/100")
            print("-" * 50)
            
        except Exception as e:
            print(f"리뷰 생성 중 오류: {e}")

if __name__ == "__main__":
    test_pension_without_pool()
