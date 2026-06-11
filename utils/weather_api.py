"""
기상청 단기예보 API 호출 모듈
- Endpoint: http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst
- 예보 기간: 최대 5일
- 발표 시각: 02, 05, 08, 11, 14, 17, 20, 23시
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Optional
import os


BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"

# 발표 시각 목록 (HH00 형식)
BASE_TIMES = ["2300", "2000", "1700", "1400", "1100", "0800", "0500", "0200"]


def get_valid_base_time(target_dt: datetime) -> tuple[str, str]:
    """
    현재 시각 기준으로 가장 최근 발표 시각을 반환
    Returns: (base_date: YYYYMMDD, base_time: HHMM)
    """
    now = datetime.now()
    
    # 현재 시간에서 가장 가까운 과거 발표 시각 찾기 (1시간 이전 기준)
    check_dt = now - timedelta(hours=1)
    
    for btime in BASE_TIMES:
        hour = int(btime[:2])
        check_hour = check_dt.hour
        check_date = check_dt.strftime("%Y%m%d")
        
        if check_hour >= hour:
            return check_date, btime
    
    # 자정 이전이면 전날 23시
    yesterday = (check_dt - timedelta(days=1)).strftime("%Y%m%d")
    return yesterday, "2300"


def fetch_weather(api_key: str, nx: int, ny: int, target_date: datetime) -> Optional[dict]:
    """
    기상청 단기예보 API 호출
    
    Args:
        api_key: 서비스 키
        nx: 격자 X 좌표
        ny: 격자 Y 좌표
        target_date: 예보 조회 날짜
    
    Returns:
        날씨 데이터 딕셔너리 또는 None (오류 시)
    """
    base_date, base_time = get_valid_base_time(datetime.now())
    
    params = {
        "serviceKey": api_key,
        "pageNo": 1,
        "numOfRows": 1000,
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny,
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # 응답 코드 확인
        result_code = data.get("response", {}).get("header", {}).get("resultCode", "")
        if result_code != "00":
            result_msg = data.get("response", {}).get("header", {}).get("resultMsg", "Unknown error")
            return {"error": f"API 오류: {result_msg} (코드: {result_code})"}
        
        items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        
        if not items:
            return {"error": "날씨 데이터가 없습니다."}
        
        # 목표 날짜의 데이터만 필터링
        target_date_str = target_date.strftime("%Y%m%d")
        
        # 시간대별로 가장 가까운 데이터 추출
        # 기상청 API는 3시간 단위 예보 (0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300)
        # 러닝 크루는 주로 저녁 시간대이므로 1800~2100 데이터 우선
        preferred_times = ["1800", "1900", "2000", "2100", "1500", "1200", "0900", "0600"]
        
        weather_data = {}
        for item in items:
            if item.get("fcstDate") == target_date_str:
                category = item.get("category")
                fcst_time = item.get("fcstTime")
                fcst_value = item.get("fcstValue")
                
                # 카테고리별로 시간대 우선순위에 맞게 저장
                key = f"{category}_{fcst_time}"
                weather_data[key] = fcst_value
        
        if not weather_data:
            return {"error": f"{target_date_str} 날짜의 예보 데이터가 없습니다. (최대 5일 이내 날짜를 선택하세요)"}
        
        # 원하는 시간대의 날씨 추출 (저녁 러닝 기준)
        result = _extract_weather_for_time(items, target_date_str, preferred_times)
        return result
        
    except requests.exceptions.Timeout:
        return {"error": "API 요청 시간이 초과되었습니다. 잠시 후 다시 시도하세요."}
    except requests.exceptions.ConnectionError:
        return {"error": "네트워크 연결을 확인해 주세요."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP 오류: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "API 응답 파싱 오류."}
    except Exception as e:
        return {"error": f"예상치 못한 오류: {str(e)}"}


def _extract_weather_for_time(items: list, target_date: str, preferred_times: list) -> dict:
    """
    항목 리스트에서 날짜+시간대별 날씨 데이터 추출
    """
    # 카테고리별 데이터 수집
    categories_by_time = {}
    for item in items:
        if item.get("fcstDate") != target_date:
            continue
        cat = item.get("category")
        time = item.get("fcstTime")
        val = item.get("fcstValue")
        
        if time not in categories_by_time:
            categories_by_time[time] = {}
        categories_by_time[time][cat] = val
    
    if not categories_by_time:
        return {"error": "해당 날짜의 데이터가 없습니다."}
    
    # 우선 시간대 탐색
    selected_time = None
    selected_data = {}
    for ptime in preferred_times:
        if ptime in categories_by_time:
            selected_time = ptime
            selected_data = categories_by_time[ptime]
            break
    
    if not selected_data:
        # 아무 시간대나 사용
        selected_time = list(categories_by_time.keys())[0]
        selected_data = categories_by_time[selected_time]
    
    # 하루 통계 (최고/최저 기온, 최대 강수확률)
    all_temps = []
    all_pops = []
    for time_data in categories_by_time.values():
        if "TMP" in time_data:
            try:
                all_temps.append(float(time_data["TMP"]))
            except:
                pass
        if "POP" in time_data:
            try:
                all_pops.append(int(time_data["POP"]))
            except:
                pass
    
    try:
        tmp = float(selected_data.get("TMP", 15))
    except:
        tmp = 15.0
    try:
        pop = int(selected_data.get("POP", 0))
    except:
        pop = 0
    try:
        wsd = float(selected_data.get("WSD", 2))
    except:
        wsd = 2.0
    try:
        reh = int(selected_data.get("REH", 60))
    except:
        reh = 60
    try:
        sky = int(selected_data.get("SKY", 1))
    except:
        sky = 1
    try:
        pty = int(selected_data.get("PTY", 0))
    except:
        pty = 0
    try:
        vec = float(selected_data.get("VEC", 0))
    except:
        vec = 0.0
    
    return {
        "fcst_time": selected_time,
        "fcst_date": target_date,
        "TMP": tmp,
        "POP": pop,
        "WSD": wsd,
        "REH": reh,
        "SKY": sky,
        "PTY": pty,
        "VEC": vec,
        "TMX": max(all_temps) if all_temps else tmp,
        "TMN": min(all_temps) if all_temps else tmp,
        "MAX_POP": max(all_pops) if all_pops else pop,
        "all_times": sorted(categories_by_time.keys()),
        "all_data": categories_by_time,
    }


def get_max_forecast_date() -> datetime:
    """기상청 API 최대 예보 가능 날짜 반환 (오늘 + 4일 = 5일치)"""
    return datetime.now() + timedelta(days=4)


def get_available_dates() -> list[datetime]:
    """조회 가능한 날짜 목록 반환"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return [today + timedelta(days=i) for i in range(5)]
