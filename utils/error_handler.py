import streamlit as st
import logging
from functools import wraps
from googleapiclient.errors import HttpError
import pandas as pd

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeAPIError(Exception):
    """YouTube API 관련 커스텀 예외"""
    pass

class TextProcessingError(Exception):
    """텍스트 처리 관련 커스텀 예외"""
    pass

def handle_youtube_api_error(func):
    """YouTube API 호출 에러 처리 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            error_code = e.resp.status
            error_message = e.content.decode('utf-8') if e.content else str(e)
            
            if error_code == 403:
                if 'quotaExceeded' in error_message:
                    st.error("🚫 YouTube API 할당량이 초과되었습니다. 잠시 후 다시 시도해주세요.")
                    logger.error(f"YouTube API 할당량 초과: {error_message}")
                elif 'accessNotConfigured' in error_message:
                    st.error("🔑 YouTube API가 활성화되지 않았습니다. Google Cloud Console에서 API를 활성화해주세요.")
                    logger.error(f"YouTube API 비활성화: {error_message}")
                else:
                    st.error("🚫 YouTube API 접근이 거부되었습니다. API 키를 확인해주세요.")
                    logger.error(f"YouTube API 접근 거부: {error_message}")
            elif error_code == 400:
                st.error("📝 잘못된 요청입니다. 검색어나 매개변수를 확인해주세요.")
                logger.error(f"YouTube API 잘못된 요청: {error_message}")
            elif error_code == 500:
                st.error("🔧 YouTube 서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")
                logger.error(f"YouTube API 서버 오류: {error_message}")
            else:
                st.error(f"🔴 YouTube API 오류 ({error_code}): 관리자에게 문의하세요.")
                logger.error(f"YouTube API 기타 오류: {error_code} - {error_message}")
            
            return pd.DataFrame()
        except Exception as e:
            st.error(f"🔴 예상치 못한 오류가 발생했습니다: {str(e)}")
            logger.error(f"예상치 못한 오류: {str(e)}")
            return pd.DataFrame()
    
    return wrapper

def handle_text_processing_error(func):
    """텍스트 처리 에러 처리 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            function_name = func.__name__
            st.warning(f"⚠️ {function_name} 처리 중 오류가 발생했습니다: {str(e)}")
            logger.warning(f"텍스트 처리 오류 in {function_name}: {str(e)}")
            return [] if function_name.startswith('extract') else pd.DataFrame()
    
    return wrapper

def safe_streamlit_write(message, level="info"):
    """안전한 Streamlit 메시지 출력"""
    try:
        if level == "error":
            st.error(message)
        elif level == "warning":
            st.warning(message)
        elif level == "success":
            st.success(message)
        else:
            st.info(message)
    except Exception as e:
        # Streamlit 컨텍스트 외부에서 호출된 경우
        print(f"[{level.upper()}] {message}")
        logger.info(f"Streamlit 컨텍스트 외부 메시지: {message}")

def validate_api_key(api_key):
    """API 키 유효성 검증"""
    if not api_key:
        raise YouTubeAPIError("YouTube API 키가 설정되지 않았습니다.")
    
    if not api_key.startswith('AIza'):
        raise YouTubeAPIError("올바르지 않은 YouTube API 키 형식입니다.")
    
    return True

def validate_search_query(query):
    """검색 쿼리 유효성 검증"""
    if not query or not query.strip():
        raise ValueError("검색어를 입력해주세요.")
    
    if len(query) > 100:
        raise ValueError("검색어는 100자 이하로 입력해주세요.")
    
    return query.strip()

def validate_max_results(max_results):
    """최대 결과 수 유효성 검증"""
    if not isinstance(max_results, int) or max_results < 1:
        raise ValueError("최대 결과 수는 1 이상의 정수여야 합니다.")
    
    if max_results > 50:
        raise ValueError("최대 결과 수는 50개를 초과할 수 없습니다.")
    
    return max_results

class ProgressTracker:
    """진행 상황 추적 클래스"""
    
    def __init__(self, total_steps, description="처리 중..."):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.progress_bar = st.progress(0)
        self.status_text = st.empty()
    
    def update(self, step_description=""):
        """진행 상황 업데이트"""
        self.current_step += 1
        progress = self.current_step / self.total_steps
        
        self.progress_bar.progress(progress)
        
        if step_description:
            self.status_text.text(f"{self.description} - {step_description}")
        else:
            self.status_text.text(f"{self.description} - {self.current_step}/{self.total_steps}")
    
    def complete(self, message="완료!"):
        """진행 상황 완료"""
        self.progress_bar.progress(1.0)
        self.status_text.text(message)
    
    def clear(self):
        """진행 상황 표시 제거"""
        self.progress_bar.empty()
        self.status_text.empty() 