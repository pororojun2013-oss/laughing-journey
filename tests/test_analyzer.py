"""
Phase 2 분석 엔진 테스트
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import Analyzer


def test_analyzer():
    """분석 엔진 테스트"""
    
    # 샘플 응답 데이터 생성
    sample_responses = {
        "usage_purpose": [5, 5, 4, 5, 4, 3, 3, 4, 4, 4],
        "performance": [5, 5, 5, 5, 4, 3, 4, 4, 5, 4],
        "storage": [4, 4, 3, 3, 3, 2, 2, 3, 3, 2],
        "display": [4, 4, 3, 4, 3, 3, 3, 4, 3, 4],
        "portability": [5, 5, 5, 4, 5, 4, 5, 4, 4, 5],
        "connectivity": [3, 3, 2, 3, 2, 2, 2, 3, 2, 2],
        "audio_video": [3, 3, 2, 3, 2, 2, 2, 2, 2, 3],
        "keyboard_input": [4, 3, 3, 4, 3, 3, 2, 3, 3, 3],
        "os_ecosystem": [2, 2, 2, 3, 2, 4, 4, 5, 4, 4],
        "build_quality": [4, 4, 4, 4, 4, 3, 3, 4, 4, 4],
        "cooling_thermal": [4, 4, 3, 3, 3, 3, 2, 3, 3, 3],
        "budget": [3, 3, 3, 3, 3, 2, 2, 3, 2, 3],
        "warranty_support": [3, 3, 2, 2, 2, 2, 2, 2, 2, 2],
        "upgrade_repair": [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        "specific_features": [2, 2, 2, 2, 2, 1, 1, 2, 1, 1],
        "brand_preference": [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        "environmental": [2, 2, 2, 2, 2, 1, 1, 2, 1, 1]
    }
    
    print("✅ 분석기 초기화 중...")
    analyzer = Analyzer()
    
    print("✅ 응답 분석 중...")
    profile = analyzer.analyze_responses(sample_responses)
    
    print("✅ 결과 출력 중...")
    analyzer.print_analysis_report(profile)
    
    print("✅ 프로필 저장 중...")
    analyzer.save_profile(profile, "tests/sample_profile.json")
    
    print("✅ 모든 테스트 완료!")
    
    return profile


if __name__ == "__main__":
    test_analyzer()
