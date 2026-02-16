# -*- coding: utf-8 -*-
"""
农历工具模块
用于根据公历年份推断农历年和生肖
"""

def get_zodiac(year):
    """
    根据年份获取生肖
    :param year: 公历年份
    :return: 生肖名称
    """
    zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
    # 1900年是鼠年
    offset = (year - 1900) % 12
    return zodiacs[offset]


def get_lunar_year_name(year):
    """
    根据年份获取农历年名称（干支纪年法）
    :param year: 公历年份
    :return: 农历年名称，如"甲辰年"
    """
    # 天干
    tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    # 地支
    dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    # 1900年是庚子年
    year_offset = year - 1900
    tiangan_index = (year_offset + 6) % 10  # 1900年是庚，庚在天干中索引为6
    dizhi_index = (year_offset) % 12  # 1900年是子，子在地支中索引为0

    return f"{tiangan[tiangan_index]}{dizhi[dizhi_index]}年"


def get_lunar_info(year):
    """
    获取年份的农历信息
    :param year: 公历年份
    :return: 包含农历年名称和生肖的字典
    """
    zodiac = get_zodiac(year)
    lunar_year = get_lunar_year_name(year)
    return {
        'year': year,
        'lunar_year': lunar_year,
        'zodiac': zodiac
    }


if __name__ == '__main__':
    # 测试代码
    for year in [2024, 2025, 2026]:
        info = get_lunar_info(year)
        print(f"{year}年: {info['lunar_year']}, 生肖: {info['zodiac']}")
