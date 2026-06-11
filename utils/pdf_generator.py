"""
PDF 레포트 생성 모듈 (ReportLab 기반)
- A4 사이즈 러닝 레포트
- 한글 지원 (NanumGothic 또는 시스템 폰트)
- 우측 하단 옥수수 러닝크루 필기체 사인
"""

import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle


# 폰트 등록 (한글 지원)
def register_fonts():
    """시스템에 설치된 한글 폰트를 등록합니다."""
    font_registered = False
    
    # 로컬 fonts 폴더 절대 경로 계산
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_regular = os.path.join(base_dir, "fonts", "NanumGothic.ttf")
    local_bold = os.path.join(base_dir, "fonts", "NanumGothic-Bold.ttf")
    
    # Windows 한글 폰트 경로들 + 로컬 프로젝트 폰트 최우선 적용
    font_candidates = [
        (local_regular, "NanumGothic"),
        ("C:/Windows/Fonts/malgun.ttf", "MalgunGothic"),
        ("C:/Windows/Fonts/malgunbd.ttf", "MalgunGothicBold"),
        ("C:/Windows/Fonts/NanumGothic.ttf", "NanumGothic"),
        ("C:/Windows/Fonts/gulim.ttc", "Gulim"),
    ]
    
    main_font = "Helvetica"
    bold_font = "Helvetica-Bold"
    
    for font_path, font_name in font_candidates:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                if not font_registered:
                    main_font = font_name
                    font_registered = True
            except Exception:
                continue
    
    # 볼드 폰트 탐색
    bold_candidates = [
        (local_bold, "NanumGothicBold"),
        ("C:/Windows/Fonts/malgunbd.ttf", "MalgunGothicBold"),
        ("C:/Windows/Fonts/NanumGothicBold.ttf", "NanumGothicBold"),
    ]
    for font_path, font_name in bold_candidates:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                bold_font = font_name
                break
            except Exception:
                continue
    
    return main_font, bold_font


# 색상 팔레트
COLOR_PRIMARY = colors.HexColor("#1B4332")      # 진한 초록 (옥수수 테마)
COLOR_SECONDARY = colors.HexColor("#40916C")    # 중간 초록
COLOR_ACCENT = colors.HexColor("#95D5B2")       # 연한 초록
COLOR_GOLD = colors.HexColor("#D4A017")         # 골드 (강조)
COLOR_BG = colors.HexColor("#F0F7F4")           # 연한 배경
COLOR_TEXT = colors.HexColor("#1A1A1A")         # 거의 검정
COLOR_GRAY = colors.HexColor("#6C757D")         # 회색
COLOR_WHITE = colors.white


def generate_running_report_pdf(
    course: dict,
    selected_date: datetime,
    weather_data: dict,
    clothing: dict,
    running_plan: dict,
) -> io.BytesIO:
    """
    러닝 레포트 PDF 생성
    
    Args:
        course: 코스 정보 딕셔너리
        selected_date: 선택된 날짜
        weather_data: 날씨 데이터
        clothing: 복장 추천 딕셔너리
        running_plan: 러닝 설계 딕셔너리
    
    Returns:
        PDF BytesIO 객체
    """
    buffer = io.BytesIO()
    
    main_font, bold_font = register_fonts()
    
    # A4 캔버스 생성
    width, height = A4  # 595.27 x 841.89 pt
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # ─── 배경 ───
    c.setFillColor(COLOR_BG)
    c.rect(0, 0, width, height, fill=True, stroke=False)
    
    y = height - 15 * mm
    
    # ─── 헤더 배너 ───
    c.setFillColor(COLOR_PRIMARY)
    c.rect(0, height - 45 * mm, width, 45 * mm, fill=True, stroke=False)
    
    # 로고 텍스트 (옥수수)
    c.setFillColor(COLOR_WHITE)
    c.setFont(bold_font, 28)
    c.drawString(15 * mm, height - 22 * mm, "옥수수 러닝크루")
    
    c.setFont(main_font, 11)
    c.setFillColor(COLOR_ACCENT)
    c.drawString(15 * mm, height - 30 * mm, "Oksusu Running Crew  |  매주 수요일, 옥수역에서 달립니다 🌽")
    
    # 레포트 제목
    c.setFont(bold_font, 14)
    c.setFillColor(COLOR_GOLD)
    report_title = "러닝 플랜 레포트"
    c.drawRightString(width - 15 * mm, height - 22 * mm, report_title)
    
    # 발행일
    c.setFont(main_font, 9)
    c.setFillColor(COLOR_ACCENT)
    issue_date = f"발행: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}"
    c.drawRightString(width - 15 * mm, height - 30 * mm, issue_date)
    
    # 러너 정보 출력
    runner_name = running_plan.get("runner_name", "홍길동")
    runner_gender = running_plan.get("runner_gender", "선택 안함")
    runner_nickname = running_plan.get("runner_nickname", "옥수수러너")
    runner_info = f"러너: {runner_name} ({runner_gender})  |  닉네임: {runner_nickname}"
    c.setFont(bold_font, 9.5)
    c.setFillColor(COLOR_GOLD)
    c.drawRightString(width - 15 * mm, height - 36 * mm, runner_info)
    
    y = height - 52 * mm
    
    # ─── 구분선 ───
    def draw_section_title(title: str, y_pos: float, color=COLOR_PRIMARY) -> float:
        c.setFillColor(color)
        c.rect(10 * mm, y_pos - 6 * mm, width - 20 * mm, 8 * mm, fill=True, stroke=False)
        c.setFillColor(COLOR_WHITE)
        c.setFont(bold_font, 11)
        c.drawString(13 * mm, y_pos - 4 * mm, title)
        return y_pos - 12 * mm
    
    def draw_info_row(label: str, value: str, y_pos: float, label_w=50 * mm) -> float:
        c.setFillColor(COLOR_TEXT)
        c.setFont(bold_font, 9)
        c.drawString(13 * mm, y_pos, label)
        c.setFont(main_font, 9)
        c.drawString(13 * mm + label_w, y_pos, value)
        return y_pos - 6 * mm
    
    # ─── 1. 코스 정보 ───
    y = draw_section_title("📍  선택 코스", y)
    y = draw_info_row("코스명", course.get("name", ""), y)
    y = draw_info_row("거리", f"{course.get('distance_km', 0):.1f} km", y)
    y = draw_info_row("난이도", course.get("difficulty", "").replace("⭐", "★"), y)
    y = draw_info_row("지형", course.get("terrain", ""), y)
    y = draw_info_row("출발 위치", course.get("start_location", ""), y)
    desc = course.get("description", "")
    if desc:
        # 설명 줄바꿈 처리
        c.setFont(main_font, 8.5)
        c.setFillColor(COLOR_GRAY)
        words = desc
        max_w = width - 30 * mm
        c.drawString(13 * mm, y, words[:85])
        if len(words) > 85:
            y -= 5 * mm
            c.drawString(13 * mm, y, words[85:])
        y -= 8 * mm
    else:
        y -= 3 * mm
    
    # ─── 2. 날짜 & 날씨 정보 ───
    y = draw_section_title("🌤  날짜 & 날씨", y, COLOR_SECONDARY)
    
    date_str = selected_date.strftime("%Y년 %m월 %d일 (%A)")
    # 한국어 요일
    weekdays_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    date_str_kr = selected_date.strftime(f"%Y년 %m월 %d일 ({weekdays_kr[selected_date.weekday()]})")
    y = draw_info_row("러닝 날짜", date_str_kr, y)
    
    tmp = weather_data.get("TMP", 0)
    tmx = weather_data.get("TMX", tmp)
    tmn = weather_data.get("TMN", tmp)
    pop = weather_data.get("POP", 0)
    wsd = weather_data.get("WSD", 0)
    reh = weather_data.get("REH", 0)
    sky = weather_data.get("SKY", 1)
    pty = weather_data.get("PTY", 0)
    
    from config.weather_code import SKY_CODE, PTY_CODE
    if pty > 0:
        weather_label = PTY_CODE.get(pty, {}).get("label", "비")
    else:
        weather_label = SKY_CODE.get(sky, {}).get("label", "맑음")
    
    y = draw_info_row("날씨", weather_label, y)
    y = draw_info_row("기온 (예보 시점)", f"{tmp}°C  (최고 {tmx}°C / 최저 {tmn}°C)", y)
    y = draw_info_row("강수 확률", f"{pop}%", y)
    y = draw_info_row("풍속", f"{wsd} m/s", y)
    y = draw_info_row("습도", f"{reh}%", y)
    y -= 3 * mm
    
    # (3. 권장 러닝 복장 섹션 삭제)
    
    # ─── 4. 러닝 설계 ───
    y = draw_section_title("🏃  러닝 설계", y, colors.HexColor("#1B4332"))
    
    run_type = running_plan.get("type", "이지런")
    distance = running_plan.get("distance_km", 5.0)
    pace_min = running_plan.get("pace_min", 5)
    pace_sec = running_plan.get("pace_sec", 30)
    total_sec = int(distance * (pace_min * 60 + pace_sec))
    total_min = total_sec // 60
    total_hour = total_min // 60
    rem_min = total_min % 60
    
    duration_str = f"{total_hour}시간 {rem_min}분" if total_hour > 0 else f"{rem_min}분"
    
    y = draw_info_row("러닝 타입", run_type, y)
    y = draw_info_row("목표 거리", f"{distance:.1f} km", y)
    y = draw_info_row("목표 페이스", f"{pace_min}'{pace_sec:02d}\"/km", y)
    y = draw_info_row("예상 소요 시간", duration_str, y)
    
    memo = running_plan.get("memo", "")
    
    # 인터벌 설정
    if run_type in ["인터벌 러닝", "빌드업 러닝"]:
        y -= 2 * mm
        c.setFont(bold_font, 9)
        c.setFillColor(COLOR_SECONDARY)
        c.drawString(13 * mm, y, f"[ {run_type} 세부 설정 ]")
        y -= 6 * mm
        
        if run_type == "인터벌 러닝":
            repeats = running_plan.get("interval_repeats", 5)
            fast_pace = running_plan.get("fast_pace", "4'00\"")
            recovery = running_plan.get("recovery_pace", "6'00\"")
            fast_dist = running_plan.get("fast_dist", 400)
            recovery_dist = running_plan.get("recovery_dist", 200)
            y = draw_info_row("반복 횟수", f"{repeats}회", y, 45 * mm)
            y = draw_info_row("인터벌 구간", f"{fast_dist}m @ {fast_pace}/km", y, 45 * mm)
            y = draw_info_row("회복 구간", f"{recovery_dist}m @ {recovery}/km", y, 45 * mm)
        
        elif run_type == "빌드업 러닝":
            start_pace = running_plan.get("buildup_start_pace", "6'00\"")
            end_pace = running_plan.get("buildup_end_pace", "4'30\"")
            y = draw_info_row("시작 페이스", f"{start_pace}/km", y, 45 * mm)
            y = draw_info_row("종료 페이스", f"{end_pace}/km", y, 45 * mm)
    
    if memo:
        y -= 2 * mm
        c.setFont(bold_font, 9)
        c.setFillColor(COLOR_TEXT)
        c.drawString(13 * mm, y, "📝 메모")
        y -= 5 * mm
        c.setFont(main_font, 8.5)
        c.drawString(16 * mm, y, memo[:100])
        if len(memo) > 100:
            y -= 5 * mm
            c.drawString(16 * mm, y, memo[100:200])
        y -= 5 * mm
    
    y -= 5 * mm
    
    # (5. 오늘의 러닝 추천 지수 및 띠 그래프 영역 삭제)
    
    # ─── 하단 서명 ───
    # 구분선
    c.setStrokeColor(COLOR_SECONDARY)
    c.setLineWidth(0.5)
    c.line(10 * mm, 25 * mm, width - 10 * mm, 25 * mm)
    
    # 좌측 하단 - 앱 정보
    c.setFont(main_font, 7)
    c.setFillColor(COLOR_GRAY)
    c.drawString(13 * mm, 18 * mm, "생성: 옥수수 러닝크루 러닝 플래너 앱")
    c.drawString(13 * mm, 13 * mm, f"기상 데이터: 기상청 단기예보 API  |  지도: 카카오맵")
    
    # 우측 하단 - 필기체 사인
    # ReportLab에서는 필기체 폰트가 없으므로 이탤릭체 + 장식으로 표현
    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-BoldOblique", 14)
    c.drawRightString(width - 13 * mm, 20 * mm, "Oksusu Running Crew")
    c.setFont(main_font, 9.5)
    c.setFillColor(COLOR_SECONDARY)
    c.drawRightString(width - 13 * mm, 14 * mm, "~ 옥수수 러닝크루 ~")
    
    # 서명 라인 장식
    c.setStrokeColor(COLOR_GOLD)
    c.setLineWidth(1)
    sign_right = width - 13 * mm
    sign_left = sign_right - 60 * mm
    c.line(sign_left, 12 * mm, sign_right, 12 * mm)
    
    c.save()
    buffer.seek(0)
    return buffer
