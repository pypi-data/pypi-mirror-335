import re
import calendar
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np


def first_and_last_day(date):
    """
    返回指定日期当月的第一天和最后一天
    """
    date = pd.to_datetime(date)  # n 月以前的今天
    _, _lastDay = calendar.monthrange(date.year, date.month)  # 返回月的第一天的星期和当月总天数
    _firstDay = datetime.date(date.year, date.month, day=1)
    _lastDay = datetime.date(date.year, date.month, day=_lastDay)
    return _firstDay, _lastDay


def get_day_of_month(num: int, fm=None):
    """
    num: 获取n月以前的第一天和最后一天, num=0时, 返回当月第一天和最后一天
    fm: 日期输出格式
    """
    if not fm:
        fm ='%Y%m%d'
    _today = datetime.date.today()
    months_ago = _today - relativedelta(months=num)  # n 月以前的今天
    _, _lastDay = calendar.monthrange(months_ago.year, months_ago.month)  # 返回月的第一天的星期和当月总天数
    _firstDay = datetime.date(months_ago.year, months_ago.month, day=1).strftime(fm)
    _lastDay = datetime.date(months_ago.year, months_ago.month, day=_lastDay).strftime(fm)
    return _firstDay, _lastDay


def dates_between(start_date, end_date, fm=None) -> list:
    """
    获取两个日期之间的所有日期， 返回 list
    fm: 日期输出格式
    """
    if not fm:
        fm ='%Y%m%d'
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime(fm))
        current_date += datetime.timedelta(days=1)
    return dates


def cover_df(df):
    df.replace([np.inf, -np.inf], '0', inplace=True)  # 清理一些非法值
    df.replace(to_replace=['\\N', '-', '--', '', 'nan', 'NAN'], value='0', regex=False, inplace=True)  # 替换掉特殊字符
    df.replace(to_replace=[','], value='', regex=True, inplace=True)
    df.replace(to_replace=['="'], value='', regex=True, inplace=True)  # ="和"不可以放在一起清洗, 因为有: id=86785565
    df.replace(to_replace=['"'], value='', regex=True, inplace=True)
    cols = df.columns.tolist()
    for col in cols:
        df[col] = df[col].apply(
            lambda x: float(float((str(x).rstrip("%"))) / 100) if re.findall(r'^\d+\.?\d*%$', str(x)) else x)

        new_col = col.lower()
        new_col = re.sub(r'[()\-，,&~^、 （）\"\'“”=·/。》《><！!`]', '_', new_col, re.IGNORECASE)
        new_col = new_col.replace('）', '')
        new_col = re.sub(r'_{2,}', '_', new_col)
        new_col = re.sub(r'_+$', '', new_col)
        df.rename(columns={col: new_col}, inplace=True)
    df.fillna(0, inplace=True)
    return df


def translate_keys(original_dict:dict, translation_dict:dict) -> dict:
    """
    original_dict键名翻译, 若键存在则返回翻译值，否则返回原键
    """
    return {translation_dict.get(k, k): v for k, v in original_dict.items()}


if __name__ == '__main__':
    pass