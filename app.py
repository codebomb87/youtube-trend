import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import time
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

# 동적 테마 시스템 사용 (스타일은 apply_theme_styles()에서 적용)

def initialize_session_state():
    """세션 상태 초기화"""
    if 'youtube_api' not in st.session_state:
        st.session_state.youtube_api = YouTubeAPI()
    if 'text_processor' not in st.session_state:
        st.session_state.text_processor = TextProcessor()
    if 'visualizer' not in st.session_state:
        st.session_state.visualizer = Visualizer()
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = "📊 대시보드"

def get_theme_colors():
    """현재 테마에 맞는 색상 팔레트 반환"""
    if st.session_state.get('dark_mode', False):
        return {
            'bg_primary': '#0e1117',
            'bg_secondary': '#262730',
            'bg_card': '#1e1e2e',
            'text_primary': '#fafafa',
            'text_secondary': '#b8b8b8',
            'accent': '#ff6b6b',
            'accent_secondary': '#4ecdc4',
            'border': '#404040',
            'success': '#51cf66',
            'warning': '#ffd43b',
            'error': '#ff6b6b',
            'info': '#339af0',
            'plotly_template': 'plotly_dark'
        }
    else:
        return {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8f9fa',
            'bg_card': '#ffffff',
            'text_primary': '#262626',
            'text_secondary': '#666666',
            'accent': '#1f77b4',
            'accent_secondary': '#ff7f0e',
            'border': '#e1e5e9',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'info': '#17a2b8',
            'plotly_template': 'plotly_white'
        }

def apply_theme_styles():
    """현재 테마에 맞는 CSS 스타일 적용"""
    colors = get_theme_colors()
    
    css = f"""
    <style>
        /* 메인 배경 */
        .stApp {{
            background-color: {colors['bg_primary']};
            color: {colors['text_primary']};
        }}
        
        /* 사이드바 */
        .css-1d391kg {{
            background-color: {colors['bg_secondary']};
        }}
        
        /* 메인 헤더 */
        .main-header {{
            font-size: 2.5rem;
            font-weight: bold;
            color: {colors['accent']};
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* 메트릭 카드 */
        .metric-card {{
            background-color: {colors['bg_card']};
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: 1px solid {colors['border']};
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        
        /* 라디오 버튼을 탭처럼 스타일링 */
        .stRadio > div {{
            background-color: {colors['bg_secondary']};
            border-radius: 12px;
            padding: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stRadio > div > label {{
            background-color: transparent;
            border-radius: 8px;
            padding: 12px 20px;
            margin: 2px;
            font-weight: 500;
            color: {colors['text_secondary']};
            transition: all 0.2s ease;
            cursor: pointer;
            border: 1px solid transparent;
        }}
        
        .stRadio > div > label:hover {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
            border-color: {colors['border']};
        }}
        
        .stRadio > div > label > div[data-testid="stMarkdownContainer"] {{
            font-size: 0.9rem;
        }}
        
        /* 선택된 라디오 버튼 스타일 */
        .stRadio input[type="radio"]:checked + label {{
            background: linear-gradient(45deg, {colors['accent']}, {colors['accent_secondary']}) !important;
            color: white !important;
            border-color: {colors['accent']} !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        
        /* 버튼 스타일 */
        .stButton > button {{
            background: linear-gradient(45deg, {colors['accent']}, {colors['accent_secondary']});
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        
        /* 다크 모드 토글 버튼 */
        .theme-toggle {{
            background: linear-gradient(45deg, {colors['accent']}, {colors['accent_secondary']});
            color: white;
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        
        .theme-toggle:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        /* 정보 박스 */
        .stAlert {{
            border-radius: 10px;
            border-left: 4px solid {colors['accent']};
        }}
        
        /* 슬라이더 */
        .stSlider > div > div > div > div {{
            background-color: {colors['accent']};
        }}
        
        /* 선택 박스 */
        .stSelectbox > div > div > div {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
        }}
        
        /* 텍스트 입력 */
        .stTextInput > div > div > input {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
        }}
        
        /* 차트 배경 */
        .js-plotly-plot {{
            background-color: {colors['bg_card']} !important;
            border-radius: 12px;
        }}
        
        /* 애니메이션 키프레임 */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .animate-fadeIn {{
            animation: fadeIn 0.5s ease-out;
        }}
        
        /* 스피너 개선 */
        .stSpinner > div {{
            border-top-color: {colors['accent']} !important;
        }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

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
    try:
        # 세션 상태 초기화
        initialize_session_state()
        
        # API 키 확인
        check_api_key()
        
        # 테마 스타일 적용
        apply_theme_styles()
        
        # 헤더 (애니메이션 클래스 추가)
        st.markdown(f'<div class="main-header animate-fadeIn">{config.APP_TITLE}</div>', unsafe_allow_html=True)
        
        # 사이드바 설정
        setup_sidebar()
        
        # 메인 콘텐츠
        main_content()
        
    except Exception as e:
        st.error(f"앱 실행 중 오류가 발생했습니다: {str(e)}")

def setup_sidebar():
    """사이드바 설정"""
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 테마 설정
        st.subheader("🎨 테마")
        
        # 다크 모드 토글
        col1, col2 = st.columns([3, 1])
        with col1:
            current_theme = "다크 모드" if st.session_state.get('dark_mode', False) else "라이트 모드"
            st.write(f"현재 테마: **{current_theme}**")
        
        with col2:
            theme_icon = "🌙" if not st.session_state.get('dark_mode', False) else "☀️"
            if st.button(theme_icon, help="테마 변경", use_container_width=True):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        st.divider()
        
        # 데이터 수집 설정
        st.subheader("📊 데이터 수집")
        
        # 분석 모드 선택
        analysis_mode = st.radio(
            "📊 분석 모드",
            ["전체 트렌딩", "카테고리별 분석", "키워드 검색"],
            help="분석하고 싶은 데이터의 종류를 선택하세요"
        )
        
        # API 제한사항 안내
        if analysis_mode == "전체 트렌딩":
            st.info("ℹ️ **YouTube API 제한**: 트렌딩 동영상은 최대 **50개**까지만 제공됩니다")
        elif analysis_mode == "카테고리별 분석":
            st.info("ℹ️ **YouTube API 제한**: 카테고리별 동영상은 최대 **50개**까지만 제공됩니다")
        elif analysis_mode == "키워드 검색":
            st.success("✅ **확장 가능**: 키워드 검색은 최대 **200개**까지 수집 가능합니다")
        
        st.divider()
        
        # 분석 모드별 추가 설정
        if analysis_mode == "카테고리별 분석":
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
        
        # 모드별 최대 동영상 수 제한
        if analysis_mode == "키워드 검색":
            max_limit = 200
            default_value = min(config.MAX_RESULTS, 200)
        else:  # 전체 트렌딩, 카테고리별 분석
            max_limit = 50
            default_value = min(config.MAX_RESULTS, 50)
        
        max_results = st.slider(
            "최대 동영상 수",
            min_value=10,
            max_value=max_limit,
            value=default_value,
            step=10,
            help=f"분석할 최대 동영상 수 (현재 모드: 최대 {max_limit}개)"
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
        
        # 현재 설정값 표시
        st.info(f"📋 현재 설정: 동영상 {max_results}개, 키워드 {max_keywords}개, 최소길이 {min_word_length}글자")
        
        # 설정 변경 안내
        if st.session_state.get('min_word_length', config.MIN_WORD_LENGTH) != config.MIN_WORD_LENGTH:
            st.warning("⚠️ 설정이 변경되었습니다. 새로운 설정을 적용하려면 캐시를 클리어하고 데이터를 다시 수집하세요.")
        
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
    
    # 데이터 수집 (진행 상황 시각화 포함)
    if st.session_state.get('collect_data', False):
        # 진행 상황 시각화
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 🚀 데이터 수집 진행 상황")
            
            # 진행 단계 정의
            step_names = [
                "API 연결 확인", 
                "데이터 요청", 
                "응답 처리", 
                "데이터 정제", 
                "분석 준비"
            ]
            
            # 진행 상황 바 생성
            progress_chart_placeholder = st.empty()
            status_placeholder = st.empty()
            
            # 단계별 진행
            for step in range(len(step_names)):
                progress_chart = st.session_state.visualizer.create_progress_visualization(
                    step, 
                    len(step_names), 
                    step_names
                )
                
                if progress_chart:
                    progress_chart_placeholder.plotly_chart(progress_chart, use_container_width=True)
                
                status_placeholder.info(f"🔄 {step_names[step]} 중...")
                
                # 실제 작업 수행
                if step == 0:  # API 연결 확인
                    time.sleep(0.5)
                elif step == 1:  # 데이터 요청
                    time.sleep(1.0)
                elif step == 2:  # 응답 처리
                    df = collect_youtube_data()
                    time.sleep(0.5)
                elif step == 3:  # 데이터 정제
                    time.sleep(0.8)
                elif step == 4:  # 분석 준비
                    time.sleep(0.3)
            
            # 완료 상태 표시
            final_progress_chart = st.session_state.visualizer.create_progress_visualization(
                len(step_names), 
                len(step_names), 
                step_names
            )
            
            if final_progress_chart:
                progress_chart_placeholder.plotly_chart(final_progress_chart, use_container_width=True)
            
            if df is not None and not df.empty:
                st.session_state.df = df
                st.session_state.collect_data = False
                
                # 성공 메시지와 풍선 효과
                status_placeholder.success(f"✅ {len(df)}개의 동영상 데이터를 성공적으로 수집했습니다!")
                st.balloons()  # 축하 풍선 효과
                
                # 잠시 후 진행 상황 바 숨기기
                time.sleep(2)
                progress_container.empty()
                
            else:
                status_placeholder.error("❌ 데이터 수집에 실패했습니다.")
                st.stop()
    
    # 데이터가 있는 경우에만 분석 표시
    if 'df' in st.session_state:
        df = st.session_state.df
        
        # 탭 선택 (라디오 버튼으로 변경)
        tab_options = [
            "📊 대시보드", 
            "👥 채널 분석",
            "🔗 네트워크 분석",
            "☁️ 워드클라우드", 
            "🎬 동영상 목록"
        ]
        
        selected_tab = st.radio(
            "탭 선택",
            tab_options,
            index=tab_options.index(st.session_state.selected_tab) if st.session_state.selected_tab in tab_options else 0,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # 선택된 탭 상태 저장
        st.session_state.selected_tab = selected_tab
        
        # 선택된 탭에 따라 해당 함수 실행
        if selected_tab == "📊 대시보드":
            dashboard_tab(df)
        elif selected_tab == "👥 채널 분석":
            channel_analysis_tab(df)
        elif selected_tab == "🔗 네트워크 분석":
            network_analysis_tab(df)
        elif selected_tab == "☁️ 워드클라우드":
            wordcloud_tab(df)
        elif selected_tab == "🎬 동영상 목록":
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
        
        elif analysis_mode == "카테고리별 분석":
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
    """대시보드 탭 (인터랙티브 필터링 지원)"""
    st.header("📊 트렌드 대시보드")
    
    # 주요 지표
    st.session_state.visualizer.create_metric_cards(df)
    
    st.divider()
    
    # 키워드 분석 및 필터링 시스템
    with st.spinner("키워드를 분석하고 있습니다..."):
        keywords = st.session_state.text_processor.extract_keywords_from_dataframe(
            df, 
            min_length=st.session_state.get('min_word_length', config.MIN_WORD_LENGTH)
        )
        
        if keywords:
            keyword_freq = st.session_state.text_processor.get_keyword_frequency(
                keywords, 
                max_keywords=st.session_state.max_keywords
            )
            
            # 키워드 통계 정보 표시
            st.success(f"🔍 **{len(keywords)}개의 키워드**를 추출했습니다 (상위 {len(keyword_freq)}개 표시)")
            
            # ===== 새로운 인터랙티브 필터링 시스템 =====
            st.subheader("🎛️ 인터랙티브 필터링")
            
            # 필터링 옵션들
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                # 키워드 선택 필터
                available_keywords = list(keyword_freq.keys())[:20]  # 상위 20개 키워드
                selected_keywords = st.multiselect(
                    "🔍 키워드 필터",
                    available_keywords,
                    default=[],
                    help="특정 키워드를 선택하면 해당 키워드가 포함된 동영상만 표시합니다",
                    placeholder="키워드를 선택하세요..."
                )
            
            with col2:
                # 카테고리 필터
                available_categories = df['category_id'].unique()
                category_names = [config.CATEGORY_MAPPING.get(cat_id, f"카테고리 {cat_id}") for cat_id in available_categories]
                selected_categories = st.multiselect(
                    "📂 카테고리 필터",
                    category_names,
                    default=[],
                    help="특정 카테고리를 선택하여 필터링합니다",
                    placeholder="카테고리를 선택하세요..."
                )
            
            with col3:
                # 필터 초기화 버튼
                if st.button("🔄 필터 초기화", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()
            
            # 조회수 범위 슬라이더
            min_views, max_views = int(df['view_count'].min()), int(df['view_count'].max())
            views_range = st.slider(
                "📈 조회수 범위",
                min_value=min_views,
                max_value=max_views,
                value=(min_views, max_views),
                format="%d",
                help="조회수 범위를 설정하여 동영상을 필터링합니다"
            )
            
            # 필터링 적용
            filtered_df = apply_filters(df, selected_keywords, selected_categories, views_range)
            
            # 필터링 결과 표시
            if len(filtered_df) != len(df):
                st.info(f"🎯 **{len(filtered_df)}개의 동영상**이 필터 조건에 맞습니다 (전체 {len(df)}개 중)")
                
                # 필터링된 데이터로 키워드 재분석
                if len(filtered_df) > 0:
                    filtered_keywords = st.session_state.text_processor.extract_keywords_from_dataframe(
                        filtered_df, 
                        min_length=st.session_state.get('min_word_length', config.MIN_WORD_LENGTH)
                    )
                    filtered_keyword_freq = st.session_state.text_processor.get_keyword_frequency(
                        filtered_keywords, 
                        max_keywords=st.session_state.max_keywords
                    )
                else:
                    filtered_keyword_freq = {}
            else:
                filtered_keyword_freq = keyword_freq
            
            st.divider()
            
            # 차트 표시 (필터링된 데이터 사용)
            display_data = filtered_df if len(filtered_df) > 0 else df
            display_keywords = filtered_keyword_freq if filtered_keyword_freq else keyword_freq
            
            # 상위 키워드 차트 (인터랙티브)
            col1, col2 = st.columns(2)
            
            with col1:
                with st.container():
                    st.markdown("### 🏆 상위 키워드")
                    
                    # 정적 차트만 사용
                    bar_chart = st.session_state.visualizer.create_keyword_bar_chart(
                        display_keywords, 
                        "상위 키워드",
                        max_keywords=15
                    )
                    if bar_chart:
                        st.plotly_chart(bar_chart, use_container_width=True, config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToAdd': ['zoom2d', 'pan2d'],
                            'modeBarButtonsToRemove': ['autoScale2d']
                        })
                    else:
                        st.info("표시할 키워드가 없습니다.")
            
            with col2:
                with st.container():
                    st.markdown("### 📊 키워드 분포")
                    pie_chart = st.session_state.visualizer.create_keyword_pie_chart(
                        display_keywords,
                        "키워드 분포 (호버로 세부 정보)",
                        max_keywords=10
                    )
                    if pie_chart:
                        # 인터랙티브 옵션 추가
                        pie_chart.update_layout(
                            clickmode='event+select'
                        )
                        st.plotly_chart(pie_chart, use_container_width=True, config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'autoScale2d']
                        })
            
            # 추가 분석 차트들
            st.subheader("📈 상세 분석")
            
            # 카테고리 분석만 표시
            with st.container():
                st.markdown("### 📂 카테고리 분석")
                category_chart = st.session_state.visualizer.create_category_analysis(display_data)
                if category_chart:
                    st.plotly_chart(category_chart, use_container_width=True, config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToAdd': ['zoom2d', 'pan2d']
                    })
        
        else:
            st.warning("키워드를 추출할 수 없습니다. 다른 설정을 시도해보세요.")

def apply_filters(df, selected_keywords, selected_categories, views_range):
    """필터링 조건을 적용하여 DataFrame 반환"""
    filtered_df = df.copy()
    
    # 조회수 범위 필터
    filtered_df = filtered_df[
        (filtered_df['view_count'] >= views_range[0]) & 
        (filtered_df['view_count'] <= views_range[1])
    ]
    
    # 키워드 필터
    if selected_keywords:
        keyword_mask = pd.Series([False] * len(filtered_df))
        for keyword in selected_keywords:
            # 제목, 설명, 태그에서 키워드 검색
            title_mask = filtered_df['title'].str.contains(keyword, case=False, na=False)
            desc_mask = filtered_df['description'].str.contains(keyword, case=False, na=False) if 'description' in filtered_df.columns else pd.Series([False] * len(filtered_df))
            tags_mask = filtered_df['tags'].str.contains(keyword, case=False, na=False) if 'tags' in filtered_df.columns else pd.Series([False] * len(filtered_df))
            
            keyword_mask = keyword_mask | title_mask | desc_mask | tags_mask
        
        filtered_df = filtered_df[keyword_mask]
    
    # 카테고리 필터
    if selected_categories:
        # 카테고리 이름을 ID로 변환
        category_ids = []
        for cat_name in selected_categories:
            for cat_id, name in config.CATEGORY_MAPPING.items():
                if name == cat_name:
                    category_ids.append(cat_id)
                    break
        
        if category_ids:
            filtered_df = filtered_df[filtered_df['category_id'].isin(category_ids)]
    
    return filtered_df

def wordcloud_tab(df):
    """워드클라우드 탭"""
    st.header("☁️ 워드클라우드")
    
    with st.spinner("워드클라우드를 생성하고 있습니다..."):
        keywords = st.session_state.text_processor.extract_keywords_from_dataframe(
            df,
            min_length=st.session_state.get('min_word_length', config.MIN_WORD_LENGTH)
        )
        
        if keywords:
            keyword_freq = st.session_state.text_processor.get_keyword_frequency(keywords)
            
            # 워드클라우드 생성
            wordcloud = st.session_state.text_processor.generate_wordcloud(keyword_freq)
            
            if wordcloud:
                # 워드클라우드 표시
                fig = st.session_state.visualizer.create_wordcloud_plot(wordcloud)
                if fig:
                    st.pyplot(fig)
            
            else:
                st.error("워드클라우드 생성에 실패했습니다.")
        
        else:
            st.warning("워드클라우드를 생성할 키워드가 없습니다.")


def video_list_tab(df):
    """동영상 목록 탭"""
    st.header("🎬 동영상 목록")
    
    # 현재 데이터 상태 표시
    st.info(f"📊 총 **{len(df)}개**의 동영상이 수집되었습니다")
    
    # 정렬 옵션
    sort_options = {
        '조회수 (높은 순)': ('view_count', False),
        '조회수 (낮은 순)': ('view_count', True),
        '좋아요 (높은 순)': ('like_count', False),
        '좋아요 (낮은 순)': ('like_count', True),
        '댓글수 (높은 순)': ('comment_count', False),
        '댓글수 (낮은 순)': ('comment_count', True),
        '게시일 (최신 순)': ('published_at', False),
        '게시일 (과거 순)': ('published_at', True)
    }
    
    # 정렬 설정
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        sort_option = st.selectbox(
            "📊 정렬 기준", 
            list(sort_options.keys()),
            help="동영상을 어떤 기준으로 정렬할지 선택하세요"
        )
    
    with col2:
        videos_per_page = st.selectbox(
            "페이지당 표시",
            [10, 20, 30, 50],
            index=2,  # 기본값 30
            help="한 페이지에 표시할 동영상 수"
        )
    
    with col3:
        layout_style = st.selectbox(
            "레이아웃",
            ["카드형", "목록형"],
            help="표시 스타일 선택"
        )
    
    # 데이터 정렬
    sort_column, ascending = sort_options[sort_option]
    sorted_df = df.sort_values(sort_column, ascending=ascending)
    
    st.success(f"✅ **{sort_option}**으로 정렬되었습니다")
    
    # 페이지네이션 설정
    total_videos = len(sorted_df)
    total_pages = (total_videos + videos_per_page - 1) // videos_per_page
    
    if total_pages > 1:
        page = st.selectbox(
            f"📄 페이지 선택 (총 {total_pages}페이지)", 
            range(1, total_pages + 1),
            help=f"총 {total_videos}개 동영상을 {videos_per_page}개씩 표시합니다"
        )
    else:
        page = 1
    
    # 현재 페이지 데이터
    start_idx = (page - 1) * videos_per_page
    end_idx = min(start_idx + videos_per_page, total_videos)
    current_page_df = sorted_df.iloc[start_idx:end_idx]
    
    st.write(f"**{start_idx + 1}-{end_idx}번째** 동영상 (총 {total_videos}개 중)")
    
    # 동영상 표시
    if layout_style == "카드형":
        # 3열 카드 레이아웃으로 개선
        display_video_cards_improved(current_page_df, start_idx)
    else:
        # 목록형 표시
        display_video_list(current_page_df, start_idx)
    
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

def display_video_cards_improved(df, start_idx=0):
    """개선된 동영상 카드 표시 (3열 레이아웃, 순서 번호 포함)"""
    try:
        # 3열 레이아웃으로 변경
        cols = st.columns(3)
        
        for idx, (_, video) in enumerate(df.iterrows()):
            col = cols[idx % 3]
            
            # 전체 순서 번호 계산
            rank_number = start_idx + idx + 1
            
            with col:
                # 카드 스타일 컨테이너 (순서 번호와 함께)
                with st.container():
                    # 순위 배지와 제목
                    title = video['title']
                    if len(title) > 50:
                        display_title = title[:50] + "..."
                    else:
                        display_title = title
                    
                    # 순위에 따른 색상 배지
                    if rank_number <= 3:
                        rank_emoji = "🥇" if rank_number == 1 else "🥈" if rank_number == 2 else "🥉"
                        st.markdown(f"### {rank_emoji} **{rank_number}위**")
                    else:
                        st.markdown(f"### 🏆 **{rank_number}위**")
                    
                    st.markdown(f"**📺 {display_title}**")
                    
                    # 채널 정보
                    st.markdown(f"**📻 채널:** {video['channel_title']}")
                    
                    # 통계 정보를 더 보기 좋게
                    col_sub1, col_sub2 = st.columns(2)
                    with col_sub1:
                        # 숫자를 K, M 단위로 표시
                        view_formatted = format_number(video['view_count'])
                        like_formatted = format_number(video['like_count'])
                        st.metric("👀 조회수", view_formatted)
                        st.metric("👍 좋아요", like_formatted)
                    with col_sub2:
                        comment_formatted = format_number(video['comment_count'])
                        st.metric("💬 댓글", comment_formatted)
                        
                        # 게시일 표시
                        try:
                            from datetime import datetime
                            pub_date = pd.to_datetime(video['published_at']).strftime('%m/%d')
                            st.caption(f"📅 {pub_date}")
                        except:
                            st.caption("📅 날짜 정보 없음")
                    
                    # 태그 정보 (간단히)
                    if 'tags' in video and video['tags']:
                        tags = str(video['tags'])
                        if tags and tags != 'nan':
                            # 첫 3개 태그만 표시
                            tag_list = tags.split(', ')[:3]
                            if tag_list:
                                st.caption(f"🏷️ {', '.join(tag_list)}")
                    
                    # 유튜브 링크 (더 눈에 띄게)
                    video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
                    st.link_button("🎬 동영상 보기", video_url, use_container_width=True, type="primary")
                    
                    st.divider()
                        
    except Exception as e:
        st.error(f"동영상 카드 표시 실패: {e}")

def display_video_list(df, start_idx=0):
    """목록형 동영상 표시 (순서 번호 포함)"""
    try:
        for idx, (_, video) in enumerate(df.iterrows()):
            # 전체 순서 번호 계산
            rank_number = start_idx + idx + 1
            
            # 순위에 따른 이모지
            if rank_number <= 3:
                rank_emoji = "🥇" if rank_number == 1 else "🥈" if rank_number == 2 else "🥉"
            else:
                rank_emoji = "🏆"
            
            # 제목 길이 조정
            title_display = video['title'][:70] + "..." if len(video['title']) > 70 else video['title']
            
            # 확장 가능한 컨테이너 (순서 번호 강조)
            with st.expander(f"{rank_emoji} **{rank_number}위** • {title_display}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # 기본 정보
                    st.write(f"**📻 채널:** {video['channel_title']}")
                    
                    # 태그 정보 표시 (있는 경우)
                    if 'tags' in video and video['tags']:
                        tags = str(video['tags'])
                        if tags and tags != 'nan':
                            tag_list = tags.split(', ')[:5]  # 최대 5개
                            if tag_list:
                                st.caption(f"🏷️ **태그:** {', '.join(tag_list)}")
                    
                    # 설명 정보 (일부)
                    if 'description' in video and video['description']:
                        desc = str(video['description'])
                        if desc and desc != 'nan':
                            if len(desc) > 120:
                                desc = desc[:120] + "..."
                            st.caption(f"📝 **설명:** {desc}")
                    
                    # 게시일 정보
                    try:
                        from datetime import datetime
                        pub_date = pd.to_datetime(video['published_at']).strftime('%Y-%m-%d %H:%M')
                        st.caption(f"📅 **게시일:** {pub_date}")
                    except:
                        st.caption("📅 게시일 정보 없음")
                
                with col2:
                    # 통계 정보 (포맷된 숫자)
                    view_formatted = format_number(video['view_count'])
                    like_formatted = format_number(video['like_count'])
                    comment_formatted = format_number(video['comment_count'])
                    
                    st.metric("👀 조회수", view_formatted)
                    st.metric("👍 좋아요", like_formatted)
                    st.metric("💬 댓글", comment_formatted)
                    
                    # 유튜브 링크
                    video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
                    st.link_button("🎬 보기", video_url, use_container_width=True, type="primary")
                        
    except Exception as e:
        st.error(f"동영상 목록 표시 실패: {e}")

def format_number(num):
    """숫자를 K, M 단위로 포맷팅"""
    try:
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return f"{num:,}"
    except:
        return str(num)

def channel_analysis_tab(df):
    """채널 분석 탭 - 채널별 심화 분석"""
    st.header("👥 채널 분석 대시보드")
    st.markdown("**채널별 성과를 분석하고 성공 요인을 발견하세요!**")
    
    try:
        # 데이터 정제 및 타입 변환
        df_clean = df.copy()
        
        # 수치 컬럼들을 확실히 변환
        numeric_columns = ['view_count', 'like_count', 'comment_count']
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # 결측값을 0으로 처리
        df_clean[numeric_columns] = df_clean[numeric_columns].fillna(0)
        
        # 채널명이 없는 데이터 제거
        df_clean = df_clean.dropna(subset=['channel_title'])
        df_clean = df_clean[df_clean['channel_title'].str.strip() != '']
        
        if df_clean.empty:
            st.warning("⚠️ 분석할 수 있는 채널 데이터가 없습니다.")
            return
        
        # 채널별 기본 통계 계산
        channel_stats = df_clean.groupby('channel_title').agg({
            'view_count': ['count', 'sum', 'mean'],
            'like_count': 'sum',
            'comment_count': 'sum',
            'published_at': ['min', 'max']
        }).round(0)
        
        # 컬럼명 정리
        channel_stats.columns = ['동영상_수', '총_조회수', '평균_조회수', '총_좋아요', '총_댓글', '첫_업로드', '최근_업로드']
        channel_stats = channel_stats.reset_index()
        
        # 모든 수치 컬럼을 정수형으로 변환
        for col in ['동영상_수', '총_조회수', '평균_조회수', '총_좋아요', '총_댓글']:
            channel_stats[col] = pd.to_numeric(channel_stats[col], errors='coerce').fillna(0).astype(int)
        
        # 상위 채널 선별 (동영상 수 기준)
        top_channels = channel_stats.nlargest(20, '동영상_수')
        
        # 주요 지표 카드
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_channels = len(channel_stats)
            st.metric(
                "📺 총 채널 수", 
                f"{total_channels:,}",
                help="트렌드에 등장한 전체 채널 수"
            )
        
        with col2:
            avg_videos_per_channel = channel_stats['동영상_수'].mean()
            st.metric(
                "📹 채널당 평균 동영상", 
                f"{avg_videos_per_channel:.1f}개",
                help="채널당 평균 트렌드 동영상 수"
            )
        
        with col3:
            top_channel = channel_stats.loc[channel_stats['총_조회수'].idxmax()]
            st.metric(
                "👑 최고 조회수 채널", 
                top_channel['channel_title'],
                f"{top_channel['총_조회수']:,.0f} views",
                help="가장 많은 총 조회수를 기록한 채널"
            )
        
        with col4:
            most_active = channel_stats.loc[channel_stats['동영상_수'].idxmax()]
            st.metric(
                "🔥 최다 트렌드 채널", 
                most_active['channel_title'],
                f"{most_active['동영상_수']:,.0f}개",
                help="가장 많은 트렌드 동영상을 보유한 채널"
            )
        
        st.divider()
        
        # 채널 선택 및 필터링
        st.subheader("🎯 채널 필터링 및 분석")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 채널 선택 (다중 선택 가능)
            selected_channels = st.multiselect(
                "📺 분석할 채널 선택",
                options=top_channels['channel_title'].tolist(),
                default=top_channels.head(5)['channel_title'].tolist(),
                help="비교 분석할 채널들을 선택하세요 (최대 10개 권장)"
            )
        
        with col2:
            # 정렬 기준
            sort_by = st.selectbox(
                "📊 정렬 기준",
                ["총_조회수", "평균_조회수", "동영상_수", "총_좋아요"],
                help="채널 순위 정렬 기준"
            )
        
        if selected_channels:
            # 선택된 채널 데이터 필터링
            filtered_channel_stats = channel_stats[
                channel_stats['channel_title'].isin(selected_channels)
            ].sort_values(sort_by, ascending=False)
            
            # 채널 비교 차트
            st.subheader("📈 채널 성과 비교")
            
            # 채널별 조회수 비교 (막대 차트)
            channel_view_chart = st.session_state.visualizer.create_channel_comparison_chart(
                filtered_channel_stats, 
                metric='총_조회수',
                title="채널별 총 조회수 비교"
            )
            if channel_view_chart:
                st.plotly_chart(channel_view_chart, use_container_width=True)
            
            # 채널별 상세 분석
            st.subheader("🔍 채널별 상세 분석")
            
            # 선택된 채널의 동영상 데이터 (정제된 데이터 사용)
            channel_videos = df_clean[df_clean['channel_title'].isin(selected_channels)]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 채널별 카테고리 분포
                category_dist_chart = st.session_state.visualizer.create_channel_category_distribution(
                    channel_videos,
                    title="채널별 카테고리 분포"
                )
                if category_dist_chart:
                    st.plotly_chart(category_dist_chart, use_container_width=True)
            
            with col2:
                # 간단한 요약 통계
                st.markdown("### 📊 선택된 채널 요약")
                
                total_videos = filtered_channel_stats['동영상_수'].sum()
                total_views = filtered_channel_stats['총_조회수'].sum()
                avg_channel_views = filtered_channel_stats['평균_조회수'].mean()
                
                st.metric("총 동영상 수", f"{total_videos:,.0f}개")
                st.metric("총 조회수", f"{total_views:,.0f}")
                st.metric("채널 평균 조회수", f"{avg_channel_views:,.0f}")
            
            # 채널 상세 테이블
            st.subheader("📋 채널 상세 정보")
            
            # 테이블 표시용 데이터 준비
            display_stats = filtered_channel_stats.copy()
            display_stats['총_조회수'] = display_stats['총_조회수'].apply(lambda x: f"{x:,.0f}")
            display_stats['평균_조회수'] = display_stats['평균_조회수'].apply(lambda x: f"{x:,.0f}")
            display_stats['총_좋아요'] = display_stats['총_좋아요'].apply(lambda x: f"{x:,.0f}")
            display_stats['총_댓글'] = display_stats['총_댓글'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(
                display_stats[['channel_title', '동영상_수', '총_조회수', '평균_조회수', '총_좋아요', '총_댓글']],
                column_config={
                    'channel_title': st.column_config.TextColumn('채널명'),
                    '동영상_수': st.column_config.NumberColumn('동영상 수'),
                    '총_조회수': st.column_config.TextColumn('총 조회수'),
                    '평균_조회수': st.column_config.TextColumn('평균 조회수'),
                    '총_좋아요': st.column_config.TextColumn('총 좋아요'),
                    '총_댓글': st.column_config.TextColumn('총 댓글')
                },
                use_container_width=True,
                hide_index=True
            )
        
        else:
            st.info("🎯 분석할 채널을 선택해주세요!")
            
    except Exception as e:
        st.error(f"채널 분석 중 오류가 발생했습니다: {str(e)}")
        st.error(f"채널 분석 중 오류가 발생했습니다: {str(e)}")

def network_analysis_tab(df):
    """네트워크 분석 탭 - 키워드 연관성과 클러스터 분석"""
    st.header("🔗 키워드 네트워크 분석")
    st.markdown("**키워드 간의 연관성을 네트워크 그래프로 시각화하고 클러스터를 분석합니다!**")
    
    try:
        # 분석 설정
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_keywords = st.slider(
                "🔢 최대 키워드 수",
                min_value=10,
                max_value=50,
                value=25,
                help="네트워크에 표시할 최대 키워드 수"
            )
        
        with col2:
            min_cooccurrence = st.slider(
                "🔗 최소 공출현 횟수",
                min_value=1,
                max_value=5,
                value=2,
                help="두 키워드가 연결되기 위한 최소 공출현 횟수"
            )
        
        with col3:
            similarity_threshold = st.slider(
                "📊 유사도 임계값",
                min_value=0.1,
                max_value=0.8,
                value=0.3,
                step=0.1,
                help="클러스터링을 위한 키워드 유사도 임계값"
            )
        
        st.divider()
        
        # 네트워크 분석 실행
        with st.spinner("키워드 네트워크를 분석하고 있습니다..."):
            # 키워드 네트워크 생성
            network_data, keyword_freq = st.session_state.text_processor.create_keyword_network(
                df, 
                max_keywords=max_keywords, 
                min_cooccurrence=min_cooccurrence
            )
            
            # 키워드 클러스터 분석
            clusters = st.session_state.text_processor.get_keyword_clusters(
                df, 
                max_keywords=max_keywords, 
                similarity_threshold=similarity_threshold
            )
        
        if network_data and keyword_freq:
            # 분석 결과 요약
            st.success(f"🎯 **{len(network_data['nodes'])}개의 키워드**와 **{len(network_data['edges'])}개의 연관관계**를 발견했습니다!")
            
            if clusters:
                st.info(f"🔍 **{len(clusters)}개의 키워드 클러스터**를 식별했습니다!")
            
            # 메트릭 카드
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_keywords = len(keyword_freq)
                st.metric(
                    "🔤 총 키워드 수", 
                    total_keywords,
                    help="네트워크에 포함된 전체 키워드 수"
                )
            
            with col2:
                total_connections = len(network_data['edges'])
                st.metric(
                    "🔗 연결 관계 수", 
                    total_connections,
                    help="키워드 간 공출현으로 생성된 연결 수"
                )
            
            with col3:
                avg_connections = total_connections / total_keywords if total_keywords > 0 else 0
                st.metric(
                    "📊 평균 연결도", 
                    f"{avg_connections:.1f}",
                    help="키워드당 평균 연결 관계 수"
                )
            
            with col4:
                cluster_count = len(clusters) if clusters else 0
                st.metric(
                    "🎯 클러스터 수", 
                    cluster_count,
                    help="발견된 키워드 클러스터 수"
                )
            
            st.divider()
            
            # 네트워크 그래프와 클러스터 분석
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("🕸️ 키워드 연관성 네트워크")
                
                # 네트워크 그래프 생성
                network_chart = st.session_state.visualizer.create_keyword_network_graph(
                    network_data,
                    title="키워드 연관성 네트워크"
                )
                
                if network_chart:
                    st.plotly_chart(network_chart, use_container_width=True, config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToAdd': ['zoom2d', 'pan2d', 'select2d', 'lasso2d'],
                        'modeBarButtonsToRemove': ['autoScale2d']
                    })
                    
                    # 네트워크 분석 인사이트
                    st.markdown("""
                    **📋 네트워크 분석 해석:**
                    - **노드 크기**: 키워드 빈도수 (클수록 더 자주 언급)
                    - **연결선 두께**: 공출현 횟수 (두꺼울수록 더 자주 함께 등장)
                    - **노드 색상**: 키워드 빈도 (진할수록 높은 빈도)
                    - **위치**: 연관성이 높은 키워드들이 가까이 배치됨
                    """)
                else:
                    st.warning("⚠️ 네트워크 그래프를 생성할 수 없습니다. 설정을 조정해보세요.")
            
            with col2:
                st.subheader("🎯 키워드 클러스터")
                
                if clusters:
                    # 클러스터 차트 생성
                    cluster_chart = st.session_state.visualizer.create_keyword_cluster_chart(
                        clusters,
                        title="키워드 클러스터 분석"
                    )
                    
                    if cluster_chart:
                        st.plotly_chart(cluster_chart, use_container_width=True)
                    
                    # 클러스터 상세 정보
                    st.markdown("### 📊 클러스터 상세 정보")
                    
                    for i, cluster in enumerate(clusters[:5]):  # 상위 5개 클러스터만
                        with st.expander(f"🎯 클러스터 {i+1} ({cluster['size']}개 키워드)"):
                            st.markdown(f"**평균 빈도**: {cluster['avg_freq']:.1f}")
                            st.markdown(f"**키워드 목록**: {', '.join(cluster['keywords'])}")
                else:
                    st.info("🔍 현재 설정으로는 의미있는 클러스터를 찾을 수 없습니다.")
                    st.markdown("""
                    **💡 클러스터 생성 팁:**
                    - 유사도 임계값을 낮춰보세요 (0.1-0.3)
                    - 최대 키워드 수를 늘려보세요
                    - 최소 공출현 횟수를 줄여보세요
                    """)
            
            # 상세 분석 결과
            st.divider()
            st.subheader("📈 상세 분석 결과")
            
            # 탭으로 구성
            detail_tab1, detail_tab2, detail_tab3 = st.tabs([
                "🔗 강한 연관관계", 
                "🏆 중심 키워드", 
                "📊 연결도 분석"
            ])
            
            with detail_tab1:
                st.markdown("### 🔗 가장 강한 연관관계 TOP 10")
                
                # 엣지를 가중치 순으로 정렬
                sorted_edges = sorted(network_data['edges'], key=lambda x: x['weight'], reverse=True)
                
                edge_data = []
                for edge in sorted_edges[:10]:
                    edge_data.append({
                        '키워드 1': edge['source'],
                        '키워드 2': edge['target'],
                        '공출현 횟수': edge['weight'],
                        '연관 강도': f"{'🔥' * min(edge['weight'], 5)}"
                    })
                
                if edge_data:
                    st.dataframe(
                        edge_data,
                        column_config={
                            '공출현 횟수': st.column_config.NumberColumn('공출현 횟수'),
                            '연관 강도': st.column_config.TextColumn('연관 강도')
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("연관관계 데이터가 없습니다.")
            
            with detail_tab2:
                st.markdown("### 🏆 중심 키워드 (연결도 높은 순)")
                
                # 각 키워드의 연결 수 계산
                keyword_connections = {}
                for edge in network_data['edges']:
                    keyword_connections[edge['source']] = keyword_connections.get(edge['source'], 0) + 1
                    keyword_connections[edge['target']] = keyword_connections.get(edge['target'], 0) + 1
                
                # 연결도 순으로 정렬
                sorted_keywords = sorted(keyword_connections.items(), key=lambda x: x[1], reverse=True)
                
                central_data = []
                for keyword, connections in sorted_keywords[:10]:
                    freq = keyword_freq.get(keyword, 0)
                    central_data.append({
                        '키워드': keyword,
                        '연결 수': connections,
                        '빈도': freq,
                        '중심성': f"{'⭐' * min(connections, 5)}"
                    })
                
                if central_data:
                    st.dataframe(
                        central_data,
                        column_config={
                            '연결 수': st.column_config.NumberColumn('연결 수'),
                            '빈도': st.column_config.NumberColumn('빈도'),
                            '중심성': st.column_config.TextColumn('중심성')
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("중심성 데이터가 없습니다.")
            
            with detail_tab3:
                st.markdown("### 📊 연결도 분포 분석")
                
                if keyword_connections:
                    # 연결도 분포 히스토그램
                    connection_counts = list(keyword_connections.values())
                    
                    import plotly.graph_objects as go
                    
                    fig = go.Figure(data=[
                        go.Histogram(
                            x=connection_counts,
                            nbinsx=min(20, len(set(connection_counts))),
                            marker_color='lightblue',
                            opacity=0.7
                        )
                    ])
                    
                    fig.update_layout(
                        title="키워드 연결도 분포",
                        xaxis_title="연결 수",
                        yaxis_title="키워드 수",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 연결도 통계
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_connections = sum(connection_counts) / len(connection_counts)
                        st.metric("평균 연결 수", f"{avg_connections:.1f}")
                    
                    with col2:
                        max_connections = max(connection_counts)
                        st.metric("최대 연결 수", max_connections)
                    
                    with col3:
                        isolated_keywords = sum(1 for freq in keyword_freq.values() if keyword_freq and freq not in keyword_connections)
                        st.metric("고립된 키워드", isolated_keywords)
                
        else:
            st.warning("⚠️ 키워드 네트워크를 생성할 수 없습니다. 다음을 확인해보세요:")
            st.markdown("""
            - 최소 공출현 횟수를 줄여보세요 (1-2)
            - 최대 키워드 수를 늘려보세요 (30-50)
            - 데이터에 충분한 텍스트가 있는지 확인해보세요
            """)
            
    except Exception as e:
        st.error(f"네트워크 분석 중 오류가 발생했습니다: {str(e)}")
        st.error(f"네트워크 분석 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 