import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import config

class YouTubeAPI:
    """YouTube Data API v3 클라이언트"""
    
    def __init__(self):
        self.api_key = config.YOUTUBE_API_KEY
        self.service = None
        self._build_service()
    
    def _build_service(self):
        """YouTube API 서비스 빌드"""
        try:
            self.service = build(
                config.YOUTUBE_API_SERVICE_NAME,
                config.YOUTUBE_API_VERSION,
                developerKey=self.api_key
            )
        except Exception as e:
            st.error(f"YouTube API 서비스 초기화 실패: {e}")
            return None
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_trending_videos(_self, region_code='KR', max_results=50):
        """
        트렌딩 동영상 목록 가져오기
        
        Args:
            region_code (str): 지역 코드 (기본값: 'KR')
            max_results (int): 최대 결과 수
            
        Returns:
            pd.DataFrame: 트렌딩 동영상 데이터
        """
        try:
            request = _self.service.videos().list(
                part='snippet,statistics',
                chart='mostPopular',
                regionCode=region_code,
                maxResults=max_results
            )
            response = request.execute()
            
            videos_data = []
            for item in response['items']:
                video_data = {
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'category_id': item['snippet']['categoryId'],
                    'tags': item['snippet'].get('tags', []),
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0))
                }
                videos_data.append(video_data)
            
            return pd.DataFrame(videos_data)
            
        except HttpError as e:
            st.error(f"YouTube API 호출 오류: {e}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"예상치 못한 오류: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_videos_by_category(_self, category_id, region_code='KR', max_results=25):
        """
        카테고리별 인기 동영상 가져오기
        
        Args:
            category_id (str): 카테고리 ID
            region_code (str): 지역 코드
            max_results (int): 최대 결과 수
            
        Returns:
            pd.DataFrame: 카테고리별 동영상 데이터
        """
        try:
            request = _self.service.videos().list(
                part='snippet,statistics',
                chart='mostPopular',
                regionCode=region_code,
                categoryId=category_id,
                maxResults=max_results
            )
            response = request.execute()
            
            videos_data = []
            for item in response['items']:
                video_data = {
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'category_id': item['snippet']['categoryId'],
                    'tags': item['snippet'].get('tags', []),
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0))
                }
                videos_data.append(video_data)
            
            return pd.DataFrame(videos_data)
            
        except HttpError as e:
            st.error(f"YouTube API 호출 오류: {e}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"예상치 못한 오류: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def search_videos(_self, query, max_results=25, order='relevance'):
        """
        키워드로 동영상 검색
        
        Args:
            query (str): 검색 쿼리
            max_results (int): 최대 결과 수
            order (str): 정렬 기준 ('relevance', 'date', 'rating', 'viewCount')
            
        Returns:
            pd.DataFrame: 검색 결과 데이터
        """
        try:
            search_request = _self.service.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results,
                order=order
            )
            search_response = search_request.execute()
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # 동영상 상세 정보 가져오기
            videos_request = _self.service.videos().list(
                part='snippet,statistics',
                id=','.join(video_ids)
            )
            videos_response = videos_request.execute()
            
            videos_data = []
            for item in videos_response['items']:
                video_data = {
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'category_id': item['snippet']['categoryId'],
                    'tags': item['snippet'].get('tags', []),
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0))
                }
                videos_data.append(video_data)
            
            return pd.DataFrame(videos_data)
            
        except HttpError as e:
            st.error(f"YouTube API 호출 오류: {e}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"예상치 못한 오류: {e}")
            return pd.DataFrame()
    
    def get_category_name(self, category_id):
        """카테고리 ID를 이름으로 변환"""
        return config.CATEGORY_MAPPING.get(category_id, f"카테고리 {category_id}") 