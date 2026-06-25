# 🖥️ Notebook Recommendation App

사용자의 노트북 사양을 분석하고 최적의 노트북을 추천하는 애플리케이션입니다.

## 📋 주요 기능

### Phase 1: 질문 시스템 ✅
- 100가지 질문을 통한 사용자 프로필 분석
- 성능, 용도, 예산, 휴대성 등 종합 평가

### Phase 2: 분석 엔진
- 사용자 답변 점수화 및 분석
- 사용 패턴 파악
- 우선순위 결정

### Phase 3: 추천 시스템
- 그램, 마이크로소프트, 삼성, 레노버, 애플 제품 데이터베이스
- AI 기반 매칭 알고리즘
- 최적 제품 추천

## 🛠️ 기술 스택

- **언어**: Python 3.11+
- **프레임워크**: Streamlit
- **데이터**: JSON

## 📁 프로젝트 구조

```
laughing-journey/
├── README.md
├── requirements.txt
├── data/
│   ├── questions.json          # Phase 1: 100가지 질문
│   ├── products.json           # Phase 3: 노트북 제품 데이터
│   └── scoring_rules.json      # Phase 2: 점수 계산 규칙
├── src/
│   ├── app.py                  # 메인 애플리케이션
│   ├── analyzer.py             # Phase 2: 분석 엔진
│   ├── recommender.py          # Phase 3: 추천 시스템
│   └── utils.py                # 유틸리티 함수
└── tests/
    └── test_analyzer.py
```

## 🚀 실행 방법

```bash
# 1. 필요한 패키지 설치
pip install -r requirements.txt

# 2. 앱 실행
streamlit run src/app.py
```

## 📝 개발 로드맵

- [x] Phase 1: 질문 시스템 구축
- [ ] Phase 2: 분석 엔진 개발
- [ ] Phase 3: 추천 시스템 구현

---

**Author**: pororojun2013-oss
