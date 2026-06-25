"""
Phase 2: 분석 엔진 (Analyzer)
사용자의 100가지 질문 응답을 분석하여 사용자 프로필을 생성합니다.
"""

import json
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from src import utils


@dataclass
class CategoryAnalysis:
    """카테고리별 분석 결과"""
    name: str
    questions_count: int
    average_score: float
    normalized_score: float
    priority_level: str
    weight: float
    weighted_score: float


@dataclass
class UserProfile:
    """사용자 프로필"""
    category_analyses: Dict[str, Dict[str, Any]]
    overall_score: float
    performance_recommendation: str
    portability_preference: str
    os_recommendation: str
    budget_preference: str
    top_3_priorities: List[Tuple[str, float]]
    

class Analyzer:
    """
    사용자 응답을 분석하고 프로필을 생성하는 클래스
    """
    
    def __init__(self, scoring_rules_path: str = "data/scoring_rules.json"):
        """
        분석기 초기화
        
        Args:
            scoring_rules_path: 점수 계산 규칙 JSON 파일 경로
        """
        self.scoring_rules = utils.load_json_file(scoring_rules_path)
        self.category_weights = self.scoring_rules.get('scoring_rules', {}).get('category_weights', {})
        self.priority_thresholds = self.scoring_rules.get('scoring_rules', {}).get('priority_thresholds', {})
    
    
    def analyze_responses(
        self, 
        all_responses: Dict[str, List[int]]
    ) -> UserProfile:
        """
        모든 카테고리의 응답을 분석합니다.
        
        Args:
            all_responses: {카테고리명: [점수들]} 형태의 응답 데이터
            
        Returns:
            UserProfile 객체
        """
        category_analyses = {}
        weighted_scores = {}
        
        for category, responses in all_responses.items():
            analysis = self._analyze_category(category, responses)
            category_analyses[category] = asdict(analysis)
            weighted_scores[category] = analysis.weighted_score
        
        # 상위 3개 우선순위 카테고리 추출
        top_3_priorities = sorted(
            weighted_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        # 전체 점수 계산
        overall_score = sum(weighted_scores.values()) / len(weighted_scores) if weighted_scores else 0
        
        # 추천사항 생성
        perf_rec = self._get_performance_recommendation(category_analyses)
        port_pref = self._get_portability_preference(category_analyses)
        os_rec = self._get_os_recommendation(category_analyses)
        budget_pref = self._get_budget_preference(category_analyses)
        
        profile = UserProfile(
            category_analyses=category_analyses,
            overall_score=overall_score,
            performance_recommendation=perf_rec,
            portability_preference=port_pref,
            os_recommendation=os_rec,
            budget_preference=budget_pref,
            top_3_priorities=top_3_priorities
        )
        
        return profile
    
    
    def _analyze_category(
        self, 
        category: str, 
        responses: List[int]
    ) -> CategoryAnalysis:
        """
        단일 카테고리를 분석합니다.
        
        Args:
            category: 카테고리명
            responses: 해당 카테고리의 1-5 점수 리스트
            
        Returns:
            CategoryAnalysis 객체
        """
        if not responses:
            return CategoryAnalysis(
                name=category,
                questions_count=0,
                average_score=0,
                normalized_score=0,
                priority_level="low",
                weight=0,
                weighted_score=0
            )
        
        # 평균 점수 계산
        avg_score = sum(responses) / len(responses)
        
        # 정규화 (0-100 범위)
        normalized_score = utils.normalize_score(avg_score, min_val=1, max_val=5)
        
        # 우선순위 레벨 결정
        priority_level = self._get_priority_level(avg_score)
        
        # 가중치 적용
        weight = self.category_weights.get(category, 1.0)
        weighted_score = normalized_score * weight
        
        return CategoryAnalysis(
            name=category,
            questions_count=len(responses),
            average_score=avg_score,
            normalized_score=normalized_score,
            priority_level=priority_level,
            weight=weight,
            weighted_score=weighted_score
        )
    
    
    def _get_priority_level(self, score: float) -> str:
        """
        1-5 스케일의 점수로부터 우선순위 레벨을 결정합니다.
        
        Args:
            score: 1-5 범위의 점수
            
        Returns:
            우선순위 레벨
        """
        if score >= 4.5:
            return "critical"
        elif score >= 3.5:
            return "high"
        elif score >= 2.5:
            return "medium"
        else:
            return "low"
    
    
    def _get_performance_recommendation(self, analyses: Dict[str, Dict[str, Any]]) -> str:
        """
        성능 점수를 기반으로 추천 성능 레벨을 반환합니다.
        """
        perf = analyses.get('performance', {}).get('normalized_score', 0)
        usage = analyses.get('usage_purpose', {}).get('normalized_score', 0)
        
        combined = (perf * 0.6) + (usage * 0.4)
        
        if combined >= 80:
            return "🔥 극고성능 (AI/ML, 4K 영상 편집)"
        elif combined >= 60:
            return "⚡ 고성능 (게이밍, 3D 작업)"
        elif combined >= 40:
            return "💻 중급 성능 (개발, 멀티태스킹)"
        else:
            return "📱 기본 성능 (일반 업무)"
    
    
    def _get_portability_preference(self, analyses: Dict[str, Dict[str, Any]]) -> str:
        """
        휴대성 선호도를 분석합니다.
        """
        portability = analyses.get('portability', {}).get('normalized_score', 0)
        
        if portability >= 75:
            return "🎒 극도로 휴대성 우선 (13인치 이하, 1kg 이하)"
        elif portability >= 50:
            return "🏃 휴대성 중요 (14-15인치, 1.5kg 이하)"
        else:
            return "🏠 휴대성 보통 (15인치 이상 가능)"
    
    
    def _get_os_recommendation(self, analyses: Dict[str, Dict[str, Any]]) -> str:
        """
        운영체제 추천을 반환합니다.
        """
        os_score = analyses.get('os_ecosystem', {}).get('normalized_score', 0)
        
        if os_score >= 75:
            return "🍎 macOS 강력 추천 (애플 에코시스템)"
        elif os_score >= 50:
            return "⚖️ OS 중립 - 선택 가능"
        else:
            return "🪟 Windows 추천"
    
    
    def _get_budget_preference(self, analyses: Dict[str, Dict[str, Any]]) -> str:
        """
        예산 선호도를 분석합니다.
        """
        budget = analyses.get('budget', {}).get('normalized_score', 0)
        
        if budget >= 75:
            return "💎 프리미엄 (200만원 이상)"
        elif budget >= 50:
            return "💰 중간가 (100~200만원)"
        else:
            return "💵 저가형 (~100만원)"
    
    
    def print_analysis_report(self, profile: UserProfile) -> None:
        """
        분석 결과를 보기 좋게 출력합니다.
        
        Args:
            profile: 분석된 사용자 프로필
        """
        print("\n" + "="*70)
        print("📊 노트북 추천 분석 리포트")
        print("="*70)
        
        print(f"\n📈 전체 점수: {profile.overall_score:.1f}/100")
        print(f"\n🎯 성능 추천: {profile.performance_recommendation}")
        print(f"🎒 휴대성: {profile.portability_preference}")
        print(f"🖥️ OS 추천: {profile.os_recommendation}")
        print(f"💰 예산대: {profile.budget_preference}")
        
        print("\n📋 카테고리별 분석:")
        print("-" * 70)
        
        for cat_name, analysis in sorted(profile.category_analyses.items()):
            score = analysis['normalized_score']
            priority = analysis['priority_level']
            bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
            print(f"{cat_name:20} [{bar}] {score:.1f}% ({priority})")
        
        print("\n⭐ 상위 3개 우선순위:")
        print("-" * 70)
        for i, (cat, score) in enumerate(profile.top_3_priorities, 1):
            print(f"{i}. {cat}: {score:.1f}")
        
        print("\n" + "="*70 + "\n")
    
    
    def save_profile(self, profile: UserProfile, filepath: str) -> bool:
        """
        프로필을 JSON으로 저장합니다.
        
        Args:
            profile: 사용자 프로필
            filepath: 저장할 경로
            
        Returns:
            성공 여부
        """
        profile_dict = {
            "category_analyses": profile.category_analyses,
            "overall_score": profile.overall_score,
            "performance_recommendation": profile.performance_recommendation,
            "portability_preference": profile.portability_preference,
            "os_recommendation": profile.os_recommendation,
            "budget_preference": profile.budget_preference,
            "top_3_priorities": [{"category": cat, "score": score} for cat, score in profile.top_3_priorities]
        }
        
        return utils.save_json_file(filepath, profile_dict)
