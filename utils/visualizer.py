import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional
from wordcloud import WordCloud

class Visualizer:
    """시각화 도구 클래스"""
    
    def __init__(self):
        """시각화 도구 초기화"""
        # 폰트 설정
        self.font_family = 'Malgun Gothic, Arial, sans-serif'
        
        # 세션 상태 확인 및 초기화
        if 'is_dark_mode' not in st.session_state:
            st.session_state.is_dark_mode = False
            
        # 기본 속성들 설정
        self.is_dark_mode = st.session_state.get('is_dark_mode', False)
        self._update_theme_properties()
        
        # Matplotlib 설정
        plt.rcParams['font.family'] = self.font_family
        plt.rcParams['axes.unicode_minus'] = False
        
    def _update_theme_properties(self):
        """테마에 따른 속성 업데이트"""
        if self.is_dark_mode:
            self.bg_color = '#1E1E1E'
            self.text_color = '#FFFFFF'
            self.grid_color = '#444444'
        else:
            self.bg_color = '#FFFFFF'
            self.text_color = '#000000'
            self.grid_color = '#CCCCCC'
    
    def _get_font_size(self, size_type):
        """폰트 크기 반환"""
        sizes = {
            'tiny': 8,
            'small': 10,
            'normal': 12,
            'large': 14,
            'title': 16
        }
        return sizes.get(size_type, 12)

    def get_current_theme(self):
        """현재 테마 상태 반환"""
        return st.session_state.get('is_dark_mode', False)

    def get_theme_colors(self):
        """테마에 맞는 색상 팔레트 반환"""
        if self.get_current_theme():
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
                'plotly_template': 'plotly_dark',
                'color_sequence': ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd', '#98d8c8', '#f7dc6f']
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
                'plotly_template': 'plotly_white',
                'color_sequence': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
            }

    def create_keyword_bar_chart(self, keyword_freq, title="키워드 빈도", max_keywords=10, interactive=True):
        """키워드 막대 차트 생성"""
        try:
            if not keyword_freq:
                return None
                
            # 상위 키워드 선택 및 빈도수 기준 내림차순 정렬
            top_keywords = dict(list(keyword_freq.items())[:max_keywords])
            
            # 빈도수 기준으로 정렬 후 차트 표시를 위해 오름차순으로 배치 (높은 값이 위에 오도록)
            sorted_items = sorted(top_keywords.items(), key=lambda x: x[1], reverse=False)  # 오름차순으로 변경
            keywords = [item[0] for item in sorted_items]
            frequencies = [item[1] for item in sorted_items]
            
            if not keywords:
                return None
            
            # 색상 그라데이션 생성 (빈도수에 따라)
            max_freq = max(frequencies)
            colors = []
            for freq in frequencies:
                # 빈도수에 따른 색상 강도 계산
                intensity = freq / max_freq
                if self.is_dark_mode:
                    # 다크 모드: 밝은 색상 사용
                    color = f'rgba(100, 200, 255, {0.6 + 0.4 * intensity})'
                else:
                    # 라이트 모드: 진한 색상 사용
                    color = f'rgba(51, 102, 204, {0.6 + 0.4 * intensity})'
                colors.append(color)
            
            # 포맷된 텍스트 생성
            formatted_frequencies = [f"{freq:,}" for freq in frequencies]
            
            # 막대 차트 생성
            fig = go.Figure(data=[
                go.Bar(
                    x=frequencies,
                    y=keywords,
                    orientation='h',
                    marker=dict(
                        color=colors,
                        line=dict(
                            color=self.text_color,
                            width=1
                        )
                    ),
                    hovertemplate="<b>%{y}</b><br>빈도: %{text}<extra></extra>",
                    text=formatted_frequencies,
                    textposition='auto',
                    textfont=dict(
                        color='white',
                        size=self._get_font_size('small'),
                        family='Arial Black'
                    )
                )
            ])
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=self._get_font_size('title')),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title="빈도수",
                    title_font=dict(size=self._get_font_size('normal')),
                    tickfont=dict(size=self._get_font_size('small')),
                    gridcolor=self.grid_color
                ),
                yaxis=dict(
                    title="키워드",
                    title_font=dict(size=self._get_font_size('normal')),
                    tickfont=dict(size=self._get_font_size('small')),
                    gridcolor=self.grid_color
                ),
                font=dict(
                    family=self.font_family,
                    size=self._get_font_size('normal')
                ),
                margin=dict(t=60, b=40, l=80, r=20),
                paper_bgcolor=self.bg_color,
                plot_bgcolor=self.bg_color,
                height=max(400, len(keywords) * 30 + 100)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"막대 차트 생성 중 오류 발생: {str(e)}")
            return None

    def create_keyword_pie_chart(self, keyword_freq, title="키워드 분포", max_keywords=8, interactive=True):
        """키워드 파이 차트 생성"""
        try:
            if not keyword_freq:
                return None
                
            # 상위 키워드 선택
            top_keywords = dict(list(keyword_freq.items())[:max_keywords])
            
            if not top_keywords:
                return None
                
            keywords = list(top_keywords.keys())
            frequencies = list(top_keywords.values())
            
            # 색상 팔레트 (다크/라이트 모드 고려)
            if self.is_dark_mode:
                colors = [
                    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                    '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
                    '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
                ]
            else:
                colors = [
                    '#FF5722', '#009688', '#2196F3', '#4CAF50',
                    '#FF9800', '#9C27B0', '#00BCD4', '#FFC107',
                    '#8BC34A', '#3F51B5', '#E91E63', '#795548'
                ]
            
            # 파이 차트 생성
            fig = go.Figure(data=[
                go.Pie(
                    labels=keywords,
                    values=frequencies,
                    hole=0.4,
                    marker=dict(
                        colors=colors[:len(keywords)],
                        line=dict(
                            color=self.text_color,
                            width=2
                        )
                    ),
                    hovertemplate="<b>%{label}</b><br>빈도: %{value}<br>비율: %{percent}<extra></extra>",
                    textinfo='label+percent',
                    textposition='auto',
                    textfont=dict(
                        color=self.text_color,
                        size=self._get_font_size('small')
                    )
                )
            ])
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=self._get_font_size('title')),
                    x=0.5,
                    xanchor='center'
                ),
                font=dict(
                    family=self.font_family,
                    size=self._get_font_size('normal')
                ),
                margin=dict(t=60, b=20, l=20, r=20),
                paper_bgcolor=self.bg_color,
                plot_bgcolor=self.bg_color,
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"파이 차트 생성 중 오류 발생: {str(e)}")
            return None

    def create_metric_cards(self, df):
        """메트릭 카드 생성"""
        try:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_videos = len(df)
                st.metric(
                    label="📹 총 동영상 수",
                    value=f"{total_videos:,}개",
                    help="수집된 전체 동영상 수"
                )
            
            with col2:
                total_views = df['view_count'].sum()
                avg_views = df['view_count'].mean()
                st.metric(
                    label="👀 총 조회수",
                    value=f"{total_views:,.0f}",
                    delta=f"평균 {avg_views:,.0f}",
                    help="모든 동영상의 총 조회수"
                )
            
            with col3:
                total_likes = df['like_count'].sum()
                avg_likes = df['like_count'].mean()
                st.metric(
                    label="👍 총 좋아요",
                    value=f"{total_likes:,.0f}",
                    delta=f"평균 {avg_likes:,.0f}",
                    help="모든 동영상의 총 좋아요 수"
                )
            
            with col4:
                total_comments = df['comment_count'].sum()
                avg_comments = df['comment_count'].mean()
                st.metric(
                    label="💬 총 댓글",
                    value=f"{total_comments:,.0f}",
                    delta=f"평균 {avg_comments:,.0f}",
                    help="모든 동영상의 총 댓글 수"
                )
                
        except Exception as e:
            st.error(f"메트릭 카드 생성 중 오류 발생: {str(e)}")

    def create_wordcloud_plot(self, wordcloud: WordCloud) -> Optional[Figure]:
        """워드클라우드 Matplotlib 플롯"""
        try:
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # 테마에 맞는 배경색 설정
            fig.patch.set_facecolor(self.bg_color)
            ax.set_facecolor(self.bg_color)
            
            ax.imshow(wordcloud.to_array(), interpolation='bilinear')
            ax.axis('off')
            
            plt.tight_layout(pad=0)
            return fig
            
        except Exception as e:
            st.error(f"워드클라우드 생성 중 오류 발생: {str(e)}")
            return None

    # 추가 기본 메소드들을 여기에 계속 추가할 예정
    def create_view_count_distribution(self, df):
        """조회수 분포 히스토그램"""
        try:
            fig = px.histogram(
                df, 
                x='view_count', 
                title='조회수 분포',
                nbins=30,
                color_discrete_sequence=[self.get_theme_colors()['accent']]
            )
            
            fig.update_layout(
                template=self.get_theme_colors()['plotly_template'],
                height=400
            )
            
            return fig
        except Exception as e:
            st.error(f"조회수 분포 차트 생성 중 오류 발생: {str(e)}")
            return None

    def create_engagement_scatter(self, df):
        """좋아요 대비 댓글 산점도 생성"""
        try:
            # 수치 데이터 검증
            if df.empty:
                return None
                
            # NaN 값 제거 및 수치형 변환
            df_clean = df.dropna(subset=['like_count', 'comment_count']).copy()
            df_clean['like_count'] = pd.to_numeric(df_clean['like_count'], errors='coerce')
            df_clean['comment_count'] = pd.to_numeric(df_clean['comment_count'], errors='coerce')
            df_clean = df_clean.dropna(subset=['like_count', 'comment_count'])
            
            if df_clean.empty:
                return None
            
            # 산점도 생성
            fig = px.scatter(
                df_clean,
                x='like_count',
                y='comment_count',
                color='category_id',
                hover_name='title',
                title="좋아요 vs 댓글 수 분포",
                labels={
                    'like_count': '좋아요 수',
                    'comment_count': '댓글 수',
                    'category_id': '카테고리'
                }
            )
            
            fig.update_layout(
                font=dict(family=self.font_family),
                paper_bgcolor=self.bg_color,
                plot_bgcolor=self.bg_color
            )
            
            return fig
            
        except Exception as e:
            st.error(f"산점도 생성 중 오류 발생: {str(e)}")
            return None

    def create_progress_visualization(self, current_step, total_steps, step_names):
        """단계별 진행 상황 시각화"""
        try:
            theme_colors = self.get_theme_colors()
            
            # 진행률 계산
            progress_percentage = (current_step / total_steps) * 100
            
            # 각 단계별 상태 설정
            step_statuses = []
            for i, step_name in enumerate(step_names):
                if i < current_step:
                    status = "완료"
                    color = theme_colors['success']
                elif i == current_step:
                    status = "진행중"
                    color = theme_colors['warning']
                else:
                    status = "대기"
                    color = theme_colors['text_secondary']
                
                step_statuses.append({
                    'step': i + 1,
                    'name': step_name,
                    'status': status,
                    'color': color,
                    'y_pos': len(step_names) - i
                })
            
            # 차트 생성
            fig = go.Figure()
            
            # 각 단계를 원형 마커로 표시
            for step_status in step_statuses:
                # 단계 원형 마커
                fig.add_trace(go.Scatter(
                    x=[1],
                    y=[step_status['y_pos']],
                    mode='markers+text',
                    marker=dict(
                        size=30,
                        color=step_status['color'],
                        line=dict(color=theme_colors['text_primary'], width=2)
                    ),
                    text=f"{step_status['step']}",
                    textfont=dict(color=theme_colors['text_primary'], size=12),
                    textposition="middle center",
                    showlegend=False,
                    hovertemplate=f"<b>{step_status['name']}</b><br>상태: {step_status['status']}<extra></extra>"
                ))
                
                # 단계 이름 표시
                fig.add_trace(go.Scatter(
                    x=[1.8],
                    y=[step_status['y_pos']],
                    mode='text',
                    text=f"{step_status['name']} ({step_status['status']})",
                    textfont=dict(
                        color=step_status['color'],
                        size=14,
                        family=self.font_family
                    ),
                    textposition="middle left",
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # 연결선 추가
            if len(step_statuses) > 1:
                y_positions = [status['y_pos'] for status in step_statuses]
                fig.add_trace(go.Scatter(
                    x=[1] * len(y_positions),
                    y=y_positions,
                    mode='lines',
                    line=dict(
                        color=theme_colors['border'],
                        width=2,
                        dash='dot'
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
            
            # 진행률 표시
            fig.add_annotation(
                x=1,
                y=len(step_names) + 0.8,
                text=f"진행률: {progress_percentage:.0f}%",
                showarrow=False,
                font=dict(
                    size=16,
                    color=theme_colors['accent'],
                    family=self.font_family
                )
            )
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text="📈 데이터 수집 진행 상황",
                    font=dict(size=20, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False,
                    range=[0.5, 4]
                ),
                yaxis=dict(
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False,
                    range=[0.5, len(step_names) + 1.2]
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                plot_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family),
                height=max(250, len(step_names) * 50 + 100),
                margin=dict(t=80, b=40, l=40, r=40)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"진행 상황 차트 생성 중 오류 발생: {str(e)}")
            return None

    def create_animated_bar_chart(self, keyword_freq, title="애니메이션 키워드 차트", max_keywords=15):
        """애니메이션 막대 차트 생성"""
        try:
            if not keyword_freq:
                return None
                
            # 상위 키워드 선택 및 빈도수 기준 정렬
            top_keywords = dict(list(keyword_freq.items())[:max_keywords])
            
            # 빈도수 기준으로 정렬 후 차트 표시를 위해 오름차순으로 배치 (높은 값이 위에 오도록)
            sorted_items = sorted(top_keywords.items(), key=lambda x: x[1], reverse=False)  # 오름차순으로 변경
            keywords = [item[0] for item in sorted_items]
            frequencies = [item[1] for item in sorted_items]
            
            if not keywords:
                return None
            
            theme_colors = self.get_theme_colors()
            
            # 애니메이션 효과를 위한 데이터 프레임 생성
            df_anim = pd.DataFrame({
                'keyword': keywords,
                'frequency': frequencies,
                'rank': range(1, len(keywords) + 1),
                'formatted_freq': [f"{freq:,}" for freq in frequencies]
            })
            
            # 애니메이션 막대 차트 생성 (go.Bar 사용)
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df_anim['frequency'],
                y=df_anim['keyword'],
                orientation='h',
                text=df_anim['formatted_freq'],
                textposition='auto',
                textfont=dict(color='white', size=11, family='Arial Black'),
                marker=dict(
                    color=df_anim['frequency'],
                    colorscale=theme_colors['color_sequence'][:2],
                    showscale=False
                ),
                hovertemplate="<b>%{y}</b><br>빈도: %{text}<extra></extra>"
            ))
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=20, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title="빈도수",
                    title_font=dict(color=theme_colors['text_primary']),
                    tickfont=dict(color=theme_colors['text_primary'])
                ),
                yaxis=dict(
                    title="키워드",
                    title_font=dict(color=theme_colors['text_primary']),
                    tickfont=dict(color=theme_colors['text_primary'])
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                plot_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family),
                margin=dict(t=60, b=40, l=80, r=20),
                height=max(400, len(keywords) * 25 + 100),
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            st.error(f"애니메이션 차트 생성 중 오류 발생: {str(e)}")
            return None

    def create_keyword_treemap(self, keyword_freq, max_keywords=20):
        """키워드 트리맵 생성"""
        try:
            if not keyword_freq:
                return None
                
            # 상위 키워드 선택
            top_keywords = dict(list(keyword_freq.items())[:max_keywords])
            
            if not top_keywords:
                return None
            
            keywords = list(top_keywords.keys())
            frequencies = list(top_keywords.values())
            
            # 0보다 큰 값만 필터링
            filtered_data = [(k, v) for k, v in zip(keywords, frequencies) if v > 0]
            
            if not filtered_data:
                return None
            
            keywords = [item[0] for item in filtered_data]
            frequencies = [item[1] for item in filtered_data]
            
            theme_colors = self.get_theme_colors()
            
            # 간단한 방식으로 트리맵 생성
            fig = go.Figure(go.Treemap(
                labels=keywords,
                values=frequencies,
                text=[f"{k}<br>{v:,}" for k, v in zip(keywords, frequencies)],
                textinfo="text",
                textfont=dict(size=12, color='white', family='Arial Black'),
                marker=dict(
                    colors=frequencies,
                    colorscale='Blues',
                    showscale=False
                ),
                hovertemplate="<b>%{label}</b><br>빈도: %{value:,}<extra></extra>"
            ))
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text="키워드 트리맵",
                    font=dict(size=18, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family),
                height=500,
                margin=dict(t=60, b=20, l=20, r=20)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"트리맵 생성 중 오류 발생: {str(e)}")
            return None

    def create_category_analysis(self, df):
        """카테고리 분석 차트 생성"""
        try:
            if df.empty:
                return None
            
            import config
            
            # 카테고리별 동영상 수 계산
            category_counts = df['category_id'].value_counts()
            
            # 카테고리 이름 매핑
            category_names = [config.CATEGORY_MAPPING.get(cat_id, f"카테고리 {cat_id}") 
                            for cat_id in category_counts.index]
            
            theme_colors = self.get_theme_colors()
            
            # 도넛 차트 생성
            fig = go.Figure(data=[go.Pie(
                labels=category_names,
                values=category_counts.values,
                hole=.3,
                textinfo='label+percent',
                textfont=dict(color=theme_colors['text_primary']),
                marker=dict(
                    colors=theme_colors['color_sequence'][:len(category_names)],
                    line=dict(color=theme_colors['border'], width=2)
                )
            )])
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text="카테고리별 동영상 분포",
                    font=dict(size=18, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family),
                showlegend=True,
                legend=dict(
                    font=dict(color=theme_colors['text_primary'])
                ),
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"카테고리 분석 차트 생성 중 오류 발생: {str(e)}")
            return None

    def create_realtime_counter(self, value, title, duration=2.0):
        """실시간 카운터 애니메이션"""
        try:
            theme_colors = self.get_theme_colors()
            
            # 카운터 값을 포맷팅
            if value >= 1000000:
                display_value = f"{value/1000000:.1f}M"
            elif value >= 1000:
                display_value = f"{value/1000:.1f}K"
            else:
                display_value = f"{value:,.0f}"
            
            # 게이지 차트로 카운터 시뮬레이션
            fig = go.Figure(go.Indicator(
                mode = "number",
                value = value,
                title = {"text": title, "font": {"color": theme_colors['text_primary']}},
                number = {
                    "font": {"color": theme_colors['accent'], "size": 24},
                    "suffix": "",
                    "valueformat": ",.0f"
                }
            ))
            
            # 레이아웃 설정
            fig.update_layout(
                paper_bgcolor=theme_colors['bg_card'],
                font=dict(family=self.font_family),
                height=150,
                margin=dict(t=40, b=20, l=20, r=20)
            )
            
            return fig
            
        except Exception as e:
            st.error(f"카운터 차트 생성 중 오류 발생: {str(e)}")
            return None

    def create_3d_scatter_plot(self, df, title="3D 성과 분석"):
        """3D 산점도 생성 (조회수, 좋아요, 댓글)"""
        try:
            if df.empty:
                return None
            
            # 수치 데이터 검증 및 정제
            df_clean = df.dropna(subset=['view_count', 'like_count', 'comment_count']).copy()
            df_clean['view_count'] = pd.to_numeric(df_clean['view_count'], errors='coerce')
            df_clean['like_count'] = pd.to_numeric(df_clean['like_count'], errors='coerce')
            df_clean['comment_count'] = pd.to_numeric(df_clean['comment_count'], errors='coerce')
            df_clean = df_clean.dropna(subset=['view_count', 'like_count', 'comment_count'])
            
            if df_clean.empty:
                return None
            
            # 카테고리 이름 매핑
            import config
            df_clean['category_name'] = df_clean['category_id'].map(
                lambda x: config.CATEGORY_MAPPING.get(x, f"카테고리 {x}")
            )
            
            theme_colors = self.get_theme_colors()
            
            # 3D 산점도 생성
            fig = px.scatter_3d(
                df_clean,
                x='view_count',
                y='like_count',
                z='comment_count',
                color='category_name',
                size='view_count',
                hover_name='title',
                hover_data={
                    'channel_title': True,
                    'view_count': ':,.0f',
                    'like_count': ':,.0f',
                    'comment_count': ':,.0f'
                },
                title=title,
                labels={
                    'view_count': '조회수',
                    'like_count': '좋아요 수',
                    'comment_count': '댓글 수',
                    'category_name': '카테고리'
                },
                size_max=20,
                color_discrete_sequence=theme_colors['color_sequence']
            )
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=20, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                scene=dict(
                    xaxis=dict(
                        title='조회수',
                        title_font=dict(color=theme_colors['text_primary']),
                        tickfont=dict(color=theme_colors['text_primary']),
                        gridcolor=theme_colors['border']
                    ),
                    yaxis=dict(
                        title='좋아요 수',
                        title_font=dict(color=theme_colors['text_primary']),
                        tickfont=dict(color=theme_colors['text_primary']),
                        gridcolor=theme_colors['border']
                    ),
                    zaxis=dict(
                        title='댓글 수',
                        title_font=dict(color=theme_colors['text_primary']),
                        tickfont=dict(color=theme_colors['text_primary']),
                        gridcolor=theme_colors['border']
                    ),
                    bgcolor=theme_colors['bg_primary']
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family),
                legend=dict(
                    font=dict(color=theme_colors['text_primary'])
                ),
                height=600
            )
            
            return fig
            
        except Exception as e:
            st.error(f"3D 산점도 생성 중 오류 발생: {str(e)}")
            return None

    def create_trend_timeline(self, df):
        """시간별 트렌드 타임라인 생성"""
        try:
            if df.empty or 'published_at' not in df.columns:
                return None
            
            # 날짜 데이터 처리
            df_clean = df.copy()
            df_clean['published_at'] = pd.to_datetime(df_clean['published_at'], errors='coerce')
            df_clean = df_clean.dropna(subset=['published_at'])
            
            if df_clean.empty:
                return None
            
            # 날짜별 동영상 수와 평균 조회수 계산
            df_clean['date'] = df_clean['published_at'].dt.date
            daily_stats = df_clean.groupby('date').agg({
                'video_id': 'count',
                'view_count': 'mean'
            }).reset_index()
            daily_stats.columns = ['date', 'video_count', 'avg_views']
            
            theme_colors = self.get_theme_colors()
            
            # 이중 Y축 차트 생성
            fig = make_subplots(
                specs=[[{"secondary_y": True}]],
                subplot_titles=["시간별 동영상 업로드 트렌드"]
            )
            
            # 동영상 수 (막대 차트)
            fig.add_trace(
                go.Bar(
                    x=daily_stats['date'],
                    y=daily_stats['video_count'],
                    name='동영상 수',
                    marker_color=theme_colors['accent'],
                    opacity=0.7
                ),
                secondary_y=False,
            )
            
            # 평균 조회수 (선 차트)
            fig.add_trace(
                go.Scatter(
                    x=daily_stats['date'],
                    y=daily_stats['avg_views'],
                    mode='lines+markers',
                    name='평균 조회수',
                    line=dict(color=theme_colors['accent_secondary'], width=3),
                    marker=dict(size=8)
                ),
                secondary_y=True,
            )
            
            # Y축 제목 설정
            fig.update_xaxes(title_text="날짜")
            fig.update_yaxes(title_text="동영상 수", secondary_y=False)
            fig.update_yaxes(title_text="평균 조회수", secondary_y=True)
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text="📅 시간별 업로드 트렌드",
                    font=dict(size=18, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                plot_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family, color=theme_colors['text_primary']),
                legend=dict(
                    font=dict(color=theme_colors['text_primary'])
                ),
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"타임라인 차트 생성 중 오류 발생: {str(e)}")
            return None

    def create_correlation_heatmap(self, df):
        """상관관계 히트맵 생성"""
        try:
            if df.empty:
                return None
            
            # 수치형 컬럼 선택
            numeric_columns = ['view_count', 'like_count', 'comment_count']
            available_columns = [col for col in numeric_columns if col in df.columns]
            
            if len(available_columns) < 2:
                return None
            
            # 수치 데이터만 추출하고 정제
            df_numeric = df[available_columns].copy()
            for col in available_columns:
                df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')
            
            df_numeric = df_numeric.dropna()
            
            if df_numeric.empty:
                return None
            
            # 상관관계 계산
            correlation_matrix = df_numeric.corr()
            
            theme_colors = self.get_theme_colors()
            
            # 히트맵 생성
            fig = px.imshow(
                correlation_matrix,
                text_auto=True,
                aspect="auto",
                title="📊 지표 간 상관관계 분석",
                color_continuous_scale=['red', 'white', 'blue'],
                labels=dict(
                    x="지표",
                    y="지표",
                    color="상관계수"
                )
            )
            
            # 축 레이블 한글화
            korean_labels = {
                'view_count': '조회수',
                'like_count': '좋아요',
                'comment_count': '댓글수'
            }
            
            fig.update_xaxes(
                ticktext=[korean_labels.get(col, col) for col in correlation_matrix.columns],
                tickvals=list(range(len(correlation_matrix.columns)))
            )
            fig.update_yaxes(
                ticktext=[korean_labels.get(col, col) for col in correlation_matrix.index],
                tickvals=list(range(len(correlation_matrix.index)))
            )
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    font=dict(size=18, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family, color=theme_colors['text_primary']),
                height=400,
                coloraxis_colorbar=dict(
                    title="상관계수",
                    titlefont=dict(color=theme_colors['text_primary']),
                    tickfont=dict(color=theme_colors['text_primary'])
                )
            )
            
            return fig
            
        except Exception as e:
            st.error(f"상관관계 히트맵 생성 중 오류 발생: {str(e)}")
            return None

    def create_channel_comparison_chart(self, channel_stats, metric='총_조회수', title="채널 비교"):
        """채널 비교 막대 차트 생성"""
        try:
            if channel_stats.empty:
                return None
            
            theme_colors = self.get_theme_colors()
            
            # 상위 10개 채널만 표시
            top_channels = channel_stats.nlargest(10, metric).copy()
            
            # 수치 데이터 확실히 변환
            top_channels[metric] = pd.to_numeric(top_channels[metric], errors='coerce')
            top_channels = top_channels.dropna(subset=[metric])
            
            if top_channels.empty:
                return None
            
            # 포맷된 텍스트 생성
            top_channels['formatted_text'] = top_channels[metric].apply(lambda x: f"{x:,.0f}")
            
            # 데이터 정렬 (내림차순으로 정렬)
            top_channels = top_channels.sort_values(metric, ascending=True)
            
            # 막대 차트 생성
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=top_channels[metric],
                y=top_channels['channel_title'],
                orientation='h',
                text=top_channels['formatted_text'],
                textposition='auto',
                textfont=dict(color=theme_colors['text_primary'], size=12),
                marker=dict(
                    color=top_channels[metric],
                    colorscale=theme_colors['color_sequence'][:3],
                    showscale=False
                ),
                hovertemplate="<b>%{y}</b><br>" + metric.replace('_', ' ') + ": %{text}<extra></extra>"
            ))
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=18, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title=metric.replace('_', ' '),
                    title_font=dict(color=theme_colors['text_primary']),
                    tickfont=dict(color=theme_colors['text_primary'])
                ),
                yaxis=dict(
                    title="채널명",
                    title_font=dict(color=theme_colors['text_primary']),
                    tickfont=dict(color=theme_colors['text_primary'])
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                plot_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family),
                height=max(400, len(top_channels) * 30 + 100),
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            st.error(f"채널 비교 차트 생성 중 오류 발생: {str(e)}")
            return None



    def create_channel_category_distribution(self, channel_videos, title="채널별 카테고리 분포"):
        """채널별 카테고리 분포 차트 생성"""
        try:
            if channel_videos.empty:
                return None
            
            import config
            
            # 채널별 카테고리 분포 계산
            channel_category = channel_videos.groupby(['channel_title', 'category_id']).size().reset_index(name='count')
            
            # 카테고리 이름 매핑
            channel_category['category_name'] = channel_category['category_id'].map(
                lambda x: config.CATEGORY_MAPPING.get(x, f"카테고리 {x}")
            )
            
            theme_colors = self.get_theme_colors()
            
            # 누적 막대 차트 생성
            fig = px.bar(
                channel_category,
                x='channel_title',
                y='count',
                color='category_name',
                title=title,
                labels={
                    'channel_title': '채널명',
                    'count': '동영상 수',
                    'category_name': '카테고리'
                },
                color_discrete_sequence=theme_colors['color_sequence']
            )
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=18, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title='채널명',
                    title_font=dict(color=theme_colors['text_primary']),
                    tickfont=dict(color=theme_colors['text_primary']),
                    tickangle=45
                ),
                yaxis=dict(
                    title='동영상 수',
                    title_font=dict(color=theme_colors['text_primary']),
                    tickfont=dict(color=theme_colors['text_primary'])
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                plot_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family),
                legend=dict(
                    font=dict(color=theme_colors['text_primary'])
                ),
                height=500
            )
            
            return fig
            
        except Exception as e:
            st.error(f"채널 카테고리 분포 차트 생성 중 오류 발생: {str(e)}")
            return None



    def create_keyword_network_graph(self, network_data, title="키워드 네트워크"):
        """키워드 네트워크 그래프 생성"""
        try:
            if not network_data or 'nodes' not in network_data or 'edges' not in network_data:
                return None
            
            nodes = network_data['nodes']
            edges = network_data['edges']
            
            if not nodes or not edges:
                return None
            
            theme_colors = self.get_theme_colors()
            
            # 노드 위치 계산 (원형 배치)
            import math
            n_nodes = len(nodes)
            node_positions = {}
            
            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / n_nodes
                radius = 1 + node.get('frequency', 1) * 0.1  # 빈도에 따라 반지름 조정
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                node_positions[node['id']] = (x, y)
            
            # 엣지 트레이스 생성
            edge_x = []
            edge_y = []
            
            for edge in edges:
                x0, y0 = node_positions[edge['source']]
                x1, y1 = node_positions[edge['target']]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            # 노드 트레이스 생성
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            node_color = []
            
            for node in nodes:
                x, y = node_positions[node['id']]
                node_x.append(x)
                node_y.append(y)
                node_text.append(node['id'])
                node_size.append(max(10, node.get('frequency', 1) * 2))
                node_color.append(node.get('frequency', 1))
            
            # 네트워크 그래프 생성
            fig = go.Figure()
            
            # 엣지 추가
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color=theme_colors['border']),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            ))
            
            # 노드 추가
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=node_size,
                    color=node_color,
                    colorscale=theme_colors['color_sequence'][:3],
                    line=dict(width=2, color=theme_colors['text_primary'])
                ),
                text=node_text,
                textposition="middle center",
                textfont=dict(color=theme_colors['text_primary'], size=10),
                hovertemplate="<b>%{text}</b><br>빈도: %{marker.color}<extra></extra>",
                showlegend=False
            ))
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=18, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="노드 크기 = 키워드 빈도",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ,
                    font=dict(color=theme_colors['text_secondary'], size=12),
                    align="left"
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                paper_bgcolor=theme_colors['bg_primary'],
                plot_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family),
                height=600
            )
            
            return fig
            
        except Exception as e:
            st.error(f"키워드 네트워크 그래프 생성 중 오류 발생: {str(e)}")
            return None

    def create_keyword_cluster_chart(self, clusters, title="키워드 클러스터"):
        """키워드 클러스터 차트 생성"""
        try:
            if not clusters:
                return None
            
            theme_colors = self.get_theme_colors()
            
            # 클러스터 데이터 준비
            cluster_data = []
            colors = theme_colors['color_sequence']
            
            for i, cluster in enumerate(clusters[:10]):  # 최대 10개 클러스터
                cluster_data.append({
                    'cluster': f"클러스터 {i+1}",
                    'size': cluster['size'],
                    'avg_freq': cluster['avg_freq'],
                    'keywords': ', '.join(cluster['keywords'][:3]) + ('...' if len(cluster['keywords']) > 3 else '')
                })
            
            if not cluster_data:
                return None
            
            # 클러스터 크기별 막대 차트
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=[item['cluster'] for item in cluster_data],
                y=[item['size'] for item in cluster_data],
                text=[f"{item['size']}개 키워드" for item in cluster_data],
                textposition='auto',
                textfont=dict(color=theme_colors['text_primary'], size=12),
                marker=dict(
                    color=[item['avg_freq'] for item in cluster_data],
                    colorscale=theme_colors['color_sequence'][:3],
                    showscale=False
                ),
                hovertemplate="<b>%{x}</b><br>키워드 수: %{y}<br>평균 빈도: %{marker.color:.1f}<extra></extra>"
            ))
            
            # 레이아웃 설정
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=18, color=theme_colors['text_primary']),
                    x=0.5,
                    xanchor='center'
                ),
                xaxis=dict(
                    title="클러스터",
                    title_font=dict(color=theme_colors['text_primary']),
                    tickfont=dict(color=theme_colors['text_primary'])
                ),
                yaxis=dict(
                    title="키워드 수",
                    title_font=dict(color=theme_colors['text_primary']),
                    tickfont=dict(color=theme_colors['text_primary'])
                ),
                paper_bgcolor=theme_colors['bg_primary'],
                plot_bgcolor=theme_colors['bg_primary'],
                font=dict(family=self.font_family),
                height=400,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            st.error(f"키워드 클러스터 차트 생성 중 오류 발생: {str(e)}")
            return None