from datetime import date

from dateutil.parser import parse


def format_date(d: date) -> str:
    return d.strftime("%Y年%m月%d日")


def days_until(target: str) -> int:
    target_date = parse(target).date()
    delta = target_date - date.today()
    return delta.days
