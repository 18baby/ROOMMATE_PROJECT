# 🏠 Roommate Recommendation System

> 기숙사 룸메이트 추천 시스템 — KMeans 클러스터링과 NLP 기반 매칭

설문 조사를 통해 사용자의 생활 습관, 성격, 선호도 등을 수집하고, 클러스터링 알고리즘을 활용하여 최적의 룸메이트 후보를 추천하는 웹 애플리케이션입니다.

## Overview

- **설문 기반 프로파일링**: 2단계 설문(생활 습관 + 원하는 룸메이트 조건)을 통해 사용자 데이터 수집
- **KMeans 클러스터링**: 가중치 기반 더미 변수 변환 후 9개 클러스터로 분류 (나이, 성격, 단과대 등 다중 기준)
- **NLP 매칭**: 자유 텍스트 입력을 OKT 형태소 분석 → Redis 사전 매핑을 통해 키워드로 변환하여 매칭 정확도 향상
- **실시간 추천**: 클러스터 대표 벡터와의 거리 계산을 통해 상위 4명의 룸메이트 후보 반환

## Tech Stack

| Category | Technologies |
|----------|-------------|
| Backend | Python 3, Flask, Flask-WTF, WTForms |
| Database | MySQL, SQLAlchemy, pymysql |
| ML | scikit-learn (KMeans), pandas, numpy |
| NLP | Redis (사전 매핑), OKT 형태소 분석 (외부 Colab API) |
| Frontend | MDBootstrap, Jinja2 Templates |

## Project Structure

```
ROOMMATE_PROJECT/
├── introduce/
│   ├── application.py      # Flask 메인 앱 (라우팅, DB 모델, 설문 처리)
│   ├── h_model.py           # KMeans 클러스터링 및 그룹 대표 벡터 생성
│   ├── h_predict.py         # 매칭 예측 로직 (application.py에서 호출)
│   ├── model.py             # 보조 모델 유틸리티
│   ├── predict.py           # 대안 예측 로직
│   ├── get_db.py            # MySQL → pandas DataFrame 헬퍼
│   ├── run_dict.py          # Redis 사전 로더 및 토큰 매핑
│   ├── templates/           # Flask HTML 템플릿
│   └── static/              # 정적 파일 (CSS, JS)
├── dictionary/
│   ├── input.csv            # 사전 데이터 (토큰 → 키워드 매핑)
│   ├── dict.txt             # 사전 텍스트 파일
│   └── redis-6.2.5/         # 번들 Redis (선택사항)
├── 주피터파일/
│   ├── 라벨인코딩 생성.ipynb    # 라벨 인코딩 생성
│   ├── 문자열 생성.ipynb        # 그룹/단과대/나이 문자열 생성
│   ├── 변수별_그룹선택.ipynb    # 변수별 그룹 선택 및 EDA
│   └── 빈도분석.ipynb          # 빈도 분석
├── db_bulkload.py           # CSV → MySQL 벌크 로드 유틸리티
├── main_data.csv            # 메인 데이터셋
├── cluster별_라벨링.csv      # 클러스터링 결과 (h_model.fit_model 출력)
└── label_df.csv             # 라벨/클러스터 데이터
```

## How It Works

```
[사용자 설문 입력] → [Flask 앱 (application.py)]
        │
        ├── 1단계: 생활 습관 설문 (/servey)
        ├── 2단계: 원하는 룸메이트 조건 (/servey2)
        │
        ├── [자유 텍스트] → OKT 토큰화 (Colab API) → Redis 사전 매핑 → 키워드 추출
        │
        ├── [DB 저장] → MySQL (SQLAlchemy)
        │
        └── [매칭 수행] → h_model.fit_model (KMeans 클러스터링)
                        → h_predict.model_predict (거리 계산)
                        → 상위 4명 후보 반환 (/result)
```

## Getting Started

### Prerequisites

- Python 3.7+
- MySQL Server
- Redis Server

### Installation

```bash
# 의존성 설치
pip install Flask Flask-WTF WTForms Flask-SQLAlchemy pandas numpy scikit-learn pymysql redis requests openpyxl

# MySQL 데이터베이스 생성
mysql -u root -p -e "CREATE DATABASE users;"

# 데이터 벌크 로드
python db_bulkload.py

# Redis 시작
redis-server

# Flask 앱 실행
cd introduce
python application.py
```

앱이 `http://127.0.0.1:8484` 에서 실행됩니다.

### Environment Setup

`application.py`와 `db_bulkload.py`에서 아래 값을 환경에 맞게 수정하세요:

```python
# DB 연결 설정
DATABASE_URI = "mysql+pymysql://<username>:<password>@localhost/users"

# Flask Secret Key
SECRET_KEY = "<your-secret-key>"
```

## Notes

- **NLP 엔드포인트**: 자유 텍스트 분석을 위해 외부 Colab API (OKT 토큰화)가 실행 중이어야 합니다. 로컬 환경에서는 `konlpy.tag.Okt`를 직접 사용하여 대체할 수 있습니다.
- **Redis**: `run_dict.py`의 사전 매핑 기능 사용을 위해 Redis 서버가 필요합니다.
- **Jupyter 노트북**: `주피터파일/` 디렉토리의 노트북을 통해 클러스터링 로직과 EDA 과정을 확인할 수 있습니다.
