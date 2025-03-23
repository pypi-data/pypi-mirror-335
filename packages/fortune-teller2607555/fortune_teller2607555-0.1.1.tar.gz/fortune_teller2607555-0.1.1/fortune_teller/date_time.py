import random
from datetime import datetime, timedelta

def rand_date_time(current_date_str: str, fortune: str) -> str:
    if not fortune:
        return "Oops: no fortune provided ( • ᴖ • ｡) Please supply a fortune from one of the other functions."
    try:
        current_date = datetime.strptime(current_date_str, "%Y-%m-%d")
    except ValueError:
        return "Oops: Invalid date format ( • ᴖ • ｡) Please use the right format, YYYY-MM-DD, next time you decide to choose this function."
    
    end_date = datetime(2060, 12, 31)
    if current_date > end_date:
        return "Oops: We can't read your future that far ahead ( • ᴖ • ｡) Only dates up to December 31, 2060 are allowed. Please keep that in mind next time you decide to choose this function!"
    
    delta_days = (end_date - current_date).days
    random_offset = random.randint(0, delta_days)
    random_date = current_date + timedelta(days=random_offset)
    
    day_of_week = random_date.strftime("%A")
    month_name  = random_date.strftime("%B")
    day         = random_date.day
    year        = random_date.year

    return f"📅 On {day_of_week}, {month_name} {day}, {year} — {fortune}"