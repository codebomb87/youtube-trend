# 🎬 유튜브 트렌드 키워드 분석기

파이썬과 스트림릿을 기반으로 한 유튜브 트렌드 키워드 추출 웹앱입니다.

## ✨ 주요 기능

- **실시간 트렌딩 분석**: 유튜브 인기 동영상에서 키워드 추출
- **카테고리별 분석**: 음악, 게임, 교육 등 카테고리별 트렌드 분석
- **키워드 검색**: 특정 키워드 관련 동영상 분석
- **다양한 시각화**: 워드클라우드, 차트, 그래프로 데이터 표현
- **상세 통계**: 조회수, 좋아요, 댓글 수 등 상세 분석
- **불용어 처리**: NLTK, KoNLPy 라이브러리를 활용한 정확한 키워드 추출

## 🚀 시작하기

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. YouTube API 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트 생성
2. YouTube Data API v3 활성화
3. API 키 생성
4. `.env` 파일 생성 및 API 키 설정:
conda
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 수정
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 3. 한국어 자연어 처리 설정 (선택사항)

KoNLPy 사용을 위해 Java가 필요합니다:

```bash
# Windows (Chocolatey 사용)
choco install openjdk

# macOS (Homebrew 사용)
brew install openjdk

# Ubuntu/Debian
sudo apt-get install openjdk-8-jdk
```

### 4. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하여 앱을 사용할 수 있습니다.

## 📁 프로젝트 구조

```
youtube-trend/
├── app.py                 # 메인 스트림릿 앱
├── config.py             # 설정 파일
├── requirements.txt      # 의존성 패키지
├── .env.example         # 환경 변수 예시
├── utils/
│   ├── __init__.py
│   ├── youtube_api.py   # YouTube API 클라이언트
│   ├── text_processor.py # 텍스트 전처리 및 키워드 추출
│   └── visualizer.py    # 데이터 시각화
├── data/
│   └── stopwords/       # 사용자 정의 불용어
└── README.md
```

## 🔧 사용 방법

### 1. 데이터 수집 모드

- **전체 트렌딩**: 현재 인기 동영상 전체 분석
- **카테고리별**: 특정 카테고리 (음악, 게임 등) 분석
- **키워드 검색**: 특정 키워드 관련 동영상 분석

### 2. 분석 결과 확인

- **대시보드**: 주요 지표 및 키워드 차트
- **워드클라우드**: 키워드 시각화
- **상세 분석**: 조회수, 참여도 등 상세 통계
- **동영상 목록**: 분석 대상 동영상 리스트

### 3. 설정 옵션

- **최대 동영상 수**: 분석할 동영상 수 (10-50개)
- **최대 키워드 수**: 표시할 키워드 수 (10-100개)
- **최소 단어 길이**: 키워드 최소 길이 (1-5자)

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **API**: YouTube Data API v3
- **텍스트 처리**: NLTK, spaCy, KoNLPy
- **시각화**: Plotly, Matplotlib, WordCloud
- **데이터 처리**: Pandas, NumPy

## 📊 지원 기능

### 키워드 추출 알고리즘
1. YouTube API로 동영상 데이터 수집
2. HTML 태그 및 특수문자 제거
3. 형태소 분석 (한국어: KoNLPy, 영어: NLTK)
4. 불용어 제거 (라이브러리 + 사용자 정의)
5. TF-IDF 스코어링 및 빈도 분석
6. 중요도 순 키워드 정렬

### 시각화 기능
- 워드클라우드
- 키워드 빈도 막대 차트
- 키워드 분포 파이 차트
- 키워드 트리맵
- 조회수 분포 히스토그램
- 참여도 산점도
- 카테고리별 분석 차트

## 🚨 주의사항

### API 할당량
- YouTube Data API v3는 일일 할당량 제한이 있습니다 (기본 10,000 units)
- 캐싱 기능을 통해 API 호출을 최소화했습니다

### 한국어 처리
- KoNLPy 사용을 위해 Java 설치가 필요합니다
- 설치되지 않은 경우 영어 키워드만 추출됩니다

## 🤝 기여하기

1. 이 레포지토리를 포크하세요
2. 새로운 기능 브랜치를 생성하세요 (`git checkout -b feature/new-feature`)
3. 변경사항을 커밋하세요 (`git commit -am 'Add new feature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/new-feature`)
5. Pull Request를 생성하세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🔍 문제 해결

### 일반적인 문제

1. **API 키 오류**: `.env` 파일에 올바른 YouTube API 키가 설정되어 있는지 확인
2. **KoNLPy 오류**: Java가 설치되어 있고 JAVA_HOME이 설정되어 있는지 확인
3. **의존성 오류**: `pip install -r requirements.txt`로 모든 패키지 재설치

### 성능 최적화

- 캐시 설정 조정 (config.py의 CACHE_TTL)
- 동영상 수 및 키워드 수 제한
- 정기적인 캐시 클리어

---

더 많은 정보는 [프로젝트 계획서](youtube-trend-app-plan.md)를 참조하세요. 