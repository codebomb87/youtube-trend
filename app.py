import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# 로컬 모듈 임포트
import config
from utils.youtube_api import YouTubeAPI
from utils.text_processor import TextProcessor
from utils.visualizer import Visualizer

# 페이지 설정
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.APP_LAYOUT,
    initial_sidebar_state="expanded"
)

# 스타일 설정
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """세션 상태 초기화"""
    if 'youtube_api' not in st.session_state:
        st.session_state.youtube_api = YouTubeAPI()
    if 'text_processor' not in st.session_state:
        st.session_state.text_processor = TextProcessor()
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = Visualizer()

def check_api_key():
    """API 키 확인"""
    if not config.YOUTUBE_API_KEY:
        st.error("🔑 YouTube API 키가 설정되지 않았습니다!")
        st.markdown("""
        ### API 키 설정 방법:
        1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
        2. YouTube Data API v3 활성화
        3. API 키 생성
        4. `.env` 파일에 `YOUTUBE_API_KEY=your_api_key` 추가
        """)
        st.stop()

def main():
    """메인 앱 함수"""
    # 세션 상태 초기화
    initialize_session_state()
    
    # API 키 확인
    check_api_key()
    
    # 헤더
    st.markdown(f'<div class="main-header">{config.APP_TITLE}</div>', unsafe_allow_html=True)
    
    # 사이드바 설정
    setup_sidebar()
    
    # 메인 콘텐츠
    main_content()

def setup_sidebar():
    """사이드바 설정"""
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 데이터 수집 설정
        st.subheader("📊 데이터 수집")
        
        # 분석 모드 선택
        analysis_mode = st.selectbox(
            "분석 모드",
            ["전체 트렌딩", "카테고리별", "키워드 검색"],
            help="분석할 데이터 유형을 선택하세요"
        )
        
        # 분석 모드별 추가 설정
        if analysis_mode == "카테고리별":
            category_id = st.selectbox(
                "카테고리 선택",
                options=list(config.CATEGORY_MAPPING.keys()),
                format_func=lambda x: config.CATEGORY_MAPPING[x],
                help="분석할 카테고리를 선택하세요"
            )
            st.session_state.category_id = category_id
        
        elif analysis_mode == "키워드 검색":
            search_query = st.text_input(
                "검색 키워드",
                placeholder="예: 음악, 게임, 요리...",
                help="검색할 키워드를 입력하세요"
            )
            st.session_state.search_query = search_query
        
        st.session_state.analysis_mode = analysis_mode
        
        # 데이터 수집 설정
        st.subheader("🔧 수집 설정")
        
        max_results = st.slider(
            "최대 동영상 수",
            min_value=10,
            max_value=50,
            value=config.MAX_RESULTS,
            help="분석할 최대 동영상 수"
        )
        st.session_state.max_results = max_results
        
        # 키워드 추출 설정
        st.subheader("🔍 키워드 설정")
        
        max_keywords = st.slider(
            "최대 키워드 수",
            min_value=10,
            max_value=100,
            value=config.MAX_KEYWORDS,
            help="표시할 최대 키워드 수"
        )
        st.session_state.max_keywords = max_keywords
        
        min_word_length = st.slider(
            "최소 단어 길이",
            min_value=1,
            max_value=5,
            value=config.MIN_WORD_LENGTH,
            help="추출할 키워드의 최소 길이"
        )
        st.session_state.min_word_length = min_word_length
        
        # 데이터 수집 버튼
        st.divider()
        collect_data = st.button("📈 데이터 수집 시작", use_container_width=True)
        
        if collect_data:
            st.session_state.collect_data = True
        
        # 캐시 클리어 버튼
        if st.button("🗑️ 캐시 클리어", use_container_width=True):
            st.cache_data.clear()
            st.success("캐시가 클리어되었습니다!")

def main_content():
    """메인 콘텐츠 영역"""
    
    # 데이터 수집
    if st.session_state.get('collect_data', False):
        with st.spinner("데이터를 수집하고 있습니다..."):
            df = collect_youtube_data()
            
            if df is not None and not df.empty:
                st.session_state.df = df
                st.session_state.collect_data = False
                st.success(f"✅ {len(df)}개의 동영상 데이터를 수집했습니다!")
            else:
                st.error("❌ 데이터 수집에 실패했습니다.")
                st.stop()
    
    # 데이터가 있는 경우에만 분석 표시
    if 'df' in st.session_state:
        df = st.session_state.df
        
        # 탭 구성
        tab1, tab2, tab3, tab4 = st.tabs(["📊 대시보드", "☁️ 워드클라우드", "📈 상세 분석", "🎬 동영상 목록"])
        
        with tab1:
            dashboard_tab(df)
        
        with tab2:
            wordcloud_tab(df)
        
        with tab3:
            detailed_analysis_tab(df)
        
        with tab4:
            video_list_tab(df)
    
    else:
        # 초기 화면
        st.info("👈 사이드바에서 설정을 조정하고 '데이터 수집 시작' 버튼을 클릭하세요.")
        
        # 샘플 이미지나 설명 추가
        st.markdown("""
        ### 🎯 주요 기능
        - **실시간 트렌딩 분석**: 유튜브 인기 동영상 키워드 추출
        - **카테고리별 분석**: 음악, 게임, 교육 등 카테고리별 트렌드
        - **키워드 검색**: 특정 키워드 관련 동영상 분석
        - **다양한 시각화**: 워드클라우드, 차트, 그래프
        - **상세 통계**: 조회수, 좋아요, 댓글 수 분석
        """)

def collect_youtube_data():
    """유튜브 데이터 수집"""
    try:
        youtube_api = st.session_state.youtube_api
        analysis_mode = st.session_state.analysis_mode
        max_results = st.session_state.max_results
        
        if analysis_mode == "전체 트렌딩":
            df = youtube_api.get_trending_videos(max_results=max_results)
        
        elif analysis_mode == "카테고리별":
            category_id = st.session_state.category_id
            df = youtube_api.get_videos_by_category(category_id, max_results=max_results)
        
        elif analysis_mode == "키워드 검색":
            search_query = str(st.session_state.get('search_query', ''))
            if not search_query or search_query == '':
                st.error("검색 키워드를 입력하세요.")
                return None
            df = youtube_api.search_videos(search_query, max_results=max_results)
        
        return df
        
    except Exception as e:
        st.error(f"데이터 수집 중 오류가 발생했습니다: {e}")
        return None

def dashboard_tab(df):
    """대시보드 탭"""
    st.header("📊 트렌드 대시보드")
    
    # 주요 지표
    st.session_state.visualizer.create_metric_cards(df)
    
    st.divider()
    
    # 키워드 분석
    with st.spinner("키워드를 분석하고 있습니다..."):
        keywords = st.session_state.text_processor.extract_keywords_from_dataframe(df)
        
        if keywords:
            keyword_freq = st.session_state.text_processor.get_keyword_frequency(
                keywords, 
                max_keywords=st.session_state.max_keywords
            )
            
            # 상위 키워드 차트
            col1, col2 = st.columns(2)
            
            with col1:
                bar_chart = st.session_state.visualizer.create_keyword_bar_chart(
                    keyword_freq, 
                    "🏆 상위 키워드",
                    max_keywords=15
                )
                if bar_chart:
                    st.plotly_chart(bar_chart, use_container_width=True)
            
            with col2:
                pie_chart = st.session_state.visualizer.create_keyword_pie_chart(
                    keyword_freq,
                    "📊 키워드 분포",
                    max_keywords=10
                )
                if pie_chart:
                    st.plotly_chart(pie_chart, use_container_width=True)
        
        else:
            st.warning("추출된 키워드가 없습니다.")
    
    st.divider()
    
    # 카테고리 및 채널 분석
    col1, col2 = st.columns(2)
    
    with col1:
        category_chart = st.session_state.visualizer.create_category_analysis(df)
        if category_chart:
            st.plotly_chart(category_chart, use_container_width=True)
    
    with col2:
        channel_chart = st.session_state.visualizer.create_top_channels(df)
        if channel_chart:
            st.plotly_chart(channel_chart, use_container_width=True)

def wordcloud_tab(df):
    """워드클라우드 탭"""
    st.header("☁️ 워드클라우드")
    
    with st.spinner("워드클라우드를 생성하고 있습니다..."):
        keywords = st.session_state.text_processor.extract_keywords_from_dataframe(df)
        
        if keywords:
            keyword_freq = st.session_state.text_processor.get_keyword_frequency(keywords)
            
            # 워드클라우드 생성
            wordcloud = st.session_state.text_processor.generate_wordcloud(keyword_freq)
            
            if wordcloud:
                # 워드클라우드 표시
                fig = st.session_state.visualizer.create_wordcloud_plot(wordcloud)
                if fig:
                    st.pyplot(fig)
                
                st.divider()
                
                # 트리맵 추가
                treemap = st.session_state.visualizer.create_keyword_treemap(keyword_freq)
                if treemap:
                    st.plotly_chart(treemap, use_container_width=True)
            
            else:
                st.error("워드클라우드 생성에 실패했습니다.")
        
        else:
            st.warning("워드클라우드를 생성할 키워드가 없습니다.")

def detailed_analysis_tab(df):
    """상세 분석 탭"""
    st.header("📈 상세 분석")
    
    # 조회수 분석
    col1, col2 = st.columns(2)
    
    with col1:
        view_dist = st.session_state.visualizer.create_view_count_distribution(df)
        if view_dist:
            st.plotly_chart(view_dist, use_container_width=True)
    
    with col2:
        engagement = st.session_state.visualizer.create_engagement_scatter(df)
        if engagement:
            st.plotly_chart(engagement, use_container_width=True)
    
    st.divider()
    
    # 시간별 트렌드
    timeline = st.session_state.visualizer.create_trend_timeline(df)
    if timeline:
        st.plotly_chart(timeline, use_container_width=True)
    
    st.divider()
    
    # 상관관계 분석
    correlation = st.session_state.visualizer.create_correlation_heatmap(df)
    if correlation:
        st.plotly_chart(correlation, use_container_width=True)

def video_list_tab(df):
    """동영상 목록 탭"""
    st.header("🎬 동영상 목록")
    
    # 정렬 옵션
    sort_options = {
        '조회수': 'view_count',
        '좋아요': 'like_count',
        '댓글수': 'comment_count',
        '게시일': 'published_at'
    }
    
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("정렬 기준", list(sort_options.keys()))
    with col2:
        ascending = st.checkbox("오름차순", value=False)
    
    # 데이터 정렬
    sorted_df = df.sort_values(
        sort_options[sort_by], 
        ascending=ascending
    )
    
    # 동영상 카드 표시
    st.session_state.visualizer.display_video_cards(sorted_df)
    
    st.divider()
    
    # 상세 데이터 테이블
    st.subheader("📋 상세 데이터")
    
    # 표시할 컬럼 선택
    display_columns = st.multiselect(
        "표시할 컬럼",
        df.columns.tolist(),
        default=['title', 'channel_title', 'view_count', 'like_count', 'comment_count'],
        help="테이블에 표시할 컬럼을 선택하세요"
    )
    
    if display_columns:
        st.dataframe(
            sorted_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
    
    # 데이터 다운로드
    csv = sorted_df.to_csv(index=False)
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name=f"youtube_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main() 