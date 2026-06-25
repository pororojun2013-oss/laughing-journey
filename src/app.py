"""
메인 Streamlit 애플리케이션
사용자 질문 > 분석 > 추천 전체 흐름을 관리합니다.
"""

import streamlit as st
import json
from src.analyzer import Analyzer
from src.recommender import Recommender
from src import utils


def load_questions():
    """질문 데이터 로드"""
    return utils.load_json_file("data/questions.json")


def initialize_session_state():
    """Streamlit 세션 상태 초기화"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'welcome'
    if 'responses' not in st.session_state:
        st.session_state.responses = {}
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None


def show_welcome():
    """웰컴 페이지"""
    st.set_page_config(page_title="노트북 추천 앱", layout="wide")
    
    st.title("🖥️ 노트북 추천 시스템")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📋 이 앱이 하는 일
        
        - **100가지 질문**으로 당신의 필요 사항을 파악합니다
        - **AI 분석**으로 최적의 노트북을 찾습니다
        - **구체적인 모델명**을 추천합니다
        
        ### ✨ 주요 기능
        
        - 성능, 휴대성, 예산 등 종합 평가
        - 카테고리별 우선순위 분석
        - 상위 3개 노트북 추천
        """)
    
    with col2:
        st.markdown("""
        ### 🚀 시작하기
        
        버튼을 클릭하여 시작하세요!
        
        소요 시간: **약 5-10분**
        
        ### 💡 팁
        
        - 솔직하게 답변해주세요
        - 스킵 불가능 (모든 질문 필수)
        - 언제든지 뒤로 가기 가능
        """)
    
    st.markdown("---")
    
    if st.button("🎯 시작하기", use_container_width=True, key="start_button"):
        st.session_state.current_step = 'questions'
        st.rerun()


def show_questions():
    """질문 페이지"""
    st.set_page_config(page_title="노트북 추천 - 질문", layout="wide")
    st.title("🎯 당신에 대해 알려주세요")
    st.markdown("---")
    
    questions_data = load_questions()
    categories = questions_data.get('categories', {})
    
    # 진행도 표시
    total_questions = sum(len(cat['questions']) for cat in categories.values())
    answered = sum(len(st.session_state.responses.get(cat_name, [])) 
                   for cat_name in categories.keys())
    
    st.progress(answered / total_questions, f"진행도: {answered}/{total_questions}")
    
    # 카테고리별 질문 표시
    for category_name, category_data in categories.items():
        with st.expander(f"📌 {category_data['category_name']}", expanded=False):
            if category_name not in st.session_state.responses:
                st.session_state.responses[category_name] = []
            
            responses = st.session_state.responses[category_name]
            
            for idx, question in enumerate(category_data['questions']):
                # 응답 선택
                response = st.radio(
                    question,
                    options=[1, 2, 3, 4, 5],
                    format_func=lambda x: {
                        1: "전혀 중요하지 않음",
                        2: "별로 중요하지 않음",
                        3: "보통",
                        4: "중요",
                        5: "매우 중요"
                    }[x],
                    key=f"{category_name}_{idx}",
                    horizontal=True
                )
                
                # 응답 저장
                if len(responses) <= idx:
                    responses.append(response)
                else:
                    responses[idx] = response
            
            st.session_state.responses[category_name] = responses
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ 돌아가기", use_container_width=True):
            st.session_state.current_step = 'welcome'
            st.rerun()
    
    with col2:
        if st.button("✅ 분석하기", use_container_width=True, key="analyze_button"):
            # 모든 응답 확인
            all_answered = all(
                len(st.session_state.responses.get(cat_name, [])) > 0
                for cat_name in categories.keys()
            )
            
            if all_answered:
                # 분석 진행
                analyzer = Analyzer()
                profile = analyzer.analyze_responses(st.session_state.responses)
                st.session_state.user_profile = profile
                st.session_state.current_step = 'analysis'
                st.rerun()
            else:
                st.error("❌ 모든 질문에 답변해주세요!")


def show_analysis():
    """분석 결과 페이지"""
    st.set_page_config(page_title="노트북 추천 - 분석", layout="wide")
    st.title("📊 분석 결과")
    st.markdown("---")
    
    profile = st.session_state.user_profile
    
    if profile:
        # 전체 점수
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 전체 점수", f"{profile['overall_score']:.1f}/100")
        
        with col2:
            st.metric("⚡ 성능 추천", profile['performance_recommendation'].split()[0])
        
        with col3:
            st.metric("🎒 휴대성", profile['portability_preference'].split()[0])
        
        with col4:
            st.metric("💰 예산", profile['budget_preference'].split()[0])
        
        st.markdown("---")
        
        # 상세 정보
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 추천사항")
            st.write(f"**성능**: {profile['performance_recommendation']}")
            st.write(f"**휴대성**: {profile['portability_preference']}")
            st.write(f"**OS**: {profile['os_recommendation']}")
            st.write(f"**예산**: {profile['budget_preference']}")
        
        with col2:
            st.subheader("⭐ 상위 우선순위")
            for i, (cat, score) in enumerate(profile['top_3_priorities'], 1):
                st.write(f"{i}. **{cat}**: {score:.1f}")
        
        st.markdown("---")
        
        # 카테고리별 상세 분석
        st.subheader("📋 카테고리별 분석")
        
        category_scores = {}
        for cat_name, analysis in profile['category_analyses'].items():
            category_scores[cat_name] = analysis['normalized_score']
        
        # 정렬하여 표시
        sorted_cats = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        cols = st.columns(3)
        for idx, (cat, score) in enumerate(sorted_cats):
            with cols[idx % 3]:
                st.metric(cat, f"{score:.1f}", "📊")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("⬅️ 다시 답변하기", use_container_width=True):
                st.session_state.current_step = 'questions'
                st.rerun()
        
        with col2:
            if st.button("➡️ 노트북 추천받기", use_container_width=True, key="recommend_button"):
                # 추천 진행
                recommender = Recommender()
                recommendations = recommender.recommend(profile, top_n=3)
                st.session_state.recommendations = recommendations
                st.session_state.current_step = 'recommendations'
                st.rerun()


def show_recommendations():
    """추천 결과 페이지"""
    st.set_page_config(page_title="노트북 추천 - 결과", layout="wide")
    st.title("🎯 노트북 추천 결과")
    st.markdown("---")
    
    recommendations = st.session_state.recommendations
    
    if recommendations:
        for rank, rec in enumerate(recommendations, 1):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(f"🏆 #{rank} 추천: {rec.product_name}")
                    st.write(f"**제조사**: {rec.manufacturer}")
                    st.write(f"**가격**: ₩{rec.price:,}")
                    st.write(f"**매칭도**: {rec.match_score:.1f}%")
                    st.write(f"**추천 이유**: {', '.join(rec.match_reasons)}")
                    st.write(f"**사양**: {rec.specs_summary}")
                
                with col2:
                    # 매칭도 게이지
                    st.metric("매칭도", f"{rec.match_score:.0f}%")
                
                st.divider()
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 다시 분석하기", use_container_width=True):
                st.session_state.current_step = 'analysis'
                st.rerun()
        
        with col2:
            if st.button("❓ 다시 답변하기", use_container_width=True):
                st.session_state.current_step = 'questions'
                st.rerun()
        
        with col3:
            if st.button("🏠 처음부터", use_container_width=True):
                st.session_state.current_step = 'welcome'
                st.session_state.responses = {}
                st.session_state.user_profile = None
                st.session_state.recommendations = None
                st.rerun()


def main():
    """메인 함수"""
    initialize_session_state()
    
    # 현재 단계에 따라 페이지 표시
    if st.session_state.current_step == 'welcome':
        show_welcome()
    elif st.session_state.current_step == 'questions':
        show_questions()
    elif st.session_state.current_step == 'analysis':
        show_analysis()
    elif st.session_state.current_step == 'recommendations':
        show_recommendations()


if __name__ == "__main__":
    main()
