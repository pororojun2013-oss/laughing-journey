"""
Utility functions for the notebook recommendation app.
"""

import json
from typing import Dict, List, Any, Tuple


def load_json_file(filepath: str) -> Dict[str, Any]:
    """
    JSON 파일을 로드하고 파싱합니다.
    
    Args:
        filepath: JSON 파일 경로
        
    Returns:
        파싱된 JSON 데이터
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} 파일을 찾을 수 없습니다.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: {filepath}는 유효한 JSON이 아닙니다.")
        return {}


def save_json_file(filepath: str, data: Dict[str, Any]) -> bool:
    """
    데이터를 JSON 파일로 저장합니다.
    
    Args:
        filepath: 저장할 JSON 파일 경로
        data: 저장할 데이터
        
    Returns:
        성공 여부
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error: 파일 저장 실패 - {e}")
        return False


def normalize_score(score: float, min_val: float = 1, max_val: float = 5) -> float:
    """
    점수를 0-100 범위로 정규화합니다.
    
    Args:
        score: 원본 점수
        min_val: 최소값
        max_val: 최대값
        
    Returns:
        0-100 범위의 정규화된 점수
    """
    if max_val == min_val:
        return 0.0
    return ((score - min_val) / (max_val - min_val)) * 100


def get_priority_level(score: float, thresholds: Dict[str, float]) -> str:
    """
    점수에 따른 우선순위 레벨을 반환합니다.
    
    Args:
        score: 정규화된 점수 (0-100)
        thresholds: 임계값 딕셔너리
        
    Returns:
        우선순위 레벨 ('critical', 'high', 'medium', 'low')
    """
    if score >= 90:
        return "critical"
    elif score >= 70:
        return "high"
    elif score >= 50:
        return "medium"
    else:
        return "low"


def calculate_category_score(
    responses: List[int],
    weights: Dict[str, float],
    category_name: str
) -> Tuple[float, str]:
    """
    카테고리의 평균 점수를 계산합니다.
    
    Args:
        responses: 해당 카테고리의 응답 리스트 (1-5 점수)
        weights: 가중치 딕셔너리
        category_name: 카테고리명
        
    Returns:
        (카테고리 점수, 우선순위 레벨) 튜플
    """
    if not responses:
        return 0.0, "low"
    
    avg_score = sum(responses) / len(responses)
    weighted_score = avg_score * weights.get(category_name, 1.0)
    normalized = normalize_score(weighted_score)
    priority = get_priority_level(normalized, {})
    
    return normalized, priority


def budget_to_range(budget_str: str) -> Tuple[int, int]:
    """
    예산 문자열을 숫자 범위로 변환합니다.
    
    Args:
        budget_str: 예산 문자열 ("저가형", "중간가", "프리미엄")
        
    Returns:
        (최소값, 최대값) 튜플
    """
    budget_ranges = {
        "저가형": (0, 1000000),
        "중간가": (1000000, 2000000),
        "프리미엄": (2000000, 999999999)
    }
    return budget_ranges.get(budget_str, (0, 999999999))


def get_performance_recommendation(scores: Dict[str, float]) -> str:
    """
    성능 점수에 따라 추천 성능 레벨을 반환합니다.
    
    Args:
        scores: 카테고리별 점수
        
    Returns:
        추천 성능 레벨
    """
    performance_score = scores.get('performance', 0)
    usage_score = scores.get('usage_purpose', 0)
    
    combined_score = (performance_score * 0.6) + (usage_score * 0.4)
    
    if combined_score >= 80:
        return "극고성능 (AI/ML, 영상 편집)"
    elif combined_score >= 60:
        return "고성능 (게이밍, 전문 작업)"
    elif combined_score >= 40:
        return "중급 (개발, 멀티태스킹)"
    else:
        return "기본 (일반 업무)"


def get_portability_preference(scores: Dict[str, float]) -> str:
    """
    휴대성 선호도를 분석합니다.
    
    Args:
        scores: 카테고리별 점수
        
    Returns:
        휴대성 추천
    """
    portability_score = scores.get('portability', 0)
    
    if portability_score >= 75:
        return "극도로 휴대성 우선 (13인치 이하, 1kg 이하)"
    elif portability_score >= 50:
        return "휴대성 중요 (14-15인치, 1.5kg 이하)"
    else:
        return "휴대성 보통 (15인치 이상 가능)"


def get_os_recommendation(scores: Dict[str, float]) -> str:
    """
    운영체제 추천을 반환합니다.
    
    Args:
        scores: 카테고리별 점수
        
    Returns:
        추천 OS
    """
    os_score = scores.get('os_ecosystem', 0)
    
    if os_score >= 75:
        return "macOS 강력 추천 (애플 에코시스템)"
    elif os_score >= 50:
        return "OS 중립 - 선택 가능"
    else:
        return "Windows 추천 (소프트웨어 호환성)"


def create_user_profile(all_responses: Dict[str, List[int]]) -> Dict[str, Any]:
    """
    모든 응답으로부터 사용자 프로필을 생성합니다.
    
    Args:
        all_responses: {카테고리명: [점수들]} 형태의 응답 데이터
        
    Returns:
        사용자 프로필 딕셔너리
    """
    scores = {}
    priorities = {}
    
    # 카테고리별 가중치
    from src.analyzer import Analyzer
    analyzer = Analyzer()
    weights = analyzer.scoring_rules.get('category_weights', {})
    
    for category, responses in all_responses.items():
        score, priority = calculate_category_score(responses, weights, category)
        scores[category] = score
        priorities[category] = priority
    
    # 프로필 생성
    profile = {
        "category_scores": scores,
        "category_priorities": priorities,
        "performance_recommendation": get_performance_recommendation(scores),
        "portability_preference": get_portability_preference(scores),
        "os_recommendation": get_os_recommendation(scores),
        "overall_score": sum(scores.values()) / len(scores) if scores else 0
    }
    
    return profile


def print_category_summary(scores: Dict[str, float], priorities: Dict[str, str]) -> None:
    """
    카테고리별 점수 및 우선순위를 출력합니다.
    
    Args:
        scores: 카테고리별 점수
        priorities: 카테고리별 우선순위
    """
    print("\n" + "="*60)
    print("📊 카테고리별 분석 결과")
    print("="*60)
    
    for category in sorted(scores.keys()):
        score = scores[category]
        priority = priorities[category]
        bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
        print(f"{category:20} [{bar}] {score:.1f}% ({priority})")
    
    print("="*60 + "\n")
