"""
옥수수 러닝크루 러닝 플래너
Oksusu Running Crew - Running Planner App
"""

import streamlit as st
import os
import sys
from datetime import datetime, timedelta, date
from dotenv import load_dotenv

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 환경변수 로드
load_dotenv()

from config.courses import RUNNING_COURSES, get_course_by_id
from config.weather_code import get_weather_summary, SKY_CODE, PTY_CODE
from utils.weather_api import fetch_weather, get_available_dates
from utils.clothing_advisor import (
    get_clothing_recommendation,
    get_clothing_for_course_terrain,
    CATEGORY_ICONS,
)
from utils.pdf_generator import generate_running_report_pdf


# ─────────────────────────────────────────────
#  페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="옥수수 러닝크루 플래너 🌽",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
#  커스텀 CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Noto+Serif+KR:wght@400;700&display=swap');

/* 전체 배경 */
.stApp {
    background: linear-gradient(135deg, #0A1628 0%, #0D2137 50%, #0A1628 100%);
    font-family: 'Noto Sans KR', sans-serif;
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D2B1A 0%, #1B4332 60%, #2D6A4F 100%) !important;
    border-right: 1px solid #40916C;
}
[data-testid="stSidebar"] * {
    color: #D8F3DC !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label,
[data-testid="stSidebar"] .stSlider label {
    color: #95D5B2 !important;
    font-weight: 500;
}

/* 메인 컨테이너 */
.main .block-container {
    padding: 1.5rem 2rem;
}

/* 카드 스타일 */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(149,213,178,0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

/* 날씨 카드 */
.weather-card {
    background: linear-gradient(135deg, rgba(27,67,50,0.8) 0%, rgba(45,106,79,0.6) 100%);
    border: 1px solid #40916C;
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.weather-card::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(149,213,178,0.1) 0%, transparent 70%);
    border-radius: 50%;
}

/* 날씨 수치 */
.weather-temp {
    font-size: 3.5rem;
    font-weight: 900;
    color: #D8F3DC;
    line-height: 1;
}
.weather-label {
    font-size: 1.1rem;
    color: #95D5B2;
    margin-top: 0.3rem;
}

/* 메트릭 카드 */
.metric-row {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.metric-box {
    flex: 1;
    min-width: 100px;
    background: rgba(0,0,0,0.25);
    border-radius: 12px;
    padding: 0.8rem;
    text-align: center;
    border: 1px solid rgba(149,213,178,0.15);
}
.metric-value {
    font-size: 1.3rem;
    font-weight: 700;
    color: #D8F3DC;
}
.metric-label {
    font-size: 0.7rem;
    color: #95D5B2;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* 섹션 헤더 */
.section-header {
    font-size: 1.2rem;
    font-weight: 700;
    color: #95D5B2;
    border-left: 4px solid #40916C;
    padding-left: 0.8rem;
    margin: 1.5rem 0 1rem 0;
}

/* 복장 태그 */
.clothing-tag {
    display: inline-block;
    background: rgba(64,145,108,0.2);
    border: 1px solid rgba(64,145,108,0.4);
    color: #B7E4C7;
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.85rem;
    margin: 0.2rem;
}

/* 팁 박스 */
.tip-box {
    background: rgba(212,160,23,0.15);
    border: 1px solid rgba(212,160,23,0.4);
    border-radius: 12px;
    padding: 1rem;
    color: #FFD166;
    font-size: 0.9rem;
    margin-top: 1rem;
}

/* 추천도 바 */
.score-bar-bg {
    width: 100%;
    height: 10px;
    background: rgba(255,255,255,0.1);
    border-radius: 5px;
    overflow: hidden;
    margin-top: 0.5rem;
}

/* 러닝 설계 카드 */
.plan-card {
    background: rgba(27,67,50,0.4);
    border: 1px solid rgba(64,145,108,0.3);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}

/* 레포트 섹션 */
.report-section {
    background: linear-gradient(135deg, rgba(27,67,50,0.9) 0%, rgba(13,43,26,0.95) 100%);
    border: 2px solid #40916C;
    border-radius: 24px;
    padding: 2.5rem;
    margin-top: 2rem;
    position: relative;
}

/* 사이드바 로고 */
.sidebar-logo {
    text-align: center;
    padding: 1.5rem 0 1rem 0;
    border-bottom: 1px solid rgba(149,213,178,0.3);
    margin-bottom: 1.5rem;
}
.sidebar-logo-title {
    font-size: 1.6rem;
    font-weight: 900;
    color: #D8F3DC;
    line-height: 1.2;
}
.sidebar-logo-sub {
    font-size: 0.8rem;
    color: #95D5B2;
    margin-top: 0.3rem;
}

/* 사이드바 코스 그룹 */
.course-group-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #74C69D !important;
    margin-top: 1rem;
}

/* API 상태 뱃지 */
.api-badge-ok {
    display: inline-block;
    background: rgba(0,200,81,0.2);
    color: #00C851;
    border: 1px solid #00C851;
    border-radius: 20px;
    padding: 0.15rem 0.6rem;
    font-size: 0.75rem;
    font-weight: 600;
}
.api-badge-err {
    display: inline-block;
    background: rgba(213,0,0,0.2);
    color: #FF5252;
    border: 1px solid #FF5252;
    border-radius: 20px;
    padding: 0.15rem 0.6rem;
    font-size: 0.75rem;
    font-weight: 600;
}

/* 페이스 계산기 */
.pace-display {
    font-size: 2rem;
    font-weight: 900;
    color: #95D5B2;
    text-align: center;
}

/* Streamlit 기본 컴포넌트 재스타일 */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(149,213,178,0.3) !important;
    color: #D8F3DC !important;
}
.stDateInput > div > div > input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(149,213,178,0.3) !important;
    color: #D8F3DC !important;
}

/* 사이드바 selectbox 및 dateinput 스타일 (흰색 배경 + 검은색 글자) */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid rgba(149,213,178,0.5) !important;
    color: #000000 !important;
}
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
    color: #000000 !important;
}
[data-testid="stSidebar"] .stDateInput > div > div > input {
    background: #ffffff !important;
    border: 1px solid rgba(149,213,178,0.5) !important;
    color: #000000 !important;
}

/* 드롭다운 메뉴 및 달력 팝업 (흰색 배경에 검은색 글자) */
[data-baseweb="menu"] * {
    color: #000000 !important;
}
[data-baseweb="popover"] * {
    color: #000000 !important;
}
div[role="dialog"] * {
    color: #000000 !important;
}
.stSlider [data-baseweb="slider"] {
    padding-top: 0.5rem;
}
.stButton > button {
    background: linear-gradient(135deg, #2D6A4F, #1B4332) !important;
    color: #D8F3DC !important;
    border: 1px solid #40916C !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #40916C, #2D6A4F) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(64,145,108,0.4) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #D4A017, #B8860B) !important;
    color: #1A1A1A !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.6rem 1.5rem !important;
}
div[data-testid="stMetricValue"] {
    color: #95D5B2 !important;
    font-weight: 700 !important;
}
h1, h2, h3 {
    color: #D8F3DC !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
p, label {
    color: #B7E4C7 !important;
}
.stTextArea textarea {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(149,213,178,0.3) !important;
    color: #D8F3DC !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  API 키 로드
#  우선순위: Streamlit Cloud Secrets → .env 파일
# ─────────────────────────────────────────────
def _get_secret(key: str) -> str:
    """Streamlit Secrets → .env 순서로 API 키를 읽습니다."""
    # 1순위: Streamlit Cloud Secrets (배포 환경)
    try:
        return st.secrets[key]
    except Exception:
        pass
    # 2순위: 로컬 .env 파일
    return os.getenv(key, "")

KMA_API_KEY = _get_secret("KMA_API_KEY")
KAKAO_API_KEY = _get_secret("KAKAO_API_KEY")
KAKAO_JS_KEY = _get_secret("KAKAO_JS_KEY")


# ─────────────────────────────────────────────
#  사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    # 로고
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:3rem; margin-bottom:0.3rem;">🌽</div>
        <div class="sidebar-logo-title">옥수수<br>러닝크루</div>
        <div class="sidebar-logo-sub">Oksusu Running Crew</div>
        <div style="font-size:0.75rem; color:#74C69D; margin-top:0.5rem;">매주 수요일 · 옥수역</div>
    </div>
    """, unsafe_allow_html=True)
    
    # API 상태
    st.markdown("**🔌 API 상태**")
    col_a, col_b = st.columns(2)
    with col_a:
        if KMA_API_KEY and KMA_API_KEY != "여기에_기상청_API_키_입력":
            st.markdown('<span class="api-badge-ok">✓ 기상청</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="api-badge-err">✗ 기상청</span>', unsafe_allow_html=True)
    with col_b:
        if KAKAO_API_KEY and KAKAO_API_KEY != "여기에_카카오_REST_API_키_입력":
            st.markdown('<span class="api-badge-ok">✓ 카카오</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="api-badge-err">✗ 카카오</span>', unsafe_allow_html=True)
    
    if not KMA_API_KEY or KMA_API_KEY == "여기에_기상청_API_키_입력":
        st.warning("`.env` 파일에 `KMA_API_KEY`를 입력하세요.", icon="⚠️")
    
    st.divider()
    
    # ── 코스 선택 ──
    st.markdown("### 🗺️ 러닝 코스 선택")
    
    selected_group = st.selectbox(
        "코스 그룹",
        options=list(RUNNING_COURSES.keys()),
        index=0,
        key="course_group",
    )
    
    courses_in_group = RUNNING_COURSES[selected_group]
    course_options = {
        f"{c['name']} ({c['distance_km']}km) {c['difficulty']}": c
        for c in courses_in_group
    }
    
    selected_course_label = st.selectbox(
        "코스 선택",
        options=list(course_options.keys()),
        key="course_select",
    )
    selected_course = course_options[selected_course_label]
    
    # 코스 미리보기
    st.markdown(f"""
    <div style="background:rgba(0,0,0,0.2);border-radius:10px;padding:0.8rem;margin-top:0.5rem;">
        <div style="color:#95D5B2;font-size:0.8rem;font-weight:600;">📍 {selected_course['start_location']}</div>
        <div style="color:#74C69D;font-size:0.75rem;margin-top:0.3rem;">{selected_course['terrain']} | {selected_course['distance_km']}km</div>
        <div style="color:#D8F3DC;font-size:0.78rem;margin-top:0.4rem;">{selected_course['description'][:60]}...</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ── 날짜 선택 ──
    st.markdown("### 📅 러닝 날짜 선택")
    
    today = datetime.now().date()
    max_date = today + timedelta(days=4)
    
    selected_date = st.date_input(
        "날짜 (최대 5일 이내)",
        value=today,
        min_value=today,
        max_value=max_date,
        key="date_select",
        help="기상청 단기예보는 최대 5일(오늘 포함)까지 제공됩니다.",
    )
    
    st.caption(f"📆 조회 가능: {today.strftime('%m/%d')} ~ {max_date.strftime('%m/%d')}")
    
    st.divider()
    
    # ── 날씨 조회 버튼 ──
    fetch_btn = st.button("🌤 날씨 조회하기", use_container_width=True, type="primary")


# ─────────────────────────────────────────────
#  Session State 초기화
# ─────────────────────────────────────────────
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
if "clothing" not in st.session_state:
    st.session_state.clothing = None
if "weather_summary" not in st.session_state:
    st.session_state.weather_summary = None
if "report_ready" not in st.session_state:
    st.session_state.report_ready = False


# ─────────────────────────────────────────────
#  메인 영역
# ─────────────────────────────────────────────

# 앱 타이틀
st.markdown("""
<div style="text-align:center; padding: 1rem 0 0.5rem 0;">
    <h1 style="font-size:2.2rem; font-weight:900; color:#D8F3DC; margin:0;">
        🌽 옥수수 러닝크루 플래너
    </h1>
    <p style="color:#95D5B2; font-size:1rem; margin-top:0.3rem;">
        코스 선택 → 날씨 확인 → 러닝 설계 → 레포트 발행
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── 날씨 조회 처리 ──
if fetch_btn:
    if not KMA_API_KEY or KMA_API_KEY == "여기에_기상청_API_키_입력":
        st.error("❌ 기상청 API 키가 설정되지 않았습니다. `.env` 파일을 확인하세요.")
    else:
        with st.spinner(f"🌤 {selected_course['name']} 날씨 조회 중..."):
            target_dt = datetime.combine(selected_date, datetime.min.time())
            weather_result = fetch_weather(
                api_key=KMA_API_KEY,
                nx=selected_course["nx"],
                ny=selected_course["ny"],
                target_date=target_dt,
            )
            
            if "error" in weather_result:
                st.error(f"❌ 날씨 조회 실패: {weather_result['error']}")
                st.session_state.weather_data = None
            else:
                st.session_state.weather_data = weather_result
                # 복장 추천 생성
                clothing = get_clothing_recommendation(
                    tmp=weather_result["TMP"],
                    pty=weather_result["PTY"],
                    wsd=weather_result["WSD"],
                    pop=weather_result["POP"],
                )
                clothing = get_clothing_for_course_terrain(
                    selected_course["terrain"], clothing
                )
                st.session_state.clothing = clothing
                # 날씨 종합
                st.session_state.weather_summary = get_weather_summary(
                    sky=weather_result["SKY"],
                    pty=weather_result["PTY"],
                    tmp=weather_result["TMP"],
                    pop=weather_result["POP"],
                    wsd=weather_result["WSD"],
                    reh=weather_result["REH"],
                )
                st.success(f"✅ 날씨 정보를 불러왔습니다!")


# ─── 2단 레이아웃: 날씨 | 코스 정보 ───
col_weather, col_course = st.columns([3, 2])

with col_weather:
    st.markdown('<div class="section-header">🌤 날씨 & 복장 추천</div>', unsafe_allow_html=True)
    
    if st.session_state.weather_data:
        wd = st.session_state.weather_data
        ws = st.session_state.weather_summary
        
        tmp = wd["TMP"]
        tmx = wd["TMX"]
        tmn = wd["TMN"]
        pop = wd["POP"]
        wsd = wd["WSD"]
        reh = wd["REH"]
        sky = wd["SKY"]
        pty = wd["PTY"]
        
        weather_emoji = ws["weather_emoji"]
        weather_label = ws["weather_label"]
        run_recommend = ws["run_recommend"]
        run_color = ws["run_color"]
        run_score = ws["running_score"]
        
        # 날씨 카드
        weekdays_kr = ["월", "화", "수", "목", "금", "토", "일"]
        date_display = f"{selected_date.strftime('%m월 %d일')} ({weekdays_kr[selected_date.weekday()]})"
        
        st.markdown(f"""
        <div class="weather-card">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div style="color:#95D5B2; font-size:0.9rem; margin-bottom:0.3rem;">
                        📅 {date_display} | 📍 {selected_course['name']}
                    </div>
                    <div class="weather-temp">{weather_emoji} {tmp}°C</div>
                    <div class="weather-label">{weather_label}</div>
                    <div style="color:#74C69D; font-size:0.85rem; margin-top:0.3rem;">
                        최고 {tmx}°C / 최저 {tmn}°C | {ws['temp_feel']}
                    </div>
                </div>
                <div style="text-align:center;">
                    <div style="background:rgba(0,0,0,0.3); border-radius:16px; padding:1rem 1.5rem; border: 2px solid {run_color};">
                        <div style="font-size:0.75rem; color:#95D5B2; margin-bottom:0.3rem;">러닝 추천</div>
                        <div style="font-size:1.3rem; font-weight:900; color:{run_color};">{run_recommend}</div>
                        <div style="font-size:0.75rem; color:#74C69D;">{run_score}/100</div>
                    </div>
                </div>
            </div>
            <div class="metric-row">
                <div class="metric-box">
                    <div class="metric-value">🌂 {pop}%</div>
                    <div class="metric-label">강수 확률</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">💨 {wsd}m/s</div>
                    <div class="metric-label">풍속</div>
                </div>
                <div class="metric-box">
                    <div class="metric-value">💧 {reh}%</div>
                    <div class="metric-label">습도</div>
                </div>
            </div>
            <div style="margin-top:0.8rem; font-size:0.8rem; color:#74C69D;">
                ⚡ {ws['wind_level']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 복장 추천
        if st.session_state.clothing:
            st.markdown('<div class="section-header">👕 권장 러닝 복장</div>', unsafe_allow_html=True)
            
            clothing = st.session_state.clothing
            
            # 카테고리별 복장 표시
            for cat, items in clothing.items():
                if cat == "tip":
                    continue
                if not items:
                    continue
                icon = CATEGORY_ICONS.get(cat, "•")
                
                with st.expander(f"{icon} {cat}", expanded=True):
                    tags_html = "".join(
                        f'<span class="clothing-tag">{item}</span>'
                        for item in items
                    )
                    st.markdown(tags_html, unsafe_allow_html=True)
            
            # 팁
            if "tip" in clothing and clothing["tip"]:
                st.markdown(f"""
                <div class="tip-box">
                    💡 <strong>러닝 팁</strong><br>
                    {clothing["tip"]}
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # 날씨 미조회 상태
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:3rem;">
            <div style="font-size:4rem; margin-bottom:1rem;">🌤</div>
            <div style="color:#95D5B2; font-size:1.1rem; font-weight:600;">날씨 정보를 불러오세요</div>
            <div style="color:#74C69D; font-size:0.9rem; margin-top:0.5rem;">
                좌측 사이드바에서 코스와 날짜를 선택한 후<br>
                <strong>🌤 날씨 조회하기</strong> 버튼을 눌러주세요
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_course:
    st.markdown('<div class="section-header">📍 선택된 코스</div>', unsafe_allow_html=True)
    
    # 코스 정보 카드
    highlights_html = "".join(
        f'<span class="clothing-tag">✦ {h}</span>'
        for h in selected_course.get("highlights", [])
    )
    
    st.markdown(f"""
    <div class="glass-card">
        <div style="font-size:1.3rem; font-weight:800; color:#D8F3DC; margin-bottom:0.5rem;">
            {selected_course['name']}
        </div>
        <div style="color:#95D5B2; font-size:0.9rem; margin-bottom:1rem;">
            {selected_course['description']}
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.8rem; margin-bottom:1rem;">
            <div class="metric-box">
                <div class="metric-value">🏃 {selected_course['distance_km']}km</div>
                <div class="metric-label">거리</div>
            </div>
            <div class="metric-box">
                <div class="metric-value">{selected_course['difficulty']}</div>
                <div class="metric-label">난이도</div>
            </div>
            <div class="metric-box">
                <div class="metric-value" style="font-size:0.9rem;">🗺️ {selected_course['terrain']}</div>
                <div class="metric-label">지형</div>
            </div>
            <div class="metric-box">
                <div class="metric-value" style="font-size:0.85rem;">📍 출발</div>
                <div class="metric-label">{selected_course['start_location'][:10]}</div>
            </div>
        </div>
        <div style="margin-bottom:0.5rem; color:#74C69D; font-size:0.8rem;">🌟 코스 하이라이트</div>
        {highlights_html}
    </div>
    """, unsafe_allow_html=True)
    
    # 카카오맵 JS API - 러닝 코스 폴리라인 표시
    import streamlit.components.v1 as components
    import json

    if KAKAO_JS_KEY and KAKAO_JS_KEY != "여기에_카카오_JavaScript_키_입력":
        route_path = selected_course.get("route_path", [])
        center_lat = selected_course["kakao_lat"]
        center_lng = selected_course["kakao_lng"]
        map_level = selected_course.get("map_level", 5)
        course_name = selected_course["name"]
        start_location = selected_course["start_location"]
        distance_km = selected_course["distance_km"]
        path_json = json.dumps(route_path)

        kakao_map_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ background: #0D2B1A; font-family: 'Noto Sans KR', sans-serif; }}
                #map {{ width: 100%; height: 260px; border-radius: 12px; }}
                .map-info {{
                    background: rgba(13,43,26,0.95);
                    border: 1px solid #40916C;
                    border-radius: 0 0 12px 12px;
                    padding: 8px 12px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .map-title {{ color: #95D5B2; font-size: 12px; font-weight: 600; }}
                .map-dist {{ color: #D8F3DC; font-size: 12px; font-weight: 700; }}
                .map-legend {{
                    display: flex; align-items: center; gap: 6px;
                    color: #74C69D; font-size: 11px;
                }}
                .legend-line {{
                    width: 20px; height: 3px;
                    background: linear-gradient(90deg, #40916C, #95D5B2);
                    border-radius: 2px;
                }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <div class="map-info">
                <div>
                    <div class="map-title">📍 {course_name}</div>
                </div>
                <div class="map-legend">
                    <div class="legend-line"></div>
                    <span>러닝 코스</span>
                </div>
                <div class="map-dist">🏃 {distance_km}km</div>
            </div>
            <script type="text/javascript"
                src="//dapi.kakao.com/v2/maps/sdk.js?appkey={KAKAO_JS_KEY}">
            </script>
            <script>
                var routeCoords = {path_json};
                var mapContainer = document.getElementById('map');
                var mapOption = {{
                    center: new kakao.maps.LatLng({center_lat}, {center_lng}),
                    level: {map_level}
                }};
                var map = new kakao.maps.Map(mapContainer, mapOption);

                // 폴리라인 경로 좌표 변환
                var linePath = routeCoords.map(function(coord) {{
                    return new kakao.maps.LatLng(coord[0], coord[1]);
                }});

                // 러닝 코스 폴리라인 (메인)
                var polyline = new kakao.maps.Polyline({{
                    path: linePath,
                    strokeWeight: 5,
                    strokeColor: '#40916C',
                    strokeOpacity: 0.9,
                    strokeStyle: 'solid'
                }});
                polyline.setMap(map);

                // 외곽선 (가독성 향상)
                var polylineOuter = new kakao.maps.Polyline({{
                    path: linePath,
                    strokeWeight: 9,
                    strokeColor: '#1B4332',
                    strokeOpacity: 0.5,
                    strokeStyle: 'solid'
                }});
                polylineOuter.setMap(map);
                polyline.setMap(map); // 메인 선을 위에

                // 출발점 마커
                if (linePath.length > 0) {{
                    var startMarkerImage = new kakao.maps.MarkerImage(
                        'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/red_b.png',
                        new kakao.maps.Size(50, 45),
                        {{ offset: new kakao.maps.Point(15, 43) }}
                    );
                    var startMarker = new kakao.maps.Marker({{
                        position: linePath[0],
                        map: map,
                        title: '출발점: {start_location}'
                    }});

                    // 출발 인포윈도우
                    var startInfo = new kakao.maps.InfoWindow({{
                        content: '<div style="padding:5px 8px;font-size:11px;font-weight:600;color:#1B4332;white-space:nowrap;">🏁 출발 · {start_location}</div>',
                        removable: false
                    }});
                    startInfo.open(map, startMarker);
                }}

                // 종료점 마커 (출발점과 다를 경우)
                if (linePath.length > 1) {{
                    var endPos = linePath[linePath.length - 1];
                    var endMarker = new kakao.maps.Marker({{
                        position: endPos,
                        map: map,
                        title: '도착점'
                    }});
                }}

                // 지도 타입 컨트롤
                var mapTypeControl = new kakao.maps.MapTypeControl();
                map.addControl(mapTypeControl, kakao.maps.ControlPosition.TOPRIGHT);

                // 줌 컨트롤
                var zoomControl = new kakao.maps.ZoomControl();
                map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);
            </script>
        </body>
        </html>
        """
        components.html(kakao_map_html, height=300)
        _kakao_url = f"https://map.kakao.com/?map_type=TYPE_MAP&q={selected_course['start_location']}&wx={selected_course['kakao_lng']}&wy={selected_course['kakao_lat']}&zoom=4"
        st.markdown(
            f"""
            <div style="
                text-shadow: 
                    -1.5px -1.5px 0 #ffffff,  
                     1.5px -1.5px 0 #ffffff,
                    -1.5px  1.5px 0 #ffffff,
                     1.5px  1.5px 0 #ffffff;
                color: #000000;
                font-size: 0.85rem;
                font-weight: 700;
                margin-top: 0.3rem;
                margin-bottom: 0.8rem;
            ">
                🗺️ <a href="{_kakao_url}" target="_blank" style="color: #000000; text-decoration: underline;">카카오맵에서 크게 보기</a> | 초록선: 러닝 코스 경로
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        _kakao_url = f"https://map.kakao.com/?map_type=TYPE_MAP&q={selected_course['start_location']}&wx={selected_course['kakao_lng']}&wy={selected_course['kakao_lat']}&zoom=4"
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.2);border-radius:10px;padding:1.2rem;text-align:center;color:#74C69D;font-size:0.85rem;">
            🗺️ <strong>.env</strong>에 <code>KAKAO_JS_KEY</code> 입력 시 코스 지도가 표시됩니다<br>
            <a href="{_kakao_url}" target="_blank" style="color:#95D5B2;margin-top:6px;display:inline-block;">📍 카카오맵에서 보기 →</a>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  러닝 설계 섹션
# ─────────────────────────────────────────────
st.divider()
st.markdown('<div class="section-header">🏃 러닝 설계</div>', unsafe_allow_html=True)

# 러닝 타입 설명
RUNNING_TYPES = {
    "이지런 (Easy Run)": {
        "desc": "편안한 대화 가능 페이스로 달리는 회복 위주의 러닝. 전체 러닝 훈련의 70~80%.",
        "icon": "🟢",
        "zone": "Zone 1-2",
    },
    "페이스런 (Pace Run)": {
        "desc": "목표 레이스 페이스로 달리는 훈련. 심폐 능력과 페이스 감각을 키웁니다.",
        "icon": "🔵",
        "zone": "Zone 3",
    },
    "빌드업 러닝 (Build-up)": {
        "desc": "처음에 천천히 시작해서 점차 페이스를 올리는 훈련. 속도 적응 능력 향상.",
        "icon": "🟡",
        "zone": "Zone 2→4",
    },
    "인터벌 러닝 (Interval)": {
        "desc": "빠른 구간과 회복 구간을 반복하는 고강도 훈련. VO2max 향상에 효과적.",
        "icon": "🔴",
        "zone": "Zone 4-5",
    },
    "템포런 (Tempo Run)": {
        "desc": "약간 불편한 페이스(젖산 역치)를 유지하는 훈련. 지속 주행 능력 향상.",
        "icon": "🟠",
        "zone": "Zone 3-4",
    },
    "장거리 LSD (Long Slow Distance)": {
        "desc": "느린 페이스로 장거리를 달리는 훈련. 지구력과 지방 연소 능력을 키웁니다.",
        "icon": "🟣",
        "zone": "Zone 1-2",
    },
    "힐 리피트 (Hill Repeat)": {
        "desc": "오르막길을 반복해서 달리는 훈련. 근력과 파워를 강화합니다.",
        "icon": "⛰️",
        "zone": "Zone 4-5",
    },
    "파트렉 (Fartlek)": {
        "desc": "자유롭게 속도를 변주하는 훈련. 놀이처럼 즐기며 다양한 페이스를 경험합니다.",
        "icon": "🎲",
        "zone": "혼합",
    },
    "회복 런 (Recovery Run)": {
        "desc": "고강도 훈련 다음 날 가볍게 달리는 회복 러닝. 젖산 제거 및 혈류 촉진.",
        "icon": "💚",
        "zone": "Zone 1",
    },
}

col_type, col_type_info = st.columns([2, 3])

with col_type:
    selected_run_type = st.selectbox(
        "러닝 타입",
        options=list(RUNNING_TYPES.keys()),
        key="run_type",
    )

with col_type_info:
    type_info = RUNNING_TYPES[selected_run_type]
    st.markdown(f"""
    <div class="plan-card" style="margin-top:1.5rem;">
        <span style="font-size:1.1rem;">{type_info['icon']}</span>
        <span style="color:#95D5B2; font-size:0.9rem; font-weight:600; margin-left:0.3rem;">{type_info['zone']}</span>
        <div style="color:#D8F3DC; font-size:0.85rem; margin-top:0.4rem;">{type_info['desc']}</div>
    </div>
    """, unsafe_allow_html=True)

# 거리 & 페이스 설정
col_dist, col_pace = st.columns(2)

with col_dist:
    st.markdown("**목표 거리 (km)**")
    target_distance = st.slider(
        "거리",
        min_value=1.0,
        max_value=42.195,
        value=float(selected_course["distance_km"]),
        step=0.5,
        format="%.1f km",
        key="target_dist",
        label_visibility="collapsed",
    )

with col_pace:
    st.markdown("**목표 페이스 (분/km)**")
    col_pm, col_ps = st.columns(2)
    with col_pm:
        pace_min = st.number_input("분", min_value=3, max_value=10, value=5, step=1, key="pace_min")
    with col_ps:
        pace_sec = st.number_input("초", min_value=0, max_value=59, value=30, step=5, key="pace_sec")

# 예상 소요 시간 자동 계산
total_seconds = int(target_distance * (pace_min * 60 + pace_sec))
total_min = total_seconds // 60
hours = total_min // 60
minutes = total_min % 60
secs = total_seconds % 60

# 계산 표시
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("🏃 목표 거리", f"{target_distance:.1f} km")
with col_m2:
    st.metric("⏱️ 목표 페이스", f"{pace_min}'{pace_sec:02d}\"/km")
with col_m3:
    if hours > 0:
        duration_display = f"{hours}시간 {minutes}분 {secs:02d}초"
    else:
        duration_display = f"{minutes}분 {secs:02d}초"
    st.metric("🕐 예상 소요 시간", duration_display)

# ─── 러닝 타입별 세부 설정 ───
extra_settings = {}

if "인터벌" in selected_run_type:
    st.markdown('<div class="section-header" style="font-size:1rem;">⚡ 인터벌 세부 설정</div>', unsafe_allow_html=True)
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        interval_repeats = st.number_input("반복 횟수", min_value=1, max_value=20, value=6, step=1, key="iv_rep")
        extra_settings["interval_repeats"] = interval_repeats
    with col_i2:
        fast_dist = st.selectbox("인터벌 구간", [200, 400, 600, 800, 1000, 1200], index=1, key="iv_fast_dist")
        extra_settings["fast_dist"] = fast_dist
        fast_pace_min = st.number_input("인터벌 페이스 (분)", min_value=2, max_value=6, value=4, key="iv_fp_min")
        fast_pace_sec = st.number_input("인터벌 페이스 (초)", min_value=0, max_value=59, value=0, step=5, key="iv_fp_sec")
        extra_settings["fast_pace"] = f"{fast_pace_min}'{fast_pace_sec:02d}\""
    with col_i3:
        recovery_dist = st.selectbox("회복 구간", [100, 200, 400, 600], index=1, key="iv_rec_dist")
        extra_settings["recovery_dist"] = recovery_dist
        rec_pace_min = st.number_input("회복 페이스 (분)", min_value=4, max_value=9, value=6, key="iv_rp_min")
        rec_pace_sec = st.number_input("회복 페이스 (초)", min_value=0, max_value=59, value=0, step=5, key="iv_rp_sec")
        extra_settings["recovery_pace"] = f"{rec_pace_min}'{rec_pace_sec:02d}\""
    
    # 인터벌 요약
    total_iv_dist = (fast_dist + recovery_dist) * interval_repeats / 1000
    st.info(f"📊 인터벌 총 거리: 약 {total_iv_dist:.1f}km | {interval_repeats}세트 × ({fast_dist}m 빠르게 + {recovery_dist}m 회복)")

elif "빌드업" in selected_run_type:
    st.markdown('<div class="section-header" style="font-size:1rem;">📈 빌드업 세부 설정</div>', unsafe_allow_html=True)
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("**시작 페이스 (처음)**")
        bu_start_min = st.number_input("시작 분", min_value=4, max_value=10, value=6, key="bu_sm")
        bu_start_sec = st.number_input("시작 초", min_value=0, max_value=59, value=30, step=5, key="bu_ss")
        extra_settings["buildup_start_pace"] = f"{bu_start_min}'{bu_start_sec:02d}\""
    with col_b2:
        st.markdown("**종료 페이스 (마지막)**")
        bu_end_min = st.number_input("종료 분", min_value=3, max_value=8, value=4, key="bu_em")
        bu_end_sec = st.number_input("종료 초", min_value=0, max_value=59, value=30, step=5, key="bu_es")
        extra_settings["buildup_end_pace"] = f"{bu_end_min}'{bu_end_sec:02d}\""
    
    st.info(f"📈 빌드업: {bu_start_min}'{bu_start_sec:02d}\"  →  {bu_end_min}'{bu_end_sec:02d}\"/km로 점점 빠르게")

elif "힐 리피트" in selected_run_type:
    st.markdown('<div class="section-header" style="font-size:1rem;">⛰️ 힐 리피트 세부 설정</div>', unsafe_allow_html=True)
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        hill_reps = st.number_input("반복 횟수", min_value=3, max_value=15, value=6, key="hill_rep")
        extra_settings["hill_repeats"] = hill_reps
    with col_h2:
        hill_length = st.selectbox("오르막 길이", ["100m", "200m", "300m", "400m"], index=1, key="hill_len")
        extra_settings["hill_length"] = hill_length
    st.info(f"⛰️ {hill_reps}회 × {hill_length} 언덕 반복")

# 메모
st.markdown("**📝 러닝 메모 (선택)**")
memo = st.text_area(
    "오늘의 목표, 컨디션, 특이사항 등을 자유롭게 입력하세요",
    placeholder="예) 오늘은 페이스보다 즐기는 것에 집중. 중간에 물 보충 필수.",
    max_chars=300,
    key="run_memo",
    label_visibility="collapsed",
)


# ─────────────────────────────────────────────
#  레포트 생성 & 다운로드
# ─────────────────────────────────────────────
st.divider()

st.markdown("""
<div style="text-align:center; margin-bottom:1.5rem;">
    <div style="font-size:1.5rem; font-weight:800; color:#D8F3DC;">📋 러닝 레포트 발행</div>
    <div style="color:#95D5B2; font-size:0.9rem; margin-top:0.3rem;">
        모든 설정을 종합한 러닝 레포트를 PDF로 저장하세요
    </div>
</div>
""", unsafe_allow_html=True)

col_rpt1, col_rpt2, col_rpt3 = st.columns([1, 2, 1])

with col_rpt2:
    # 레포트 미리보기 (인포 박스)
    if st.session_state.weather_data:
        wd = st.session_state.weather_data
        ws = st.session_state.weather_summary
        
        # PDF 생성
        running_plan_data = {
            "type": selected_run_type,
            "distance_km": target_distance,
            "pace_min": pace_min,
            "pace_sec": pace_sec,
            "memo": memo,
            "run_score": ws["running_score"],
            **extra_settings,
        }
        
        try:
            pdf_buffer = generate_running_report_pdf(
                course=selected_course,
                selected_date=datetime.combine(selected_date, datetime.min.time()),
                weather_data=wd,
                clothing=st.session_state.clothing or {},
                running_plan=running_plan_data,
            )
            
            file_date = selected_date.strftime("%Y%m%d")
            file_name = f"옥수수러닝크루_레포트_{file_date}.pdf"
            
            st.download_button(
                label="📥 PDF 레포트 다운로드",
                data=pdf_buffer,
                file_name=file_name,
                mime="application/pdf",
                use_container_width=True,
            )
            
            # 레포트 요약 미리보기
            st.markdown(f"""
            <div class="report-section">
                <div style="text-align:center; margin-bottom:1.5rem;">
                    <div style="font-size:1.8rem; font-weight:900; color:#D8F3DC;">🌽 옥수수 러닝크루</div>
                    <div style="color:#95D5B2; font-size:0.85rem;">러닝 플랜 레포트</div>
                </div>
                
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; margin-bottom:1rem;">
                    <div>
                        <div style="color:#74C69D; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;">코스</div>
                        <div style="color:#D8F3DC; font-weight:700;">{selected_course['name']}</div>
                    </div>
                    <div>
                        <div style="color:#74C69D; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;">날짜</div>
                        <div style="color:#D8F3DC; font-weight:700;">{selected_date.strftime('%Y.%m.%d')}</div>
                    </div>
                    <div>
                        <div style="color:#74C69D; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;">날씨</div>
                        <div style="color:#D8F3DC; font-weight:700;">{ws['weather_emoji']} {ws['weather_label']} {wd['TMP']}°C</div>
                    </div>
                    <div>
                        <div style="color:#74C69D; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;">러닝 추천</div>
                        <div style="color:{ws['run_color']}; font-weight:700;">{ws['run_recommend']}</div>
                    </div>
                    <div>
                        <div style="color:#74C69D; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;">거리/페이스</div>
                        <div style="color:#D8F3DC; font-weight:700;">{target_distance:.1f}km @ {pace_min}'{pace_sec:02d}\"</div>
                    </div>
                    <div>
                        <div style="color:#74C69D; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;">예상 시간</div>
                        <div style="color:#D8F3DC; font-weight:700;">{duration_display}</div>
                    </div>
                </div>
                
                <div style="text-align:right; margin-top:1.5rem; padding-top:1rem; border-top:1px solid rgba(149,213,178,0.2);">
                    <div style="font-style:italic; font-size:1.1rem; color:#40916C; font-weight:700;">Oksusu Running Crew</div>
                    <div style="font-size:0.8rem; color:#2D6A4F;">~ 옥수수 러닝크루 ~  🌽</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 스크린샷 안내
            st.markdown("""
            <div style="text-align:center; margin-top:1rem; color:#74C69D; font-size:0.8rem;">
                💡 스크린샷: <strong>Ctrl+Shift+S</strong> (Windows) | <strong>Cmd+Shift+4</strong> (Mac)
            </div>
            """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"PDF 생성 오류: {str(e)}")
            st.info("ReportLab이 설치되었는지 확인하세요: `pip install reportlab`")
    
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:2rem;">
            <div style="font-size:3rem; margin-bottom:0.8rem;">📋</div>
            <div style="color:#95D5B2; font-weight:600;">날씨 조회 후 레포트를 발행할 수 있습니다</div>
            <div style="color:#74C69D; font-size:0.85rem; margin-top:0.5rem;">
                사이드바에서 날씨를 조회하면 PDF 다운로드가 활성화됩니다
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  하단 푸터
# ─────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; padding:1.5rem 0; color:#2D6A4F; font-size:0.8rem;">
    <div style="font-size:1.5rem; margin-bottom:0.5rem;">🌽</div>
    <div>옥수수 러닝크루 플래너 · 매주 수요일 · 옥수역</div>
    <div style="margin-top:0.3rem;">날씨 데이터: 기상청 단기예보 API · 지도: 카카오맵</div>
</div>
""", unsafe_allow_html=True)
