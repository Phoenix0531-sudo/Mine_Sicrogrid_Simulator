# -*- coding: utf-8 -*-
"""
通用工具模块 - 提供通用的工具函数和辅助功能
包含单位转换、数据处理、常用计算等功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def convert_units(value, from_unit, to_unit):
    """
    单位转换函数
    
    参数:
    - value: float, 要转换的数值
    - from_unit: str, 源单位
    - to_unit: str, 目标单位
    
    返回:
    - float: 转换后的数值
    """
    # 功率单位转换
    power_conversions = {
        ('kW', 'MW'): 0.001,
        ('MW', 'kW'): 1000,
        ('kW', 'W'): 1000,
        ('W', 'kW'): 0.001,
        ('MW', 'GW'): 0.001,
        ('GW', 'MW'): 1000
    }
    
    # 能量单位转换
    energy_conversions = {
        ('kWh', 'MWh'): 0.001,
        ('MWh', 'kWh'): 1000,
        ('MWh', 'GWh'): 0.001,
        ('GWh', 'MWh'): 1000,
        ('kWh', 'GWh'): 0.000001,
        ('GWh', 'kWh'): 1000000
    }
    
    # 合并转换字典
    conversions = {**power_conversions, **energy_conversions}
    
    conversion_key = (from_unit, to_unit)
    
    if conversion_key in conversions:
        return value * conversions[conversion_key]
    elif from_unit == to_unit:
        return value
    else:
        raise ValueError(f"不支持从 {from_unit} 到 {to_unit} 的转换")

def calculate_capacity_factor(generation_series, rated_capacity_kw):
    """
    计算容量因子
    
    参数:
    - generation_series: pandas.Series, 发电功率时间序列 (kW)
    - rated_capacity_kw: float, 额定容量 (kW)
    
    返回:
    - float: 容量因子 (0-1)
    """
    if rated_capacity_kw <= 0:
        return 0
    
    actual_generation = generation_series.sum()  # 实际发电量 (kWh)
    theoretical_max = rated_capacity_kw * len(generation_series)  # 理论最大发电量 (kWh)
    
    capacity_factor = actual_generation / theoretical_max if theoretical_max > 0 else 0
    
    return min(capacity_factor, 1.0)  # 确保不超过1

def calculate_lcoe(capex, opex_annual, generation_annual_kwh, lifetime_years, discount_rate=0.08):
    """
    计算平准化电力成本 (LCOE)
    
    参数:
    - capex: float, 初始投资成本 ($)
    - opex_annual: float, 年运维成本 ($/年)
    - generation_annual_kwh: float, 年发电量 (kWh/年)
    - lifetime_years: int, 项目寿命 (年)
    - discount_rate: float, 折现率 (默认8%)
    
    返回:
    - float: LCOE ($/kWh)
    """
    if generation_annual_kwh <= 0 or lifetime_years <= 0:
        return float('inf')
    
    # 计算净现值
    npv_costs = capex
    npv_generation = 0
    
    for year in range(1, lifetime_years + 1):
        discount_factor = 1 / (1 + discount_rate) ** year
        npv_costs += opex_annual * discount_factor
        npv_generation += generation_annual_kwh * discount_factor
    
    lcoe = npv_costs / npv_generation if npv_generation > 0 else float('inf')
    
    return lcoe

def resample_timeseries(data, target_frequency='H'):
    """
    重采样时间序列数据
    
    参数:
    - data: pandas.Series 或 pandas.DataFrame, 时间序列数据
    - target_frequency: str, 目标频率 ('H'=小时, 'D'=天, 'M'=月)
    
    返回:
    - 重采样后的数据
    """
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("数据索引必须是DatetimeIndex")
    
    if target_frequency == 'H':
        return data.resample('H').mean()
    elif target_frequency == 'D':
        return data.resample('D').sum()
    elif target_frequency == 'M':
        return data.resample('M').sum()
    else:
        return data.resample(target_frequency).mean()

def calculate_statistics(data, percentiles=[25, 50, 75, 95]):
    """
    计算数据统计信息
    
    参数:
    - data: pandas.Series, 数据序列
    - percentiles: list, 要计算的百分位数
    
    返回:
    - dict: 统计信息字典
    """
    stats = {
        'count': len(data),
        'mean': data.mean(),
        'std': data.std(),
        'min': data.min(),
        'max': data.max(),
        'sum': data.sum()
    }
    
    # 添加百分位数
    for p in percentiles:
        stats[f'p{p}'] = data.quantile(p/100)
    
    return stats

def detect_outliers(data, method='iqr', threshold=1.5):
    """
    检测异常值
    
    参数:
    - data: pandas.Series, 数据序列
    - method: str, 检测方法 ('iqr', 'zscore')
    - threshold: float, 阈值
    
    返回:
    - pandas.Series: 布尔序列，True表示异常值
    """
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = (data < lower_bound) | (data > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((data - data.mean()) / data.std())
        outliers = z_scores > threshold
    
    else:
        raise ValueError("method 必须是 'iqr' 或 'zscore'")
    
    return outliers

def smooth_data(data, window_size=24, method='rolling_mean'):
    """
    数据平滑处理
    
    参数:
    - data: pandas.Series, 数据序列
    - window_size: int, 窗口大小
    - method: str, 平滑方法 ('rolling_mean', 'exponential')
    
    返回:
    - pandas.Series: 平滑后的数据
    """
    if method == 'rolling_mean':
        return data.rolling(window=window_size, center=True).mean()
    elif method == 'exponential':
        return data.ewm(span=window_size).mean()
    else:
        raise ValueError("method 必须是 'rolling_mean' 或 'exponential'")

def create_time_index(start_date, periods, freq='H'):
    """
    创建时间索引
    
    参数:
    - start_date: str 或 datetime, 开始日期
    - periods: int, 时间点数量
    - freq: str, 频率 ('H'=小时, 'D'=天)
    
    返回:
    - pandas.DatetimeIndex: 时间索引
    """
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    
    return pd.date_range(start=start_date, periods=periods, freq=freq)

def validate_time_series(data, expected_length=8760):
    """
    验证时间序列数据
    
    参数:
    - data: pandas.Series, 时间序列数据
    - expected_length: int, 期望长度
    
    返回:
    - dict: 验证结果
    """
    validation_result = {
        'is_valid': True,
        'issues': []
    }
    
    # 检查长度
    if len(data) != expected_length:
        validation_result['is_valid'] = False
        validation_result['issues'].append(f"数据长度 {len(data)} 不等于期望长度 {expected_length}")
    
    # 检查缺失值
    missing_count = data.isnull().sum()
    if missing_count > 0:
        validation_result['issues'].append(f"存在 {missing_count} 个缺失值")
    
    # 检查负值（对于功率数据）
    negative_count = (data < 0).sum()
    if negative_count > 0:
        validation_result['issues'].append(f"存在 {negative_count} 个负值")
    
    # 检查时间索引
    if not isinstance(data.index, pd.DatetimeIndex):
        validation_result['is_valid'] = False
        validation_result['issues'].append("索引不是DatetimeIndex类型")
    
    return validation_result

def format_number(value, unit='', decimals=2):
    """
    格式化数字显示
    
    参数:
    - value: float, 数值
    - unit: str, 单位
    - decimals: int, 小数位数
    
    返回:
    - str: 格式化后的字符串
    """
    if abs(value) >= 1e9:
        formatted = f"{value/1e9:.{decimals}f}B"
    elif abs(value) >= 1e6:
        formatted = f"{value/1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        formatted = f"{value/1e3:.{decimals}f}K"
    else:
        formatted = f"{value:.{decimals}f}"
    
    return f"{formatted} {unit}".strip()

def calculate_payback_period(initial_investment, annual_savings):
    """
    计算投资回收期
    
    参数:
    - initial_investment: float, 初始投资 ($)
    - annual_savings: float, 年节省金额 ($/年)
    
    返回:
    - float: 回收期 (年)
    """
    if annual_savings <= 0:
        return float('inf')
    
    return initial_investment / annual_savings
