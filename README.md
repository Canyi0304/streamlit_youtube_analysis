# YouTube 인기 동영상 Streamlit 앱

간단한 YouTube Data API v3를 사용해 인기 동영상을 보여주는 Streamlit 앱입니다.

## 기능
- 한 페이지에 30개 인기 동영상 리스트 표시 (지역 기본값: KR)
- 썸네일, 제목(YouTube 링크), 채널명, 조회수, 좋아요 수, 댓글 수, 업로드 날짜 표시
- 동영상 길이(재생시간) 표시
- 새로고침 버튼
- 에러 처리 (API 오류, 키 미설정 등)

## 파일 구조
```
20250916_class/
├─ streamlit_app.py       # 메인 앱
├─ requirements.txt       # Python 의존성 목록
├─ .env.example           # 환경변수 예시 파일
├─ .env                   # (개발자 로컬) 실제 API 키 저장 - git에 커밋 금지
└─ README.md
```

## 사전 준비
1. Google Cloud Console에서 YouTube Data API v3 활성화 및 API 키 발급
   - https://console.cloud.google.com/
2. `.env` 파일 생성
   - `.env.example`를 복사하여 `.env` 작성
   - `YOUTUBE_API_KEY`와(옵션) `REGION_CODE` 설정

예시:
```
YOUTUBE_API_KEY=YOUR_API_KEY
REGION_CODE=KR
```

## 설치 및 실행
의존성 설치:
```
pip install -r requirements.txt
```

Anaconda(base) 파이썬을 사용한다면(권장):
```
/opt/anaconda3/bin/python -m pip install -r requirements.txt
```

앱 실행:
```
streamlit run streamlit_app.py
```

Anaconda 해석기로 실행(환경 일치 보장):
```
/opt/anaconda3/bin/python -m streamlit run streamlit_app.py
```

실행 후 브라우저에서 다음 주소로 접속:
- http://localhost:8501

## 배포(Secrets) 및 환경변수
이 앱은 설정을 다음 순서로 로드합니다.

1) `st.secrets` (배포 환경용)
2) `.env` (로컬 개발용)

배포 시에는 `.env` 내용을 `.streamlit/secrets.toml`로 옮기세요.

예시 템플릿: `.streamlit/secrets.toml.example`를 복사하여 `.streamlit/secrets.toml` 생성
```toml
YOUTUBE_API_KEY = "YOUR_API_KEY"
REGION_CODE = "KR"
```

로컬 개발 시에는 `.env` 사용:
```
YOUTUBE_API_KEY=YOUR_API_KEY
REGION_CODE=KR
```

코드에서의 로드 우선순위는 `st.secrets`가 먼저이며, 없으면 `.env`를 사용합니다.

## 환경 변수 설명
- `YOUTUBE_API_KEY`: YouTube Data API v3 키
- `REGION_CODE`(선택): ISO 3166-1 alpha-2 국가 코드. 기본값 `KR`

## 트러블슈팅
- ModuleNotFoundError: No module named 'googleapiclient'
  - Streamlit이 사용하는 파이썬과 패키지를 설치한 파이썬이 다른 경우 발생합니다.
  - 해결: 위의 “Anaconda 해석기로 실행/설치” 명령을 사용하여 동일 해석기(`/opt/anaconda3/bin/python`)로 설치/실행하세요.

- API 키 오류 또는 미설정
  - 앱 상단에 경고가 표시됩니다. `.env`에 `YOUTUBE_API_KEY`를 설정하고 다시 실행하세요.

- API 쿼터 초과
  - Google Cloud Console에서 쿼터 사용량을 확인하거나, 트래픽을 줄이세요.

## 보안
- `.env` 파일에는 민감한 키가 포함되므로 절대 저장소에 커밋하지 마세요.
- 공유가 필요한 경우 `.env.example`만 배포하세요.

## 라이선스
- 목적에 맞게 자유롭게 수정/사용하세요.
