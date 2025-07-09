import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# YouTube API 설정
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# 앱 설정
APP_TITLE = '🎬 유튜브 트렌드 키워드 분석기'
APP_ICON = '🎬'
APP_LAYOUT = 'wide'

# 데이터 수집 설정
MAX_RESULTS = 50  # 한 번에 가져올 동영상 수
TRENDING_REGION = 'KR'  # 트렌딩 지역 (한국)
CACHE_TTL = 3600  # 캐시 유효 시간 (초)

# 텍스트 처리 설정
MIN_WORD_LENGTH = 2  # 최소 단어 길이
MAX_KEYWORDS = 50  # 최대 키워드 수

# 시각화 설정
WORDCLOUD_WIDTH = 800
WORDCLOUD_HEIGHT = 400
WORDCLOUD_BACKGROUND = 'white'
WORDCLOUD_COLORMAP = 'viridis'

# 카테고리 매핑 (YouTube API 카테고리 ID)
CATEGORY_MAPPING = {
    '1': '영화 및 애니메이션',
    '2': '자동차',
    '10': '음악',
    '15': '애완동물',
    '17': '스포츠',
    '19': '여행 및 이벤트',
    '20': '게임',
    '22': '사람 및 블로그',
    '23': '코미디',
    '24': '엔터테인먼트',
    '25': '뉴스 및 정치',
    '26': '노하우 및 스타일',
    '27': '교육',
    '28': '과학 및 기술'
}

# 불용어 설정
CUSTOM_STOPWORDS_KR = [
    '그냥', '진짜', '정말', '너무', '완전', '엄청', '되게', '정말로',
    '그래서', '그런데', '그리고', '하지만', '그러나', '때문에', '그러면',
    '안녕하세요', '여러분', '구독', '좋아요', '댓글', '알림', '설정'
]

CUSTOM_STOPWORDS_EN = [
    'video', 'youtube', 'subscribe', 'like', 'comment', 'notification',
    'bell', 'icon', 'channel', 'playlist', 'watch', 'viewers'
] 