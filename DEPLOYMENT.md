# 🚀 Streamlit Cloud 배포 가이드

## 📋 배포 전 준비사항

### 1. GitHub 저장소 준비
- 코드를 GitHub 저장소에 업로드
- `.env` 파일은 업로드하지 않음 (이미 .gitignore에 포함됨)
- 모든 변경사항 커밋 및 푸시

### 2. YouTube API 키 준비
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. "API 및 서비스" > "라이브러리"에서 "YouTube Data API v3" 활성화
4. "API 및 서비스" > "사용자 인증 정보"에서 API 키 생성
5. API 키 복사 (나중에 Streamlit Cloud에서 사용)

## 🌐 Streamlit Cloud 배포 단계

### 1. Streamlit Cloud 계정 생성
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭

### 2. 앱 설정
1. **Repository**: 업로드한 GitHub 저장소 선택
2. **Branch**: `main` 또는 `master`
3. **Main file path**: `app.py`
4. **App URL**: 원하는 URL 설정 (예: `youtube-trend-analyzer`)

### 3. Secrets 설정 (중요!)
1. 앱 생성 후 "App settings" 클릭
2. "Secrets" 탭 선택
3. 다음 내용 입력:
```toml
YOUTUBE_API_KEY = "실제_유튜브_API_키_입력"
```
4. "Save" 클릭

### 4. 배포 완료
- 자동으로 앱이 빌드되고 배포됩니다
- 빌드 로그에서 오류가 없는지 확인
- 배포 완료 후 제공된 URL로 접속

## ⚠️ 주의사항

### 보안
- **절대 API 키를 코드에 직접 포함하지 마세요**
- **실제 .env 파일을 GitHub에 업로드하지 마세요**
- **Streamlit Secrets만 사용하여 API 키 관리**

### 성능
- 무료 계정은 리소스 제한이 있습니다
- 많은 사용자가 동시 접속시 속도가 느려질 수 있습니다
- 필요시 Streamlit Cloud Pro 고려

### API 할당량
- YouTube API는 일일 할당량이 있습니다 (기본 10,000 units)
- 많은 사용자가 사용시 할당량 초과 가능
- Google Cloud Console에서 할당량 모니터링 권장

## 🔧 문제 해결

### 배포 실패시
1. 빌드 로그 확인
2. requirements.txt의 라이브러리 버전 호환성 확인
3. API 키가 Secrets에 올바르게 설정되었는지 확인

### 앱 실행 오류시
1. API 키가 유효한지 확인
2. YouTube Data API v3가 활성화되었는지 확인
3. Streamlit Cloud 로그 확인

## 📞 지원

배포 관련 문제가 있을 경우:
- [Streamlit Community Forum](https://discuss.streamlit.io/)
- [Streamlit Documentation](https://docs.streamlit.io/streamlit-cloud)

## 🎯 배포 후 확인사항

배포 완료 후 다음 기능들이 정상 작동하는지 확인:
- [ ] 사이드바 설정 변경
- [ ] 데이터 수집 (API 연결 확인)
- [ ] 키워드 분석 및 시각화
- [ ] 모든 탭 정상 작동
- [ ] 워드클라우드 생성
- [ ] 채널 분석 기능
- [ ] 네트워크 분석 기능

성공적인 배포를 위해 이 가이드를 차근차근 따라해주세요! 🚀 