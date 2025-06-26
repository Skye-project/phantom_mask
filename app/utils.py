from datetime import datetime, time
import re

WEEKDAYS = {
    "Mon": "Mon", "Monday": "Mon",
    "Tue": "Tue", "Tues": "Tue", "Tuesday": "Tue",
    "Wed": "Wed", "Wednesday": "Wed",
    "Thu": "Thu", "Thur": "Thu", "Thursday": "Thu",
    "Fri": "Fri", "Friday": "Fri",
    "Sat": "Sat", "Saturday": "Sat",
    "Sun": "Sun", "Sunday": "Sun",
}

def parse_time(t: str) -> time:
    return datetime.strptime(t.strip(), "%H:%M").time()

def parse_opening_hours(raw: str):
    """輸入: 'Mon, Wed, Fri 08:00 - 12:00 / Tue, Thur 14:00 - 18:00'
       輸出: List[{"day_of_week": "Mon", "open_time": time(), "close_time": time()}, ...]
    """
    result = []
    parts = [p.strip() for p in raw.split("/")]

    for part in parts:
        match = re.match(r"^(.*?)\s+(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})$", part)
        if not match:
            continue
        days_raw, open_str, close_str = match.groups()
        open_time = parse_time(open_str)
        close_time = parse_time(close_str)
        days = [WEEKDAYS.get(d.strip(), d.strip()) for d in days_raw.split(",")]
        for day in days:
            result.append({
                "day_of_week": day,
                "open_time": open_time,
                "close_time": close_time
            })
    return result
