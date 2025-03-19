import calendar
import time
import datetime
from datetime import date, datetime as inner_datetime, time, timedelta
from typing import Union

year_format = "%Y"
month_format = "%Y-%m"
day_format = "%Y-%m-%d"
hours_format = "%Y-%m-%d %H"
minutes_format = "%Y-%m-%d %H:%M"
seconds_format = "%Y-%m-%d %H:%M:%S"


def unix_time(string: str, date_format: str) -> int:
    """
    将日期转换为时间戳
    :param string:
    :param date_format:
    :return:
    """
    # 转换成时间数组
    time_list = time.strptime(string, date_format)
    # 转换成时间戳
    timestamp = int(time.mktime(time_list))
    return timestamp


def custom_time(timestamp: int, date_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    将时间戳转为日期 date_format默认
    :param timestamp:
    :param date_format:
    :return:
    """
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    dt = time.strftime(date_format, time_local)
    return dt


def date_to_timestamp(date_: date) -> int:
    day_str = date_.strftime(day_format)
    return unix_time(day_str, day_format)


def get_curr_time() -> int:
    """
    获取当前时间戳 秒
    :return:
    """
    return int(time.time())


def get_curr_time_of_ms() -> int:
    """
    获取当前时间戳 毫秒
    :return:
    """
    return int(time.time() * 1000)


def get_curr_day() -> str:
    """
    获取当前日期
    :return:
    """
    return datetime.datetime.today().strftime(day_format)


def get_day(timestamp: int = None) -> date:
    """
    获取日期对象 默认当天
    :param timestamp: 时间戳 单位s
    :return:
    """
    return datetime.datetime.utcfromtimestamp(timestamp) if timestamp else datetime.datetime.today()


def get_start_of_day(timestamp: int = None) -> int:
    """
    获取一天开始时间戳 默认当天
    :param timestamp: 时间戳 单位s
    :return:
    """
    if timestamp:
        return unix_time(custom_time(timestamp, day_format), day_format)
    return unix_time(get_curr_day(), day_format)


def get_end_of_day(time_stamp: int = None) -> int:
    """
    获取一天结束时间戳 默认当天
    :param time_stamp: 时间戳 单位s
    :return:
    """
    return get_start_of_day(time_stamp) + 86399


def get_start_of_week(timestamp: int = None, weekend_is_first: bool = False):
    """
    获取一周的开始时间戳  默认：本周
    :param timestamp: 时间戳 单位s
    :param weekend_is_first: 默认周一是第一天
    :return:
    """
    data = get_day(timestamp)
    days_ago = data.isoweekday() - 1
    if weekend_is_first:
        days_ago = days_ago + 1
    start_week = data - datetime.timedelta(days=days_ago)
    return date_to_timestamp(start_week)


def get_end_of_week(timestamp: int = None, weekend_is_first: bool = False) -> int:
    """
    获取一周的结束时间戳 默认：本周
    :param timestamp: 时间戳 单位s
    :param weekend_is_first: 默认周一是第一天
    :return:
    """
    return get_start_of_week(timestamp, weekend_is_first) + 604799


def get_start_of_month(time_stamp: int = None) -> int:
    """
    获取本月的开始时间戳 默认本月
    :param time_stamp: 时间戳 单位s
    :return:
    """
    data = get_day(time_stamp)
    start_month = datetime.date(data.year, data.month, 1)
    return date_to_timestamp(start_month)


def get_ent_of_month(time_stamp: int = None) -> int:
    """
    获取一个月的结束时间戳 默认本月
    :param time_stamp: 时间戳 单位s
    :return:
    """
    data = get_day(time_stamp)
    if data.month == 12:
        year_int, month_int = data.year + 1, data.month
    else:
        year_int, month_int = data.year, data.month + 1
    start_month = datetime.date(year_int, month_int, 1)
    return date_to_timestamp(start_month) - 1


def get_start_of_year(timestamp: int = None) -> int:
    """
    获取一年的开始时间戳 默认本年
    :param timestamp: 时间戳 单位s
    :return:
    """
    data = get_day(timestamp)
    start_month = datetime.date(data.year, 1, 1)
    return date_to_timestamp(start_month)


def get_end_of_year(timestamp: int = None) -> int:
    """
    获取一年的结束时间戳 默认本年
    :param timestamp: 时间戳 单位s
    :return:
    """
    data = get_day(timestamp)
    start_month = datetime.date(data.year + 1, 1, 1)
    return date_to_timestamp(start_month) - 1


def get_start_of_the_day(one_day: Union[str, date]) -> datetime:
    """获取一天开始和结束时间"""
    if isinstance(one_day, str):
        one_day = inner_datetime.strptime(one_day, day_format)
    start_time = inner_datetime.combine(one_day, time().min)
    end_time = inner_datetime.combine(one_day, time().max)
    return start_time, end_time


def get_month_first_day(day: date = None) -> date:
    """获取当月第一天"""
    if day is None:
        day = inner_datetime.now().date()
    return inner_datetime(day.year, day.month, 1).date()


def get_previous_month_first_day(day: date = None) -> date:
    """获取上月第一天"""
    if day is None:
        day = inner_datetime.now().date()
    return get_month_first_day(inner_datetime(day.year, day.month, 1).date() - timedelta(days=1))


def get_next_month_first_day(day: date = None) -> date:
    """获取下一个月第一天"""
    if day is None:
        day = inner_datetime.now().date()
    return inner_datetime(day.year, day.month, calendar.monthrange(day.year, day.month)[1]).date() + timedelta(days=1)
