# -*- coding: utf-8 -*-
"""
输入验证模块 - 负责用户输入参数的验证
包含参数合理性检查、警告和错误分类功能
"""

from .config import get_config

def validate_inputs(user_inputs):
    """
    验证用户输入参数的合理性
    
    参数:
    - user_inputs: dict, 包含所有侧边栏用户输入值的字典
    
    返回:
    - tuple: (warnings, errors) 两个列表，分别包含警告信息和错误信息
    """
    warnings = []
    errors = []
    
    # 1. 检查所有数值输入是否为负数（致命错误）
    critical_numeric_params = {
        'annual_consumption': '年总用电量',
        'pv_capacity': '光伏装机容量',
        'wind_turbine_count': '风机数量',
        'battery_capacity': '电池储能容量',
        'battery_power': '电池最大充放电功率',
        'grid_purchase_price': '电网购电电价',
        'grid_sell_price': '上网卖电电价'
    }
    
    # 经纬度负数检查（可能合理，只是警告）
    coordinate_params = {
        'longitude': '经度',
        'latitude': '纬度'
    }
    
    # 检查关键参数的负数（致命错误）
    for param_key, param_name in critical_numeric_params.items():
        if param_key in user_inputs:
            value = user_inputs[param_key]
            if isinstance(value, (int, float)) and value < 0:
                errors.append(f"{param_name} 不能为负数，请重新输入。")
    
    # 检查坐标参数（警告）
    for param_key, param_name in coordinate_params.items():
        if param_key in user_inputs:
            value = user_inputs[param_key]
            if isinstance(value, (int, float)) and value < 0:
                warnings.append(f"{param_name} 为负数，请确认是否正确。")
    
    # 2. 检查经纬度范围（致命错误）
    if 'latitude' in user_inputs:
        lat = user_inputs['latitude']
        if lat < -90 or lat > 90:
            errors.append("纬度必须在-90到90度之间。")
    
    if 'longitude' in user_inputs:
        lon = user_inputs['longitude']
        if lon < -180 or lon > 180:
            errors.append("经度必须在-180到180度之间。")
    
    # 3. 检查电池充放电效率（致命错误）
    if 'battery_efficiency' in user_inputs:
        efficiency = user_inputs['battery_efficiency']
        if efficiency > 1 or efficiency < 0:
            errors.append("电池效率必须在0到1之间 (即0%到100%)。")
    
    # 4. 检查电网购买电价是否低于售电电价（警告）
    if 'grid_purchase_price' in user_inputs and 'grid_sell_price' in user_inputs:
        purchase_price = user_inputs['grid_purchase_price']
        sell_price = user_inputs['grid_sell_price']
        if purchase_price < sell_price:
            warnings.append("通常情况下，购电电价会高于售电电价，请检查您的设置。")
    
    # 5. 检查光伏板倾斜角（警告）
    if 'pv_tilt_angle' in user_inputs:
        tilt_angle = user_inputs['pv_tilt_angle']
        if tilt_angle < 0 or tilt_angle > 90:
            warnings.append("光伏板倾角通常在0到90度之间。")
    
    # 6. 额外的合理性检查（使用配置文件中的阈值）
    validation_config = get_config("validation")

    # 检查年总用电量是否过大或过小
    if 'annual_consumption' in user_inputs:
        consumption = user_inputs['annual_consumption']
        if consumption > validation_config["max_annual_consumption"]:
            warnings.append(f"年总用电量超过{validation_config['max_annual_consumption']} GWh，请确认是否正确。")
        elif consumption < validation_config["min_annual_consumption"]:
            warnings.append(f"年总用电量小于{validation_config['min_annual_consumption']} GWh，请确认是否正确。")

    # 检查光伏容量是否合理
    if 'pv_capacity' in user_inputs:
        pv_cap = user_inputs['pv_capacity']
        if pv_cap > validation_config["max_pv_capacity"]:
            warnings.append(f"光伏装机容量超过{validation_config['max_pv_capacity']} MW，请确认是否正确。")

    # 检查风机数量是否合理
    if 'wind_turbine_count' in user_inputs:
        turbine_count = user_inputs['wind_turbine_count']
        if turbine_count > validation_config["max_wind_turbines"]:
            warnings.append(f"风机数量超过{validation_config['max_wind_turbines']}台，请确认是否正确。")
    
    # 检查电池容量与功率的匹配性
    if 'battery_capacity' in user_inputs and 'battery_power' in user_inputs:
        capacity = user_inputs['battery_capacity']  # MWh
        power = user_inputs['battery_power']  # MW
        if capacity > 0 and power > 0:
            c_rate = power / capacity  # C倍率
            if c_rate > 2:
                warnings.append("电池功率相对于容量过高（C倍率>2），可能不经济，建议检查配置。")
            elif c_rate < 0.1:
                warnings.append("电池功率相对于容量过低（C倍率<0.1），可能无法有效调节，建议检查配置。")
    
    # 检查电价的合理性
    if 'grid_purchase_price' in user_inputs:
        purchase_price = user_inputs['grid_purchase_price']
        if purchase_price > 1.0:
            warnings.append("购电电价超过$1.0/kWh，请确认是否正确。")
        elif purchase_price < 0.01:
            warnings.append("购电电价低于$0.01/kWh，请确认是否正确。")
    
    if 'grid_sell_price' in user_inputs:
        sell_price = user_inputs['grid_sell_price']
        if sell_price > 0.5:
            warnings.append("售电电价超过$0.5/kWh，请确认是否正确。")
        elif sell_price < 0.001:
            warnings.append("售电电价低于$0.001/kWh，请确认是否正确。")
    
    return warnings, errors

def validate_data_consistency(user_inputs):
    """
    验证数据一致性
    
    参数:
    - user_inputs: dict, 用户输入数据
    
    返回:
    - list: 一致性检查警告列表
    """
    consistency_warnings = []
    
    # 检查可再生能源容量与负荷的匹配性
    if all(key in user_inputs for key in ['annual_consumption', 'pv_capacity', 'wind_turbine_count']):
        annual_consumption = user_inputs['annual_consumption']  # GWh
        pv_capacity = user_inputs['pv_capacity']  # MW
        wind_count = user_inputs['wind_turbine_count']
        
        # 估算可再生能源年发电量（简化计算）
        estimated_pv_generation = pv_capacity * 1500 / 1000  # 假设年利用小时数1500h，转换为GWh
        estimated_wind_generation = wind_count * 3 * 2000 / 1000  # 假设3MW风机，年利用小时数2000h
        total_renewable_generation = estimated_pv_generation + estimated_wind_generation
        
        renewable_ratio = total_renewable_generation / annual_consumption if annual_consumption > 0 else 0
        
        if renewable_ratio > 2:
            consistency_warnings.append("可再生能源装机容量相对于负荷过大，可能导致大量弃电。")
        elif renewable_ratio < 0.1:
            consistency_warnings.append("可再生能源装机容量相对于负荷过小，可再生能源渗透率可能很低。")
    
    # 检查储能容量与可再生能源的匹配性
    if all(key in user_inputs for key in ['battery_capacity', 'pv_capacity', 'wind_turbine_count']):
        battery_capacity = user_inputs['battery_capacity']  # MWh
        pv_capacity = user_inputs['pv_capacity']  # MW
        wind_count = user_inputs['wind_turbine_count']
        
        total_renewable_capacity = pv_capacity + wind_count * 3  # 假设3MW风机
        
        if total_renewable_capacity > 0:
            storage_ratio = battery_capacity / total_renewable_capacity
            if storage_ratio > 8:
                consistency_warnings.append("储能容量相对于可再生能源装机过大，可能不经济。")
            elif storage_ratio < 0.5:
                consistency_warnings.append("储能容量相对于可再生能源装机过小，可能无法有效平滑波动。")
    
    return consistency_warnings

def get_validation_summary(warnings, errors):
    """
    获取验证结果摘要
    
    参数:
    - warnings: list, 警告列表
    - errors: list, 错误列表
    
    返回:
    - dict: 验证摘要信息
    """
    summary = {
        'total_warnings': len(warnings),
        'total_errors': len(errors),
        'validation_passed': len(errors) == 0,
        'can_proceed': len(errors) == 0,
        'severity_level': 'error' if errors else ('warning' if warnings else 'success')
    }
    
    return summary

def format_validation_message(warnings, errors):
    """
    格式化验证消息
    
    参数:
    - warnings: list, 警告列表
    - errors: list, 错误列表
    
    返回:
    - str: 格式化的验证消息
    """
    messages = []
    
    if errors:
        messages.append("❌ **发现致命错误：**")
        for i, error in enumerate(errors, 1):
            messages.append(f"   {i}. {error}")
    
    if warnings:
        messages.append("⚠️ **发现警告信息：**")
        for i, warning in enumerate(warnings, 1):
            messages.append(f"   {i}. {warning}")
    
    if not errors and not warnings:
        messages.append("✅ **所有输入验证通过！**")
    
    return "\n".join(messages)
