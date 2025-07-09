import re
import pandas as pd
import numpy as np
from collections import Counter
import streamlit as st

# 텍스트 처리 라이브러리
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud

# 한국어 처리 - Windows 환경에서 segmentation fault 문제로 인해 비활성화
# try:
#     from konlpy.tag import Okt, Komoran
#     KONLPY_AVAILABLE = True
# except (ImportError, Exception) as e:
#     KONLPY_AVAILABLE = False
#     print(f"KoNLPy 로딩 실패: {e}")

# Windows 환경에서 KoNLPy 문제로 인해 임시로 비활성화
KONLPY_AVAILABLE = False
print("한국어 형태소 분석기가 비활성화되었습니다. 기본 텍스트 처리를 사용합니다.")

import config

class TextProcessor:
    """텍스트 전처리 및 키워드 추출 클래스"""
    
    def __init__(self):
        self.download_nltk_data()
        self.setup_korean_analyzer()
        self.setup_stopwords()
    
    def download_nltk_data(self):
        """NLTK 데이터 다운로드"""
        try:
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            print("NLTK 데이터 다운로드 완료")
        except Exception as e:
            print(f"NLTK 데이터 다운로드 실패: {e}")
    
    def setup_korean_analyzer(self):
        """한국어 형태소 분석기 설정"""
        if KONLPY_AVAILABLE:
            try:
                # KoNLPy 비활성화로 인해 주석 처리
                # self.okt = Okt()
                # self.komoran = Komoran()
                self.korean_available = True
            except Exception as e:
                print(f"한국어 분석기 초기화 실패: {e}")
                self.korean_available = False
        else:
            self.korean_available = False
    
    def setup_stopwords(self):
        """불용어 사전 설정"""
        # 영어 불용어
        try:
            self.english_stopwords = set(stopwords.words('english'))
            self.english_stopwords.update(config.CUSTOM_STOPWORDS_EN)
        except Exception:
            self.english_stopwords = set(config.CUSTOM_STOPWORDS_EN)
        
        # 한국어 불용어
        self.korean_stopwords = set(config.CUSTOM_STOPWORDS_KR)
    
    def clean_text(self, text):
        """텍스트 전처리"""
        if not text or pd.isna(text):
            return ""
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # URL 제거
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 특수문자 제거 (한국어, 영어, 숫자, 공백만 유지)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_korean_keywords(self, text, min_length=2):
        """한국어 키워드 추출 - KoNLPy 비활성화로 인해 기본 텍스트 처리 사용"""
        if not self.korean_available or not text:
            return []
        
        try:
            # KoNLPy 비활성화로 인해 간단한 공백 기반 분할 사용
            # morphs = self.okt.morphs(text)
            words = text.split()
            
            # 불용어 제거 및 길이 필터링
            keywords = [
                word for word in words 
                if len(word) >= min_length 
                and word not in self.korean_stopwords
                and not word.isdigit()
            ]
            
            return keywords
        except Exception as e:
            print(f"한국어 키워드 추출 실패: {e}")
            return []
    
    def extract_english_keywords(self, text, min_length=2):
        """영어 키워드 추출"""
        if not text:
            return []
        
        try:
            # NLTK 토크나이저 사용 시도
            tokens = word_tokenize(text.lower())
        except Exception as e:
            print(f"NLTK 토크나이저 실패, 간단한 분할 사용: {e}")
            # NLTK 실패 시 간단한 공백 기반 분할 사용
            tokens = text.lower().split()
        
        try:
            # 불용어 제거 및 길이 필터링
            keywords = [
                word for word in tokens 
                if len(word) >= min_length 
                and word not in self.english_stopwords
                and word.isalpha()
            ]
            
            return keywords
        except Exception as e:
            print(f"영어 키워드 추출 실패: {e}")
            return []
    
    def is_korean(self, text):
        """한국어 텍스트 여부 확인"""
        if not text:
            return False
        korean_chars = re.findall(r'[가-힣]', text)
        return len(korean_chars) > len(text) * 0.3
    
    def extract_keywords_from_text(self, text, min_length=None):
        """텍스트에서 키워드 추출"""
        if min_length is None:
            min_length = config.MIN_WORD_LENGTH
        
        cleaned_text = self.clean_text(text)
        
        if self.is_korean(cleaned_text):
            return self.extract_korean_keywords(cleaned_text, min_length)
        else:
            return self.extract_english_keywords(cleaned_text, min_length)
    
    def extract_keywords_from_dataframe(self, df, text_columns=['title', 'description']):
        """DataFrame에서 키워드 추출"""
        all_keywords = []
        
        for _, row in df.iterrows():
            for column in text_columns:
                if column in row and row[column]:
                    keywords = self.extract_keywords_from_text(row[column])
                    all_keywords.extend(keywords)
            
            # 태그 처리
            if 'tags' in row and row['tags']:
                if isinstance(row['tags'], list):
                    for tag in row['tags']:
                        tag_keywords = self.extract_keywords_from_text(tag)
                        all_keywords.extend(tag_keywords)
        
        return all_keywords
    
    def get_keyword_frequency(self, keywords, max_keywords=None):
        """키워드 빈도 계산"""
        if max_keywords is None:
            max_keywords = config.MAX_KEYWORDS
        
        counter = Counter(keywords)
        most_common = counter.most_common(max_keywords)
        
        return pd.DataFrame(most_common, columns=['keyword', 'frequency'])
    
    def calculate_tfidf_scores(self, texts, max_features=100):
        """TF-IDF 점수 계산"""
        try:
            # 텍스트 전처리
            cleaned_texts = [self.clean_text(text) for text in texts if text]
            
            # TF-IDF 벡터화
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                ngram_range=(1, 2),
                stop_words=None  # 이미 전처리에서 제거
            )
            
            tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # 평균 TF-IDF 점수 계산
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # 결과 DataFrame 생성
            tfidf_df = pd.DataFrame({
                'keyword': feature_names,
                'tfidf_score': mean_scores
            }).sort_values('tfidf_score', ascending=False)
            
            return tfidf_df
            
        except Exception as e:
            st.error(f"TF-IDF 계산 실패: {e}")
            return pd.DataFrame()
    
    def generate_wordcloud(self, keywords_freq, width=None, height=None):
        """워드클라우드 생성"""
        if width is None:
            width = config.WORDCLOUD_WIDTH
        if height is None:
            height = config.WORDCLOUD_HEIGHT
        
        try:
            # 키워드 빈도를 딕셔너리로 변환
            if isinstance(keywords_freq, pd.DataFrame):
                word_freq = dict(zip(keywords_freq['keyword'], keywords_freq['frequency']))
            elif isinstance(keywords_freq, dict):
                word_freq = keywords_freq
            else:
                return None
            
            # 워드클라우드 생성
            wordcloud = WordCloud(
                width=width,
                height=height,
                background_color=config.WORDCLOUD_BACKGROUND,
                colormap=config.WORDCLOUD_COLORMAP,
                font_path='NanumGothic.ttf',  # 한국어 폰트 (필요시)
                relative_scaling=0.5,
                max_words=100
            ).generate_from_frequencies(word_freq)
            
            return wordcloud
            
        except Exception as e:
            st.error(f"워드클라우드 생성 실패: {e}")
            return None 