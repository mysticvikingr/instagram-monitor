from enum import Enum


class IntervalEnum(str, Enum):
    thirty_seconds = "30s"
    thirty_minutes = "30m"
    one_hour = "1h"
    one_day = "1d"
    seven_days = "7d"


INTERVAL_MAP = {
    IntervalEnum.thirty_seconds: 30,
    IntervalEnum.thirty_minutes: 30 * 60,
    IntervalEnum.one_hour: 60 * 60,
    IntervalEnum.one_day: 24 * 60 * 60,
    IntervalEnum.seven_days: 7 * 24 * 60 * 60,
} 