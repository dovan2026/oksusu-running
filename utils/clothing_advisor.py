"""
날씨 조건에 따른 러닝 복장 추천 모듈
"""


def get_clothing_recommendation(tmp: float, pty: int, wsd: float, pop: int) -> dict:
    """
    날씨 조건에 따른 러닝 복장 추천
    
    Args:
        tmp: 기온 (°C)
        pty: 강수 형태 (0=없음, 1=비, 2=비/눈, 3=눈, 4=소나기)
        wsd: 풍속 (m/s)
        pop: 강수 확률 (%)
    
    Returns:
        복장 추천 딕셔너리
    """
    clothing = {
        "상의": [],
        "하의": [],
        "레이어링": [],
        "악세서리": [],
        "신발": [],
        "특수장비": [],
        "tip": "",
    }
    
    is_rain = pty > 0
    is_snow = pty in [2, 3]
    might_rain = pop >= 40
    strong_wind = wsd >= 9
    
    # ── 상의 ──
    if tmp <= 0:
        clothing["상의"].append("방풍+발열 러닝 재킷")
        clothing["상의"].append("기모 긴팔 러닝 셔츠")
    elif tmp <= 5:
        clothing["상의"].append("방풍 러닝 재킷")
        clothing["상의"].append("긴팔 러닝 셔츠 (기모)")
    elif tmp <= 10:
        clothing["상의"].append("얇은 러닝 재킷 or 바람막이")
        clothing["상의"].append("긴팔 러닝 셔츠")
    elif tmp <= 15:
        clothing["상의"].append("긴팔 러닝 셔츠")
        clothing["상의"].append("(선택) 얇은 조끼")
    elif tmp <= 20:
        clothing["상의"].append("긴팔 또는 반팔 러닝 셔츠")
    elif tmp <= 25:
        clothing["상의"].append("반팔 러닝 셔츠")
    else:
        clothing["상의"].append("민소매 러닝 셔츠")
        clothing["상의"].append("통기성 우선 소재 선택")
    
    # ── 하의 ──
    if tmp <= 5:
        clothing["하의"].append("기모 러닝 타이츠")
        clothing["하의"].append("방풍 러닝 팬츠")
    elif tmp <= 10:
        clothing["하의"].append("러닝 타이츠")
    elif tmp <= 15:
        clothing["하의"].append("러닝 타이츠 or 롱 러닝 팬츠")
    elif tmp <= 20:
        clothing["하의"].append("반바지 또는 7부 러닝 팬츠")
    else:
        clothing["하의"].append("러닝 반바지")
    
    # ── 레이어링 ──
    if is_rain or might_rain:
        clothing["레이어링"].append("방수 러닝 재킷 (Gore-Tex or 방수 처리 소재)")
    if strong_wind and tmp <= 15:
        clothing["레이어링"].append("방풍 소재 레이어 추가")
    
    # ── 악세서리 ──
    if tmp <= 0:
        clothing["악세서리"].append("방한 러닝 모자 (귀 덮개 포함)")
        clothing["악세서리"].append("러닝용 장갑 (두꺼운)")
        clothing["악세서리"].append("넥워머")
    elif tmp <= 5:
        clothing["악세서리"].append("귀마개 밴드 or 비니")
        clothing["악세서리"].append("러닝용 장갑")
    elif tmp <= 10:
        clothing["악세서리"].append("가벼운 귀마개 밴드")
        clothing["악세서리"].append("(선택) 얇은 장갑")
    
    if tmp >= 25:
        clothing["악세서리"].append("러닝 캡 (햇빛 차단)")
        clothing["악세서리"].append("선글라스")
        clothing["악세서리"].append("선크림 필수")
    
    if is_rain or might_rain:
        clothing["악세서리"].append("챙 있는 러닝 캡 (비 차단)")
    
    # ── 신발 ──
    if is_snow or (is_rain and tmp <= 3):
        clothing["신발"].append("방수 기능 트레일 러닝화")
        clothing["신발"].append("방수 양말 (선택)")
    elif is_rain:
        clothing["신발"].append("물 빠짐 좋은 메쉬 러닝화 또는 방수 러닝화")
    else:
        clothing["신발"].append("일반 로드 러닝화")
        if "흙길" in "" or "트레일" in "":  # 코스 정보 있으면 트레일화 추천
            clothing["신발"].append("(트레일 코스) 트레일 러닝화 권장")
    
    # ── 특수장비 ──
    if is_rain:
        clothing["특수장비"].append("방수 폰 케이스 또는 지퍼락")
    if tmp >= 28:
        clothing["특수장비"].append("수분 보충 벨트 또는 핸드헬드 물병")
        clothing["특수장비"].append("전해질 보충제 (이온음료)")
    
    # ── 팁 ──
    if tmp >= 30:
        clothing["tip"] = "🥵 고온 환경에서는 체온 조절이 중요합니다. 10~15분마다 수분 보충, 극도의 더위엔 실내 러닝을 고려하세요."
    elif tmp <= 0:
        clothing["tip"] = "🥶 영하에서는 근육 부상 위험이 높습니다. 충분한 워밍업(10분 이상)과 레이어링으로 체온을 유지하세요."
    elif is_rain:
        clothing["tip"] = "🌧️ 우천 시 시야 확보에 주의하고, 미끄러운 노면에서 보폭을 줄이세요. 마찰 부위(겨드랑이, 허벅지 안쪽)에 바셀린을 바르면 쓸림 방지에 효과적입니다."
    elif strong_wind:
        clothing["tip"] = "💨 강풍 시 전반부는 역풍으로 달려 후반부 순풍으로 돌아오는 전략이 효율적입니다."
    elif 15 <= tmp <= 20:
        clothing["tip"] = "✨ 러닝 최적 온도입니다! 편안한 페이스로 즐겁게 달려보세요. 옥수수 파이팅! 🌽"
    else:
        clothing["tip"] = f"현재 기온 {tmp}°C에 맞는 복장을 착용하고, 러닝 전 충분한 워밍업을 해주세요."
    
    # 빈 카테고리 제거
    clothing = {k: v for k, v in clothing.items() if v}
    
    return clothing


def get_clothing_for_course_terrain(terrain: str, clothing: dict) -> dict:
    """코스 지형에 따른 추가 복장 추천"""
    if "흙길" in terrain or "트레일" in terrain or "바위" in terrain:
        if "신발" in clothing:
            if "트레일 러닝화" not in str(clothing["신발"]):
                clothing["신발"].insert(0, "⚠️ 트레일 러닝화 필수 (미끄럼 방지)")
        else:
            clothing["신발"] = ["⚠️ 트레일 러닝화 필수 (미끄럼 방지)"]
        
        if "특수장비" in clothing:
            clothing["특수장비"].append("발목 보호대 (선택)")
        else:
            clothing["특수장비"] = ["발목 보호대 (선택)"]
    
    return clothing


CATEGORY_ICONS = {
    "상의": "👕",
    "하의": "🩳",
    "레이어링": "🧥",
    "악세서리": "🧢",
    "신발": "👟",
    "특수장비": "🎒",
}
