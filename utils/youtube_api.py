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
            videos_data = []
            collected_count = 0
            
            # YouTube API는 한 번에 최대 50개까지만 가져올 수 있음
            # 더 많은 데이터를 원하면 여러 번 호출해야 함
            while collected_count < max_results:
                # 이번 호출에서 가져올 개수 (최대 50개)
                current_batch_size = min(50, max_results - collected_count)
                
                request = _self.service.videos().list(
                    part='snippet,statistics',
                    chart='mostPopular',
                    regionCode=region_code,
                    maxResults=current_batch_size
                )
                response = request.execute()
                
                # 응답에서 동영상이 없으면 중단
                if not response.get('items'):
                    break
                
                for item in response['items']:
                    video_data = {
                        'video_id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'channel_title': item['snippet']['channelTitle'],
                        'category_id': item['snippet']['categoryId'],
                        'tags': ', '.join(item['snippet'].get('tags', [])),  # 리스트를 문자열로 변환
                        'published_at': item['snippet']['publishedAt'],
                        'view_count': int(item['statistics'].get('viewCount', 0)),
                        'like_count': int(item['statistics'].get('likeCount', 0)),
                        'comment_count': int(item['statistics'].get('commentCount', 0))
                    }
                    videos_data.append(video_data)
                    collected_count += 1
                    
                    # 목표 개수에 도달하면 중단
                    if collected_count >= max_results:
                        break
                
                # 더 이상 가져올 데이터가 없으면 중단
                # 트렌딩 API는 pageToken을 제공하지 않으므로 한 번만 호출
                break
            
            return pd.DataFrame(videos_data)
            
        except HttpError as e:
            st.error(f"YouTube API 호출 오류: {e}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"예상치 못한 오류: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def get_videos_by_category(_self, category_id, region_code='KR', max_results=50):
        """
        카테고리별 인기 동영상 가져오기
        
        Args:
            category_id (str): 카테고리 ID
            region_code (str): 지역 코드 (기본값: 'KR')
            max_results (int): 최대 결과 수
            
        Returns:
            pd.DataFrame: 카테고리별 인기 동영상 데이터
        """
        try:
            videos_data = []
            collected_count = 0
            
            # 카테고리별 인기 동영상도 한 번에 최대 50개까지만 가져올 수 있음
            while collected_count < max_results:
                # 이번 호출에서 가져올 개수 (최대 50개)
                current_batch_size = min(50, max_results - collected_count)
                
                request = _self.service.videos().list(
                    part='snippet,statistics',
                    chart='mostPopular',
                    regionCode=region_code,
                    videoCategoryId=category_id,
                    maxResults=current_batch_size
                )
                response = request.execute()
                
                # 응답에서 동영상이 없으면 중단
                if not response.get('items'):
                    break
                
                for item in response['items']:
                    video_data = {
                        'video_id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'channel_title': item['snippet']['channelTitle'],
                        'category_id': item['snippet']['categoryId'],
                        'tags': ', '.join(item['snippet'].get('tags', [])),  # 리스트를 문자열로 변환
                        'published_at': item['snippet']['publishedAt'],
                        'view_count': int(item['statistics'].get('viewCount', 0)),
                        'like_count': int(item['statistics'].get('likeCount', 0)),
                        'comment_count': int(item['statistics'].get('commentCount', 0))
                    }
                    videos_data.append(video_data)
                    collected_count += 1
                    
                    # 목표 개수에 도달하면 중단
                    if collected_count >= max_results:
                        break
                
                # 카테고리별 인기 동영상 API도 pageToken을 제공하지 않으므로 한 번만 호출
                break
            
            return pd.DataFrame(videos_data)
            
        except HttpError as e:
            st.error(f"YouTube API 호출 오류: {e}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"예상치 못한 오류: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=config.CACHE_TTL)
    def search_videos(_self, query, max_results=50):
        """
        키워드로 동영상 검색
        
        Args:
            query (str): 검색 키워드
            max_results (int): 최대 결과 수
            
        Returns:
            pd.DataFrame: 검색 결과 동영상 데이터
        """
        try:
            videos_data = []
            next_page_token = None
            collected_count = 0
            
            # 여러 페이지를 가져와서 더 많은 결과 수집
            while collected_count < max_results:
                # 이번 호출에서 가져올 개수 (최대 50개)
                current_batch_size = min(50, max_results - collected_count)
                
                # 검색 요청
                search_request = _self.service.search().list(
                    part='snippet',
                    q=query,
                    type='video',
                    maxResults=current_batch_size,
                    order='relevance',
                    regionCode='KR',
                    pageToken=next_page_token
                )
                search_response = search_request.execute()
                
                # 검색 결과가 없으면 중단
                if not search_response.get('items'):
                    break
                
                # 동영상 ID 목록 추출
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                
                # 상세 정보 가져오기
                videos_request = _self.service.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids)
                )
                videos_response = videos_request.execute()
                
                for item in videos_response['items']:
                    video_data = {
                        'video_id': item['id'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'channel_title': item['snippet']['channelTitle'],
                        'category_id': item['snippet']['categoryId'],
                        'tags': ', '.join(item['snippet'].get('tags', [])),  # 리스트를 문자열로 변환
                        'published_at': item['snippet']['publishedAt'],
                        'view_count': int(item['statistics'].get('viewCount', 0)),
                        'like_count': int(item['statistics'].get('likeCount', 0)),
                        'comment_count': int(item['statistics'].get('commentCount', 0))
                    }
                    videos_data.append(video_data)
                    collected_count += 1
                    
                    # 목표 개수에 도달하면 중단
                    if collected_count >= max_results:
                        break
                
                # 다음 페이지 토큰 확인
                next_page_token = search_response.get('nextPageToken')
                if not next_page_token:
                    # 더 이상 페이지가 없으면 중단
                    break
            
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