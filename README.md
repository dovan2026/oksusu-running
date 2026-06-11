# 🌽 옥수수 러닝크루 플래너

> **매주 수요일, 옥수역에서 달립니다.**  
> Oksusu Running Crew — 옥수나들목 기반 러닝크루를 위한 날씨 기반 러닝 플래너 앱

[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![기상청 API](https://img.shields.io/badge/기상청-단기예보_API-0066CC)](https://www.data.go.kr)
[![카카오 API](https://img.shields.io/badge/카카오-REST_API-FFCD00?logoColor=black)](https://developers.kakao.com)

---

## 📱 주요 기능

| 기능 | 설명 |
|------|------|
| 🗺️ **러닝 코스 선택** | 🏠 홈코스(옥수 기반 3개) + 📍 서울 전체 12개 코스 |
| 🌤 **날씨 조회** | 기상청 단기예보 API — 오늘부터 최대 5일 후까지 |
| 👕 **복장 추천** | 기온·강수·바람·지형을 고려한 상세 러닝 복장 가이드 |
| 🏃 **러닝 설계** | 9가지 러닝 타입 + 페이스/거리/예상 시간 자동 계산 |
| 📥 **PDF 레포트** | A4 레포트 자동 생성 + 옥수수 러닝크루 사인 |
| 🗺️ **카카오맵** | 코스 출발점 지도 임베딩 |

---

## 🚀 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/<your-username>/oksusu-running.git
cd oksusu-running
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. API 키 설정

`.env.example`을 복사해 `.env` 파일을 만들고 API 키를 입력합니다.

```bash
cp .env.example .env   # Mac/Linux
copy .env.example .env  # Windows
```

```env
KMA_API_KEY=여기에_기상청_API_키_입력
KAKAO_API_KEY=여기에_카카오_REST_API_키_입력
```

> ⚠️ `.env` 파일은 `.gitignore`에 포함되어 있어 GitHub에 올라가지 않습니다.

### 4. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 **http://localhost:8501** 로 접속합니다.

---

## 🔑 API 키 발급 방법

### 기상청 단기예보 API
1. [공공데이터포털](https://www.data.go.kr) 접속 후 로그인
2. `기상청_단기예보 조회서비스` 검색
3. **[활용신청]** 클릭 → 승인 후 **서비스 키(Decoding)** 복사

### 카카오 REST API
1. [카카오 개발자 콘솔](https://developers.kakao.com) 접속 후 로그인
2. **[내 애플리케이션]** → **[애플리케이션 추가하기]**
3. **[앱 키]** 탭 → **REST API 키** 복사

---

## 📁 프로젝트 구조

```
oksusu_running/
├── app.py                   # 🏠 Streamlit 메인 앱
├── requirements.txt         # 📦 패키지 목록
├── .env.example             # 🔑 API 키 예시 (이것을 복사해서 .env 생성)
├── .gitignore               # 🚫 Git 제외 파일 목록
│
├── config/
│   ├── courses.py           # 🗺️ 서울 러닝 코스 데이터 (15개, nx/ny 좌표 포함)
│   └── weather_code.py      # 🌤 기상청 날씨 코드 매핑 & 러닝 추천도 계산
│
└── utils/
    ├── weather_api.py       # 📡 기상청 단기예보 API 호출
    ├── clothing_advisor.py  # 👕 날씨 → 복장 추천 엔진
    └── pdf_generator.py     # 📄 ReportLab PDF 레포트 생성
```

---

## 🏃 지원하는 러닝 타입

| 타입 | 설명 | 강도 |
|------|------|------|
| 🟢 이지런 | 편안한 대화 가능 페이스 | Zone 1-2 |
| 🔵 페이스런 | 목표 레이스 페이스 훈련 | Zone 3 |
| 🟡 빌드업 | 점진적 페이스 상승 | Zone 2→4 |
| 🔴 인터벌 | 빠른 구간 + 회복 반복 | Zone 4-5 |
| 🟠 템포런 | 젖산 역치 페이스 유지 | Zone 3-4 |
| 🟣 장거리 LSD | 느린 페이스로 장거리 | Zone 1-2 |
| ⛰️ 힐 리피트 | 언덕 반복 주행 | Zone 4-5 |
| 🎲 파트렉 | 자유 속도 변주 | 혼합 |
| 💚 회복 런 | 고강도 훈련 후 회복 | Zone 1 |

---

## 🗺️ 포함된 러닝 코스 (15개)

### 🏠 홈코스 (옥수 기반)
- 옥수-응봉산 코스 (5km, ⭐⭐)
- 옥수-한강 코스 (8km, ⭐)
- 옥수-성수-서울숲 코스 (7km, ⭐)

### 📍 서울 전체 코스
- 반포 한강 순환 / 여의도 한강 순환 / 뚝섬 한강 롱런 / 잠실 롱런
- 올림픽공원 호반길 / 올림픽공원 전체
- 남산 북측순환로 / 남산 전체 순환
- 북한산 둘레길 / 북한산성 코스
- 청계천 / 서울숲 / 광화문-경복궁 / 북악산 트레일

---

## 🛠️ 기술 스택

- **프레임워크**: [Streamlit](https://streamlit.io)
- **날씨 API**: [기상청 단기예보 OpenAPI](https://www.data.go.kr)
- **지도 API**: [카카오 REST API](https://developers.kakao.com)
- **PDF 생성**: [ReportLab](https://www.reportlab.com)
- **환경변수**: [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 📝 라이선스

MIT License — 자유롭게 사용하세요 🌽

---

<div align="center">
  <strong>🌽 옥수수 러닝크루 | Oksusu Running Crew</strong><br>
  <em>매주 수요일, 옥수역에서 달립니다</em>
</div>
