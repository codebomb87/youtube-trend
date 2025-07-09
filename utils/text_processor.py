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

# Kiwi 형태소 분석기 (Windows 환경에서 안정적)
try:
    from kiwipiepy import Kiwi
    KIWI_AVAILABLE = True
    print("Kiwi 형태소 분석기가 성공적으로 로드되었습니다.")
except ImportError as e:
    KIWI_AVAILABLE = False
    print(f"Kiwi 로딩 실패: {e}")

# 한국어 처리 - Windows 환경에서 segmentation fault 문제로 인해 비활성화
# try:
#     from konlpy.tag import Okt, Komoran
#     KONLPY_AVAILABLE = True
# except (ImportError, Exception) as e:
#     KONLPY_AVAILABLE = False
#     print(f"KoNLPy 로딩 실패: {e}")

# Windows 환경에서 KoNLPy 문제로 인해 임시로 비활성화
KONLPY_AVAILABLE = False
print("한국어 형태소 분석기가 비활성화되었습니다. Kiwi를 우선 사용합니다.")

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
        if KIWI_AVAILABLE:
            try:
                self.kiwi = Kiwi()
                self.korean_available = True
                print("Kiwi 형태소 분석기 초기화 완료")
            except Exception as e:
                print(f"Kiwi 초기화 실패: {e}")
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
        
        # Kiwi용 품사 태그 필터 (제외할 품사들)
        self.exclude_pos_tags = {
            'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC',  # 조사
            'EP', 'EF', 'EC', 'ETN', 'ETM',  # 어미
            'XSV', 'XSA', 'XR',  # 접미사
            'SF', 'SP', 'SS', 'SE', 'SO', 'SW',  # 기호
            'VCP', 'VCN',  # 긍정지정사, 부정지정사
            'MAG', 'MAJ',  # 일반부사, 접속부사
        }
        
        # 유지할 품사 태그 (주요 의미 단어들)
        self.keep_pos_tags = {
            'NNG', 'NNP', 'NNB',  # 일반명사, 고유명사, 의존명사
            'VV', 'VA',  # 동사, 형용사 (어간만)
            'MM',  # 관형사
            'NR',  # 수사
            'SL', 'SH', 'SN'  # 외국어, 한자, 숫자
        }
    
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
    
    def extract_korean_keywords_with_kiwi(self, text, min_length=2):
        """Kiwi를 사용한 한국어 키워드 추출"""
        if not text or not self.korean_available:
            return []
        
        try:
            # Kiwi로 형태소 분석
            tokens = self.kiwi.tokenize(text)
            
            keywords = []
            for token in tokens:
                word = token.form
                pos = token.tag
                
                # 길이 확인
                if len(word) < min_length:
                    continue
                
                # 제외할 품사 확인 (조사, 어미, 접미사 등)
                if pos in self.exclude_pos_tags:
                    continue
                
                # 포함할 품사만 허용 (명사, 동사, 형용사)
                if pos not in self.keep_pos_tags:
                    continue
                
                # 불용어 확인
                if word in self.korean_stopwords:
                    continue
                
                # 숫자만으로 이루어진 단어 제외
                if word.isdigit():
                    continue
                
                # 한 글자 반복 패턴 제외 (예: ㅋㅋㅋ, ㅎㅎㅎ)
                if len(set(word)) == 1 and len(word) > 1:
                    continue
                
                # 특수문자 포함 단어 제외
                import re
                if re.search(r'[^\w\s]', word):
                    continue
                
                # 의미 있는 키워드만 추가
                if len(word) >= min_length:
                    keywords.append(word)
            
            return keywords
            
        except Exception as e:
            print(f"Kiwi 키워드 추출 실패: {e}")
            # Kiwi 실패 시 정규표현식 방법으로 폴백
            return self.extract_korean_keywords_regex(text, min_length)
    
    def extract_korean_keywords_regex(self, text, min_length=2):
        """정규표현식 기반 한국어 키워드 추출 (백업 방법)"""
        if not text:
            return []
        
        try:
            import re
            
            # 한국어 문자만 추출 (완성된 한글 + 영어 + 숫자)
            korean_pattern = r'[가-힣a-zA-Z0-9]+'
            words = re.findall(korean_pattern, text)
            
            # 불용어 제거 및 길이 필터링
            keywords = []
            for word in words:
                # 길이 확인
                if len(word) < min_length:
                    continue
                
                # 숫자만으로 이루어진 단어 제외
                if word.isdigit():
                    continue
                
                # 영어만으로 이루어진 단어는 소문자로 변환
                if word.isalpha() and word.isascii():
                    word = word.lower()
                
                # 불용어 확인
                if word in self.korean_stopwords:
                    continue
                
                keywords.append(word)
            
            return keywords
        except Exception as e:
            print(f"정규표현식 키워드 추출 실패: {e}")
            return []
    
    def extract_korean_keywords(self, text, min_length=2):
        """한국어 키워드 추출 - Kiwi 우선, 실패시 정규표현식"""
        if KIWI_AVAILABLE and self.korean_available:
            return self.extract_korean_keywords_with_kiwi(text, min_length)
        else:
            return self.extract_korean_keywords_regex(text, min_length)
    
    def extract_english_keywords(self, text, min_length=2):
        """영어 키워드 추출"""
        if not text:
            return []
        
        try:
            # NLTK 토크나이저 사용 (punkt_tab 다운로드 완료)
            tokens = word_tokenize(text.lower())
        except Exception as e:
            print(f"NLTK 토크나이저 실패, 간단한 분할 사용: {e}")
            # NLTK 실패 시 간단한 공백 기반 분할 사용
            import re
            tokens = re.findall(r'\b\w+\b', text.lower())
        
        try:
            # 불용어 제거 및 길이 필터링
            keywords = []
            for word in tokens:
                # 기본 조건 확인
                if (len(word) >= min_length 
                    and word not in self.english_stopwords
                    and word.isalpha()
                    and not word.isdigit()):
                    
                    # 추가 품질 필터링
                    # 한 글자 반복 패턴 제외 (예: aaaa, bbbb)
                    if len(set(word)) == 1 and len(word) > 2:
                        continue
                    
                    # 너무 짧은 의미없는 단어 제외
                    if len(word) == 1:
                        continue
                    
                    # URL 관련 단어 제외
                    if word in ['http', 'https', 'www', 'com', 'org', 'net']:
                        continue
                    
                    keywords.append(word)
            
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
    
    @st.cache_data(ttl=300)  # 5분 캐시
    def extract_keywords_from_dataframe(_self, df, text_columns=['title', 'description'], min_length=None):
        """DataFrame에서 키워드 추출 (캐시 적용)"""
        if min_length is None:
            min_length = config.MIN_WORD_LENGTH
            
        all_keywords = []
        
        for _, row in df.iterrows():
            for column in text_columns:
                if column in row and row[column]:
                    keywords = _self.extract_keywords_from_text(row[column], min_length=min_length)
                    all_keywords.extend(keywords)
            
            # 태그 처리
            if 'tags' in row and row['tags']:
                if isinstance(row['tags'], list):
                    # 리스트인 경우 (기존 로직 유지)
                    for tag in row['tags']:
                        tag_keywords = _self.extract_keywords_from_text(tag, min_length=min_length)
                        all_keywords.extend(tag_keywords)
                else:
                    # 문자열인 경우 (쉼표로 구분된 태그들을 분할하여 처리)
                    tags_str = str(row['tags'])
                    if ',' in tags_str:
                        # 쉼표로 구분된 태그들을 분할
                        individual_tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                        for tag in individual_tags:
                            tag_keywords = _self.extract_keywords_from_text(tag, min_length=min_length)
                            all_keywords.extend(tag_keywords)
                    else:
                        # 단일 태그인 경우
                        tag_keywords = _self.extract_keywords_from_text(tags_str, min_length=min_length)
                        all_keywords.extend(tag_keywords)
        
        return all_keywords
    
    def get_keyword_frequency(self, keywords, max_keywords=None):
        """키워드 빈도 계산"""
        if max_keywords is None:
            max_keywords = config.MAX_KEYWORDS
        
        counter = Counter(keywords)
        return dict(counter.most_common(max_keywords))
    
    @st.cache_data(ttl=600)  # 10분 캐시
    def calculate_tfidf_scores(_self, texts, max_features=100):
        """TF-IDF 점수 계산"""
        try:
            # 텍스트 전처리
            processed_texts = []
            for text in texts:
                if text and not pd.isna(text):
                    cleaned = _self.clean_text(str(text))
                    if _self.is_korean(cleaned):
                        keywords = _self.extract_korean_keywords(cleaned)
                    else:
                        keywords = _self.extract_english_keywords(cleaned)
                    processed_texts.append(' '.join(keywords))
                else:
                    processed_texts.append('')
            
            if not processed_texts or all(not text for text in processed_texts):
                return {}
            
            # TF-IDF 벡터라이저
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words=None,  # 이미 전처리에서 제거
                lowercase=False   # 이미 전처리됨
            )
            
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # 평균 TF-IDF 점수 계산
            mean_scores = tfidf_matrix.mean(axis=0).A1
            tfidf_scores = dict(zip(feature_names, mean_scores))
            
            # 점수별 정렬
            return dict(sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            print(f"TF-IDF 계산 실패: {e}")
            return {}
    
    def generate_wordcloud(self, keywords_freq, width=None, height=None):
        """워드 클라우드 생성"""
        if not keywords_freq:
            return None
        
        try:
            if width is None:
                width = config.WORDCLOUD_WIDTH
            if height is None:
                height = config.WORDCLOUD_HEIGHT
            
            # 한글 폰트 설정 (Windows용)
            font_path = None
            try:
                import matplotlib.font_manager as fm
                system_fonts = fm.findSystemFonts()
                korean_fonts = [f for f in system_fonts if 'malgun' in f.lower() or 'nanum' in f.lower()]
                if korean_fonts:
                    font_path = korean_fonts[0]
            except:
                pass
            
            wordcloud = WordCloud(
                width=width,
                height=height,
                background_color=config.WORDCLOUD_BACKGROUND,
                colormap=config.WORDCLOUD_COLORMAP,
                font_path=font_path,
                relative_scaling=0.5,
                min_font_size=10
            ).generate_from_frequencies(keywords_freq)
            
            return wordcloud
            
        except Exception as e:
            print(f"워드 클라우드 생성 실패: {e}")
            return None
    
    def create_keyword_network(self, df, min_length=2, max_keywords=30, min_cooccurrence=2):
        """키워드 네트워크 분석 - 키워드 간 연관성 분석"""
        try:
            # 모든 텍스트에서 키워드 추출
            all_keywords = self.extract_keywords_from_dataframe(df, min_length=min_length)
            
            if not all_keywords:
                return None, None
            
            # 상위 키워드 선별
            keyword_freq = self.get_keyword_frequency(all_keywords, max_keywords=max_keywords)
            top_keywords = list(keyword_freq.keys())
            
            # 공출현 매트릭스 생성
            cooccurrence_matrix = self._calculate_cooccurrence_matrix(df, top_keywords, min_cooccurrence)
            
            # 네트워크 그래프 데이터 생성
            network_data = self._create_network_data(cooccurrence_matrix, keyword_freq)
            
            return network_data, keyword_freq
            
        except Exception as e:
            st.error(f"키워드 네트워크 분석 중 오류 발생: {str(e)}")
            return None, None
    
    def _calculate_cooccurrence_matrix(self, df, keywords, min_cooccurrence=2):
        """키워드 공출현 매트릭스 계산"""
        import pandas as pd
        from collections import defaultdict
        import itertools
        
        # 공출현 카운트 딕셔너리
        cooccurrence = defaultdict(int)
        
        # 각 동영상에 대해 키워드 공출현 계산
        for _, row in df.iterrows():
            # 제목과 설명에서 키워드 찾기
            text = str(row.get('title', '')) + ' ' + str(row.get('description', ''))
            text = text.lower()
            
            # 해당 텍스트에 존재하는 키워드들 찾기
            present_keywords = []
            for keyword in keywords:
                if keyword.lower() in text:
                    present_keywords.append(keyword)
            
            # 키워드 쌍에 대한 공출현 계산
            for keyword1, keyword2 in itertools.combinations(present_keywords, 2):
                # 알파벳 순으로 정렬하여 일관성 유지
                pair = tuple(sorted([keyword1, keyword2]))
                cooccurrence[pair] += 1
        
        # 최소 공출현 횟수 이상인 것만 필터링
        filtered_cooccurrence = {
            pair: count for pair, count in cooccurrence.items() 
            if count >= min_cooccurrence
        }
        
        return filtered_cooccurrence
    
    def _create_network_data(self, cooccurrence_matrix, keyword_freq):
        """네트워크 그래프 데이터 생성"""
        nodes = []
        edges = []
        
        # 노드 데이터 생성 (키워드)
        for keyword, freq in keyword_freq.items():
            nodes.append({
                'id': keyword,
                'label': keyword,
                'size': freq,
                'freq': freq
            })
        
        # 엣지 데이터 생성 (공출현 관계)
        for (keyword1, keyword2), weight in cooccurrence_matrix.items():
            # 두 키워드가 모두 상위 키워드에 포함된 경우만
            if keyword1 in keyword_freq and keyword2 in keyword_freq:
                edges.append({
                    'source': keyword1,
                    'target': keyword2,
                    'weight': weight,
                    'width': min(weight * 2, 10)  # 선 두께 (최대 10)
                })
        
        return {'nodes': nodes, 'edges': edges}
    
    def calculate_keyword_similarity(self, df, keyword1, keyword2):
        """두 키워드 간의 유사도 계산"""
        try:
            # 각 키워드가 포함된 동영상 찾기
            keyword1_videos = set()
            keyword2_videos = set()
            
            for idx, row in df.iterrows():
                text = str(row.get('title', '')) + ' ' + str(row.get('description', ''))
                text = text.lower()
                
                if keyword1.lower() in text:
                    keyword1_videos.add(idx)
                if keyword2.lower() in text:
                    keyword2_videos.add(idx)
            
            # Jaccard 유사도 계산
            intersection = len(keyword1_videos & keyword2_videos)
            union = len(keyword1_videos | keyword2_videos)
            
            if union == 0:
                return 0
            
            similarity = intersection / union
            return similarity
            
        except Exception as e:
            st.error(f"키워드 유사도 계산 중 오류 발생: {str(e)}")
            return 0
    
    def get_keyword_clusters(self, df, min_length=2, max_keywords=20, similarity_threshold=0.3):
        """키워드 클러스터링 - 유사한 키워드들을 그룹화"""
        try:
            # 키워드 추출
            all_keywords = self.extract_keywords_from_dataframe(df, min_length=min_length)
            if not all_keywords:
                return []
            
            # 상위 키워드 선별
            keyword_freq = self.get_keyword_frequency(all_keywords, max_keywords=max_keywords)
            keywords = list(keyword_freq.keys())
            
            # 유사도 매트릭스 계산
            similarity_matrix = {}
            for i, keyword1 in enumerate(keywords):
                for j, keyword2 in enumerate(keywords[i+1:], i+1):
                    similarity = self.calculate_keyword_similarity(df, keyword1, keyword2)
                    similarity_matrix[(keyword1, keyword2)] = similarity
            
            # 간단한 클러스터링 (threshold 기반)
            clusters = []
            used_keywords = set()
            
            for keyword in keywords:
                if keyword in used_keywords:
                    continue
                
                cluster = [keyword]
                used_keywords.add(keyword)
                
                # 유사한 키워드들 찾기
                for other_keyword in keywords:
                    if other_keyword in used_keywords:
                        continue
                    
                    pair = tuple(sorted([keyword, other_keyword]))
                    similarity = similarity_matrix.get(pair, 0)
                    
                    if similarity >= similarity_threshold:
                        cluster.append(other_keyword)
                        used_keywords.add(other_keyword)
                
                if len(cluster) > 1:  # 클러스터에 2개 이상의 키워드가 있는 경우만
                    clusters.append({
                        'keywords': cluster,
                        'size': len(cluster),
                        'avg_freq': sum(keyword_freq.get(k, 0) for k in cluster) / len(cluster)
                    })
            
            # 크기와 평균 빈도순으로 정렬
            clusters.sort(key=lambda x: (x['size'], x['avg_freq']), reverse=True)
            
            return clusters
            
        except Exception as e:
            st.error(f"키워드 클러스터링 중 오류 발생: {str(e)}")
            return [] 