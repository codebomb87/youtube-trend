import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
from wordcloud import WordCloud
from typing import Optional, Any
import config

class Visualizer:
    """데이터 시각화 클래스"""
    
    def __init__(self):
        self.setup_style()
    
    def setup_style(self):
        """시각화 스타일 설정"""
        # Matplotlib 한국어 폰트 설정
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        # Seaborn 스타일 설정
        sns.set_style("whitegrid")
        sns.set_palette("husl")
    
    def create_keyword_bar_chart(self, keyword_df, title="상위 키워드", max_keywords=20):
        """키워드 빈도 막대 차트"""
        try:
            # 상위 키워드 선택
            top_keywords = keyword_df.head(max_keywords)
            
            # Plotly 막대 차트 생성
            fig = px.bar(
                top_keywords,
                x='frequency',
                y='keyword',
                orientation='h',
                title=title,
                labels={'frequency': '빈도', 'keyword': '키워드'},
                color='frequency',
                color_continuous_scale='viridis'
            )
            
            # 레이아웃 설정
            fig.update_layout(
                height=max(400, len(top_keywords) * 25),
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'}
            )
            
            return fig
            
        except Exception as e:
            st.error(f"막대 차트 생성 실패: {e}")
            return None
    
    def create_keyword_pie_chart(self, keyword_df, title="키워드 분포", max_keywords=10):
        """키워드 빈도 파이 차트"""
        try:
            # 상위 키워드 선택
            top_keywords = keyword_df.head(max_keywords)
            
            # 기타 키워드 그룹화
            if len(keyword_df) > max_keywords:
                others_count = keyword_df.iloc[max_keywords:]['frequency'].sum()
                others_row = pd.DataFrame([{'keyword': '기타', 'frequency': others_count}])
                top_keywords = pd.concat([top_keywords, others_row], ignore_index=True)
            
            # Plotly 파이 차트 생성
            fig = px.pie(
                top_keywords,
                values='frequency',
                names='keyword',
                title=title,
                hole=0.4  # 도넛 차트 스타일
            )
            
            # 레이아웃 설정
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label'
            )
            
            return fig
            
        except Exception as e:
            st.error(f"파이 차트 생성 실패: {e}")
            return None
    
    def create_wordcloud_plot(self, wordcloud: WordCloud) -> Optional[Figure]:
        """워드클라우드 Matplotlib 플롯"""
        try:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud.to_array(), interpolation='bilinear')
            ax.axis('off')
            return fig
            
        except Exception as e:
            st.error(f"워드클라우드 플롯 생성 실패: {e}")
            return None
    
    def create_category_analysis(self, df):
        """카테고리별 분석 차트"""
        try:
            # 카테고리별 동영상 수 계산
            category_counts = df['category_id'].value_counts().head(10)
            
            # 카테고리 이름 매핑
            category_names = [
                config.CATEGORY_MAPPING.get(cat_id, f"카테고리 {cat_id}")
                for cat_id in category_counts.index
            ]
            
            # 막대 차트 생성
            fig = go.Figure(data=[
                go.Bar(
                    x=category_counts.values,
                    y=category_names,
                    orientation='h',
                    marker_color='skyblue'
                )
            ])
            
            fig.update_layout(
                title="카테고리별 인기 동영상 수",
                xaxis_title="동영상 수",
                yaxis_title="카테고리",
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"카테고리 분석 차트 생성 실패: {e}")
            return None
    
    def create_view_count_distribution(self, df):
        """조회수 분포 히스토그램"""
        try:
            fig = px.histogram(
                df,
                x='view_count',
                nbins=20,
                title="조회수 분포",
                labels={'view_count': '조회수', 'count': '동영상 수'}
            )
            
            # 로그 스케일 적용
            fig.update_xaxes(type="log")
            
            return fig
            
        except Exception as e:
            st.error(f"조회수 분포 차트 생성 실패: {e}")
            return None
    
    def create_engagement_scatter(self, df):
        """조회수 vs 좋아요 수 산점도"""
        try:
            fig = px.scatter(
                df,
                x='view_count',
                y='like_count',
                size='comment_count',
                color='category_id',
                hover_data=['title', 'channel_title'],
                title="조회수 vs 좋아요 수 (버블 크기: 댓글 수)",
                labels={
                    'view_count': '조회수',
                    'like_count': '좋아요 수',
                    'comment_count': '댓글 수'
                }
            )
            
            # 로그 스케일 적용
            fig.update_xaxes(type="log")
            fig.update_yaxes(type="log")
            
            return fig
            
        except Exception as e:
            st.error(f"참여도 산점도 생성 실패: {e}")
            return None
    
    def create_trend_timeline(self, df):
        """시간별 트렌드 라인 차트"""
        try:
            # 게시 날짜별 동영상 수 계산
            df['published_date'] = pd.to_datetime(df['published_at']).dt.date
            daily_counts = df.groupby('published_date').size().reset_index(name='count')
            
            fig = px.line(
                daily_counts,
                x='published_date',
                y='count',
                title="일별 인기 동영상 게시 수",
                labels={'published_date': '게시일', 'count': '동영상 수'}
            )
            
            return fig
            
        except Exception as e:
            st.error(f"트렌드 타임라인 생성 실패: {e}")
            return None
    
    def create_top_channels(self, df, max_channels=10):
        """상위 채널 분석"""
        try:
            channel_stats = df.groupby('channel_title').agg({
                'view_count': 'sum',
                'like_count': 'sum',
                'comment_count': 'sum',
                'title': 'count'
            }).rename(columns={'title': 'video_count'})
            
            # 동영상 수 기준으로 상위 채널 선택
            top_channels = channel_stats.nlargest(max_channels, 'video_count')
            
            fig = px.bar(
                top_channels.reset_index(),
                x='video_count',
                y='channel_title',
                orientation='h',
                title=f"상위 {max_channels} 채널 (동영상 수 기준)",
                labels={'video_count': '동영상 수', 'channel_title': '채널명'}
            )
            
            fig.update_layout(
                height=max(400, len(top_channels) * 30),
                yaxis={'categoryorder': 'total ascending'}
            )
            
            return fig
            
        except Exception as e:
            st.error(f"상위 채널 차트 생성 실패: {e}")
            return None
    
    def create_keyword_treemap(self, keyword_df, max_keywords=20):
        """키워드 트리맵"""
        try:
            top_keywords = keyword_df.head(max_keywords)
            
            fig = px.treemap(
                top_keywords,
                path=['keyword'],
                values='frequency',
                title="키워드 트리맵",
                color='frequency',
                color_continuous_scale='viridis'
            )
            
            return fig
            
        except Exception as e:
            st.error(f"트리맵 생성 실패: {e}")
            return None
    
    def create_correlation_heatmap(self, df):
        """상관관계 히트맵"""
        try:
            # 수치형 컬럼 선택
            numeric_columns = ['view_count', 'like_count', 'comment_count']
            correlation_matrix = df[numeric_columns].corr()
            
            fig = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                title="지표 간 상관관계",
                labels=dict(x="지표", y="지표", color="상관계수")
            )
            
            return fig
            
        except Exception as e:
            st.error(f"상관관계 히트맵 생성 실패: {e}")
            return None
    
    def display_video_cards(self, df, max_videos=6):
        """동영상 카드 형태로 표시"""
        try:
            cols = st.columns(2)
            
            for idx, (_, video) in enumerate(df.head(max_videos).iterrows()):
                col = cols[idx % 2]
                
                with col:
                    with st.container():
                        st.markdown(f"### {video['title'][:50]}...")
                        st.markdown(f"**채널:** {video['channel_title']}")
                        st.markdown(f"**조회수:** {video['view_count']:,}")
                        st.markdown(f"**좋아요:** {video['like_count']:,}")
                        st.markdown(f"**댓글:** {video['comment_count']:,}")
                        
                        # 유튜브 링크
                        video_url = f"https://www.youtube.com/watch?v={video['video_id']}"
                        st.markdown(f"[🎬 동영상 보기]({video_url})")
                        
                        st.divider()
                        
        except Exception as e:
            st.error(f"동영상 카드 표시 실패: {e}")
    
    def create_metric_cards(self, df):
        """주요 지표 카드"""
        try:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "총 동영상 수",
                    f"{len(df):,}",
                    delta=None
                )
            
            with col2:
                total_views = df['view_count'].sum()
                st.metric(
                    "총 조회수",
                    f"{total_views:,}",
                    delta=None
                )
            
            with col3:
                avg_views = df['view_count'].mean()
                st.metric(
                    "평균 조회수",
                    f"{avg_views:,.0f}",
                    delta=None
                )
            
            with col4:
                total_likes = df['like_count'].sum()
                st.metric(
                    "총 좋아요",
                    f"{total_likes:,}",
                    delta=None
                )
                
        except Exception as e:
            st.error(f"지표 카드 생성 실패: {e}") 