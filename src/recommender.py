"""
Phase 3: 추천 시스템 (Recommender)
분석된 사용자 프로필에 기반하여 최적의 노트북을 추천합니다.
"""

import json
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from src import utils


@dataclass
class RecommendationScore:
    """제품 추천 점수"""
    product_id: int
    product_name: str
    manufacturer: str
    price: int
    match_score: float
    match_reasons: List[str]
    specs_summary: str


class Recommender:
    """
    사용자 프로필에 기반한 노트북 추천 엔진
    """
    
    def __init__(self, products_path: str = "data/products.json"):
        """
        추천 엔진 초기화
        
        Args:
            products_path: 제품 데이터 JSON 파일 경로
        """
        self.products_data = utils.load_json_file(products_path)
        self.products = self.products_data.get('products', [])
    
    
    def recommend(self, user_profile: Dict[str, Any], top_n: int = 3) -> List[RecommendationScore]:
        """
        사용자 프로필에 맞는 상위 N개 노트북을 추천합니다.
        
        Args:
            user_profile: 분석된 사용자 프로필 (analyzer.py의 UserProfile 딕셔너리)
            top_n: 상위 추천 개수
            
        Returns:
            RecommendationScore 객체 리스트 (점수 순서대로 정렬)
        """
        scores = []
        
        for product in self.products:
            score = self._calculate_match_score(product, user_profile)
            scores.append(score)
        
        # 점수순으로 정렬
        scores.sort(key=lambda x: x.match_score, reverse=True)
        
        return scores[:top_n]
    
    
    def _calculate_match_score(
        self, 
        product: Dict[str, Any], 
        user_profile: Dict[str, Any]
    ) -> RecommendationScore:
        """
        제품과 사용자 프로필의 매칭 점수를 계산합니다.
        
        Args:
            product: 제품 정보
            user_profile: 사용자 프로필
            
        Returns:
            RecommendationScore 객체
        """
        match_score = 0.0
        reasons = []
        
        category_analyses = user_profile.get('category_analyses', {})
        
        # 1. 성능 매칭 (30%)
        performance_match = self._calculate_performance_match(product, category_analyses)
        match_score += performance_match * 0.3
        if performance_match >= 80:
            reasons.append("✅ 성능 우수")
        
        # 2. 휴대성 매칭 (20%)
        portability_match = self._calculate_portability_match(product, category_analyses)
        match_score += portability_match * 0.2
        if portability_match >= 80:
            reasons.append("✅ 휴대성 우수")
        
        # 3. 예산 매칭 (25%)
        budget_match = self._calculate_budget_match(product, category_analyses)
        match_score += budget_match * 0.25
        if budget_match >= 80:
            reasons.append("💰 가격대 적합")
        
        # 4. 디스플레이 매칭 (10%)
        display_match = self._calculate_display_match(product, category_analyses)
        match_score += display_match * 0.1
        if display_match >= 80:
            reasons.append("🖥️ 디스플레이 우수")
        
        # 5. 연결성 및 기타 (15%)
        connectivity_match = self._calculate_connectivity_match(product, category_analyses)
        match_score += connectivity_match * 0.15
        if connectivity_match >= 80:
            reasons.append("🔌 연결성 우수")
        
        specs_summary = self._create_specs_summary(product)
        
        return RecommendationScore(
            product_id=product['id'],
            product_name=product['name'],
            manufacturer=product['manufacturer'],
            price=product['price'],
            match_score=match_score,
            match_reasons=reasons if reasons else ["일반적으로 적합"],
            specs_summary=specs_summary
        )
    
    
    def _calculate_performance_match(
        self, 
        product: Dict[str, Any], 
        category_analyses: Dict[str, Any]
    ) -> float:
        """성능 매칭 점수 계산"""
        perf_score = category_analyses.get('performance', {}).get('normalized_score', 50)
        product_perf = product.get('features', {}).get('performance', 50)
        
        # 사용자의 성능 요구도와 제품 성능의 차이를 계산
        diff = abs(perf_score - product_perf)
        return max(0, 100 - diff * 0.5)
    
    
    def _calculate_portability_match(
        self, 
        product: Dict[str, Any], 
        category_analyses: Dict[str, Any]
    ) -> float:
        """휴대성 매칭 점수 계산"""
        port_score = category_analyses.get('portability', {}).get('normalized_score', 50)
        product_port = product.get('features', {}).get('portability', 50)
        
        diff = abs(port_score - product_port)
        return max(0, 100 - diff * 0.5)
    
    
    def _calculate_budget_match(
        self, 
        product: Dict[str, Any], 
        category_analyses: Dict[str, Any]
    ) -> float:
        """예산 매칭 점수 계산"""
        budget_score = category_analyses.get('budget', {}).get('normalized_score', 50)
        product_price = product.get('price', 0)
        
        # 예산 점수에 따라 선호 가격대 설정
        if budget_score >= 75:  # 프리미엄
            preferred_min, preferred_max = 2000000, 999999999
        elif budget_score >= 50:  # 중간가
            preferred_min, preferred_max = 1000000, 2000000
        else:  # 저가형
            preferred_min, preferred_max = 0, 1000000
        
        # 선호 범위 내에 있으면 높은 점수
        if preferred_min <= product_price <= preferred_max:
            return 100
        else:
            # 범위 밖이면 거리에 따라 감점
            if product_price < preferred_min:
                return max(0, 100 - (preferred_min - product_price) / 10000)
            else:
                return max(0, 100 - (product_price - preferred_max) / 10000)
    
    
    def _calculate_display_match(
        self, 
        product: Dict[str, Any], 
        category_analyses: Dict[str, Any]
    ) -> float:
        """디스플레이 매칭 점수 계산"""
        display_score = category_analyses.get('display', {}).get('normalized_score', 50)
        product_display = product.get('features', {}).get('display_quality', 50)
        
        diff = abs(display_score - product_display)
        return max(0, 100 - diff * 0.5)
    
    
    def _calculate_connectivity_match(
        self, 
        product: Dict[str, Any], 
        category_analyses: Dict[str, Any]
    ) -> float:
        """연결성 및 기타 기능 매칭 점수 계산"""
        connectivity_score = category_analyses.get('connectivity', {}).get('normalized_score', 50)
        product_connectivity = product.get('features', {}).get('connectivity', 50)
        
        diff = abs(connectivity_score - product_connectivity)
        return max(0, 100 - diff * 0.5)
    
    
    def _create_specs_summary(self, product: Dict[str, Any]) -> str:
        """제품 사양 요약 문자열 생성"""
        specs = product.get('specs', {})
        display = specs.get('display', {})
        
        summary = (
            f"💻 {specs.get('cpu', 'N/A')} | "
            f"🎮 {specs.get('gpu', 'N/A')} | "
            f"🧠 {specs.get('ram', 'N/A')}GB RAM | "
            f"💾 {specs.get('storage', 'N/A')}GB SSD | "
            f"🖥️ {display.get('size', 'N/A')}\" {display.get('resolution', 'N/A')} | "
            f"⚖️ {specs.get('weight', 'N/A')}kg | "
            f"🔋 {specs.get('battery_hours', 'N/A')}h"
        )
        return summary
    
    
    def print_recommendations(self, recommendations: List[RecommendationScore]) -> None:
        """
        추천 결과를 보기 좋게 출력합니다.
        
        Args:
            recommendations: 추천 노트북 리스트
        """
        print("\n" + "="*90)
        print("🎯 노트북 추천 결과")
        print("="*90)
        
        for rank, rec in enumerate(recommendations, 1):
            print(f"\n🏆 #{rank} 추천: {rec.product_name}")
            print(f"   제조사: {rec.manufacturer}")
            print(f"   가격: ₩{rec.price:,}")
            print(f"   매칭도: {rec.match_score:.1f}%")
            print(f"   추천 이유: {', '.join(rec.match_reasons)}")
            print(f"   사양: {rec.specs_summary}")
            print("-" * 90)
        
        print("="*90 + "\n")
    
    
    def get_recommendation_json(self, recommendations: List[RecommendationScore]) -> Dict[str, Any]:
        """
        추천 결과를 JSON 형식으로 반환합니다.
        
        Args:
            recommendations: 추천 노트북 리스트
            
        Returns:
            JSON 형식의 추천 결과
        """
        return {
            "recommendations": [
                {
                    "rank": rank,
                    "product_id": rec.product_id,
                    "product_name": rec.product_name,
                    "manufacturer": rec.manufacturer,
                    "price": rec.price,
                    "match_score": rec.match_score,
                    "match_reasons": rec.match_reasons,
                    "specs_summary": rec.specs_summary
                }
                for rank, rec in enumerate(recommendations, 1)
            ]
        }
