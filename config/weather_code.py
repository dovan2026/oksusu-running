"""
기상청 단기예보 API 날씨 코드 매핑 테이블
"""

# 하늘 상태 코드 (SKY)
SKY_CODE = {
    1: {"label": "맑음", "emoji": "☀️", "color": "#FFD700"},
    3: {"label": "구름많음", "emoji": "⛅", "color": "#87CEEB"},
    4: {"label": "흐림", "emoji": "☁️", "color": "#808080"},
}

# 강수 형태 코드 (PTY)
PTY_CODE = {
    0: {"label": "없음", "emoji": ""},
    1: {"label": "비", "emoji": "🌧️", "color": "#4169E1"},
    2: {"label": "비/눈", "emoji": "🌨️", "color": "#6495ED"},
    3: {"label": "눈", "emoji": "❄️", "color": "#87CEEB"},
    4: {"label": "소나기", "emoji": "⛈️", "color": "#4682B4"},
}

# 풍향 코드 (VEC → 방향)
def wind_direction_label(vec_deg: float) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    kr_dirs = ["북", "북북동", "북동", "동북동", "동", "동남동", "남동", "남남동",
               "남", "남남서", "남서", "서남서", "서", "서북서", "북서", "북북서"]
    idx = int((vec_deg + 11.25) / 22.5) % 16
    return kr_dirs[idx]


# 풍속 강도 설명
def wind_level_label(wsd: float) -> str:
    if wsd < 4:
        return "약풍 (러닝에 영향 없음)"
    elif wsd < 9:
        return "약간 강한 바람 (약간 부담)"
    elif wsd < 14:
        return "강한 바람 (러닝 페이스 영향)"
    else:
        return "매우 강한 바람 (야외 러닝 주의)"


# 날씨 종합 상태 반환
def get_weather_summary(sky: int, pty: int, tmp: float, pop: int, wsd: float, reh: int) -> dict:
    if pty > 0:
        sky_info = PTY_CODE.get(pty, PTY_CODE[0])
        weather_label = sky_info["label"]
        weather_emoji = sky_info["emoji"]
        weather_color = sky_info.get("color", "#4169E1")
    else:
        sky_info = SKY_CODE.get(sky, SKY_CODE[1])
        weather_label = sky_info["label"]
        weather_emoji = sky_info["emoji"]
        weather_color = sky_info.get("color", "#FFD700")

    # 온도 체감
    if tmp <= 0:
        temp_feel = "매우 추움 🥶"
    elif tmp <= 5:
        temp_feel = "추움"
    elif tmp <= 10:
        temp_feel = "쌀쌀함"
    elif tmp <= 15:
        temp_feel = "서늘함"
    elif tmp <= 20:
        temp_feel = "쾌적함 👍"
    elif tmp <= 25:
        temp_feel = "따뜻함"
    elif tmp <= 30:
        temp_feel = "더움 🌡️"
    else:
        temp_feel = "매우 더움 🥵"

    # 러닝 추천도
    is_rain = pty > 0
    is_strong_wind = wsd >= 9
    running_score = 100
    if is_rain:
        running_score -= 40
    if pop >= 60:
        running_score -= 20
    elif pop >= 40:
        running_score -= 10
    if wsd >= 14:
        running_score -= 30
    elif wsd >= 9:
        running_score -= 15
    if tmp <= 0 or tmp >= 33:
        running_score -= 25
    elif tmp <= 5 or tmp >= 30:
        running_score -= 10
    if reh >= 85:
        running_score -= 10
    running_score = max(0, running_score)

    if running_score >= 80:
        run_recommend = "최적 🏃"
        run_color = "#00C851"
    elif running_score >= 60:
        run_recommend = "좋음 👍"
        run_color = "#33B679"
    elif running_score >= 40:
        run_recommend = "보통 😐"
        run_color = "#F9A825"
    elif running_score >= 20:
        run_recommend = "주의 ⚠️"
        run_color = "#FF6D00"
    else:
        run_recommend = "비추천 ❌"
        run_color = "#D50000"

    return {
        "weather_label": weather_label,
        "weather_emoji": weather_emoji,
        "weather_color": weather_color,
        "temp_feel": temp_feel,
        "wind_level": wind_level_label(wsd),
        "running_score": running_score,
        "run_recommend": run_recommend,
        "run_color": run_color,
        "is_rain": is_rain,
    }
