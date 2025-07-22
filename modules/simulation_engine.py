# -*- coding: utf-8 -*-
"""
仿真引擎模块 - 负责能源建模和调度模拟
包含光伏发电、风力发电和微电网调度模拟功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import pvlib
import windpowerlib
from windpowerlib import WindTurbine, ModelChain as WindModelChain
from .config import get_config, get_wind_turbine_info
from .performance import monitor_calculation

@st.cache_data
@monitor_calculation
def calculate_solar_power(weather_data, pv_capacity_mw, latitude, longitude):
    """
    使用pvlib-python库精确模拟光伏阵列的发电性能
    
    参数:
    - weather_data: pandas.DataFrame, 包含气象数据的DataFrame
    - pv_capacity_mw: float, 光伏装机容量 (MW)
    - latitude: float, 纬度
    - longitude: float, 经度
    
    返回:
    - pandas.Series: 包含8760个光伏发电功率值的时间序列 (kW)
    """
    try:
        if pv_capacity_mw <= 0:
            # 如果装机容量为0，返回全零序列
            zero_series = pd.Series(
                data=np.zeros(len(weather_data)),
                index=weather_data.index,
                name='光伏发电功率_kW'
            )
            return zero_series
        
        # 创建地理位置对象
        location = pvlib.location.Location(
            latitude=latitude,
            longitude=longitude,
            tz='UTC'
        )
        
        # 从配置文件获取光伏系统参数
        solar_config = get_config("solar")

        # 从内置数据库获取标准光伏组件和逆变器参数
        try:
            # 尝试获取组件数据库
            cec_modules = pvlib.pvsystem.retrieve_sam('CECMod')
            cec_inverters = pvlib.pvsystem.retrieve_sam('CECInverter')

            # 查找匹配的组件
            module_params = None
            for keyword in solar_config["preferred_module_keywords"]:
                matching_modules = [name for name in cec_modules.keys() if keyword in name]
                if matching_modules:
                    module_params = cec_modules[matching_modules[0]]
                    break

            if module_params is None:
                # 如果找不到匹配的组件，使用第一个可用的组件
                first_module = list(cec_modules.keys())[0]
                module_params = cec_modules[first_module]
                st.info(f"使用pvlib组件: {first_module}")

            # 查找匹配的逆变器
            inverter_params = None
            for keyword in solar_config["preferred_inverter_keywords"]:
                matching_inverters = [name for name in cec_inverters.keys() if keyword in name]
                if matching_inverters:
                    inverter_params = cec_inverters[matching_inverters[0]]
                    break

            if inverter_params is None:
                # 如果找不到匹配的逆变器，使用第一个可用的逆变器
                first_inverter = list(cec_inverters.keys())[0]
                inverter_params = cec_inverters[first_inverter]
                st.info(f"使用pvlib逆变器: {first_inverter}")

        except Exception as e:
            st.info(f"使用配置文件中的默认光伏参数")
            # 使用配置文件中的备用参数
            module_params = solar_config["fallback_module_params"]
            inverter_params = solar_config["fallback_inverter_params"]
        
        # 计算1MW系统所需的组件数量
        # 尝试从组件参数中获取功率，否则使用配置文件中的默认值
        if 'STC' in module_params:
            module_power_w = module_params['STC']
        else:
            module_power_w = solar_config["default_module_power"]

        modules_per_mw = 1_000_000 / module_power_w  # 每MW需要的组件数
        total_modules = int(pv_capacity_mw * modules_per_mw)
        
        # 创建光伏系统对象
        modules_per_string = solar_config["modules_per_string"]

        # 计算逆变器配置
        # 每个逆变器的额定功率
        inverter_power_w = inverter_params.get('Paco', 250000)  # 默认250kW

        # 计算需要的逆变器数量
        total_dc_power = total_modules * module_power_w
        num_inverters = max(1, int(total_dc_power / inverter_power_w))

        # 每个逆变器的串数
        strings_per_inverter = max(1, int(total_modules / modules_per_string / num_inverters))

        # 如果只有一个逆变器，调整其功率以匹配系统容量
        if num_inverters == 1 and total_dc_power > inverter_power_w:
            # 创建一个虚拟的大功率逆变器
            inverter_params = inverter_params.copy()
            inverter_params['Paco'] = total_dc_power * 1.1  # 110%的直流功率
            inverter_params['Pdco'] = total_dc_power * 1.15

        system = pvlib.pvsystem.PVSystem(
            surface_tilt=solar_config["surface_tilt"],
            surface_azimuth=solar_config["surface_azimuth"],
            module_parameters=module_params,
            inverter_parameters=inverter_params,
            modules_per_string=modules_per_string,
            strings_per_inverter=strings_per_inverter,
            racking_model='open_rack',  # 安装方式
            module_type='glass_glass'   # 组件类型
        )
        
        # 创建模型链
        mc = pvlib.modelchain.ModelChain(
            system=system,
            location=location,
            aoi_model='physical',  # 入射角模型
            spectral_model='no_loss',  # 光谱模型
            name='光伏系统'
        )
        
        # 准备气象数据（pvlib需要特定的列名和单位）
        weather_pvlib = pd.DataFrame({
            'ghi': weather_data['ghi'],  # 全球水平辐射 (W/m²)
            'dni': weather_data['dni'],  # 直接法向辐射 (W/m²)
            'dhi': weather_data['dhi'],  # 散射水平辐射 (W/m²)
            'temp_air': weather_data['temperature_2m'],  # 环境温度 (°C)
            'wind_speed': weather_data['windspeed_10m']  # 风速 (m/s)
        }, index=weather_data.index)

        # 确保辐射数据为非负值
        weather_pvlib['ghi'] = weather_pvlib['ghi'].clip(lower=0)
        weather_pvlib['dni'] = weather_pvlib['dni'].clip(lower=0)
        weather_pvlib['dhi'] = weather_pvlib['dhi'].clip(lower=0)

        # 检查数据有效性
        if weather_pvlib['ghi'].sum() == 0:
            st.warning("警告：全球水平辐射数据全为0，可能影响光伏发电计算")

        # 运行模型
        try:
            mc.run_model(weather_pvlib)
        except Exception as e:
            st.error(f"pvlib模型运行失败: {e}")
            # 返回零发电量
            return pd.Series(0, index=weather_data.index, name='光伏发电功率_kW')
        
        # 提取交流电输出（W）并转换为kW
        ac_power_w = mc.results.ac
        
        # 处理可能的NaN值
        ac_power_w = ac_power_w.fillna(0)
        
        # 转换为kW
        ac_power_kw = ac_power_w / 1000
        
        # 确保输出为正值
        ac_power_kw = ac_power_kw.clip(lower=0)
        
        # 设置Series名称
        ac_power_kw.name = '光伏发电功率_kW'
        
        return ac_power_kw
        
    except Exception as e:
        st.error(f"光伏发电计算失败: {str(e)}")
        # 返回全零序列作为备选
        zero_series = pd.Series(
            data=np.zeros(len(weather_data)),
            index=weather_data.index,
            name='光伏发电功率_kW'
        )
        return zero_series


@st.cache_data
def calculate_wind_power(weather_data, turbine_model, num_turbines):
    """
    使用windpowerlib库模拟风力发电机组的发电性能

    参数:
    - weather_data: pandas.DataFrame, 包含气象数据的DataFrame
    - turbine_model: str, 风机型号
    - num_turbines: int, 风机数量

    返回:
    - pandas.Series: 包含8760个风力发电功率值的时间序列 (kW)
    """
    try:
        if num_turbines <= 0:
            # 如果风机数量为0，返回全零序列
            zero_series = pd.Series(
                data=np.zeros(len(weather_data)),
                index=weather_data.index,
                name='风力发电功率_kW'
            )
            return zero_series

        # 从配置文件获取风机参数
        try:
            turbine_info = get_wind_turbine_info(turbine_model)
            turbine_params = {
                'turbine_type': turbine_info['turbine_type'],
                'hub_height': turbine_info['hub_height']
            }
        except KeyError:
            raise ValueError(f"不支持的风机型号: {turbine_model}")

        # 创建风机对象
        wind_turbine = WindTurbine(**turbine_params)

        # 准备windpowerlib所需的气象数据格式（多级索引）
        weather_wind = pd.DataFrame({
            ('wind_speed', turbine_params['hub_height']): weather_data['windspeed_10m'],
            ('temperature', 2): weather_data['temperature_2m'],
            ('pressure', 0): 101325  # 标准大气压（Pa）
        }, index=weather_data.index)

        # 设置多级列索引
        weather_wind.columns = pd.MultiIndex.from_tuples(weather_wind.columns)

        # 创建模型链
        mc = WindModelChain(wind_turbine)

        # 运行模型
        mc.run_model(weather_wind)

        # 提取发电量（W）
        power_output_w = mc.power_output

        # 处理可能的NaN值
        power_output_w = power_output_w.fillna(0)

        # 乘以风机数量并转换为kW
        total_power_kw = (power_output_w * num_turbines) / 1000

        # 确保输出为正值
        total_power_kw = total_power_kw.clip(lower=0)

        # 设置Series名称
        total_power_kw.name = '风力发电功率_kW'

        return total_power_kw

    except Exception as e:
        st.error(f"风力发电计算失败: {str(e)}")
        # 返回全零序列作为备选
        zero_series = pd.Series(
            data=np.zeros(len(weather_data)),
            index=weather_data.index,
            name='风力发电功率_kW'
        )
        return zero_series


@st.cache_data
@monitor_calculation
def run_simulation(mine_load, solar_power, wind_power, battery_capacity_mwh, battery_power_mw, **kwargs):
    """
    模拟一年8760小时的微电网运行，记录每个小时的详细能量流向和状态

    参数:
    - mine_load: pandas.Series, 矿区负荷序列 (kW)
    - solar_power: pandas.Series, 光伏发电序列 (kW)
    - wind_power: pandas.Series, 风力发电序列 (kW)
    - battery_capacity_mwh: float, 电池容量 (MWh)
    - battery_power_mw: float, 电池最大充/放电功率 (MW)
    - **kwargs: 其他参数，如电价等

    返回:
    - pandas.DataFrame: 包含每小时详细模拟结果的DataFrame
    """
    try:
        # 提取经济参数
        grid_purchase_price = kwargs.get('grid_purchase_price', 0.15)  # $/kWh
        grid_sell_price = kwargs.get('grid_sell_price', 0.05)  # $/kWh
        round_trip_efficiency = kwargs.get('round_trip_efficiency', 0.85)  # 电池往返效率

        # 转换单位
        battery_capacity_kwh = battery_capacity_mwh * 1000  # MWh -> kWh
        battery_power_kw = battery_power_mw * 1000  # MW -> kW

        # 初始化结果存储
        results = []

        # 电池状态变量
        battery_soc_kwh = battery_capacity_kwh * 0.5  # 初始SOC为50%

        # 逐小时模拟
        for i in range(len(mine_load)):
            # 当前时刻的数据
            load_kw = mine_load.iloc[i]
            solar_kw = solar_power.iloc[i]
            wind_kw = wind_power.iloc[i]

            # 计算可再生能源总发电量
            renewable_generation_kw = solar_kw + wind_kw

            # 计算净负荷（负荷减去可再生能源发电）
            net_load_kw = load_kw - renewable_generation_kw

            # 初始化本时刻的能量流向
            battery_charge_kw = 0
            battery_discharge_kw = 0
            grid_buy_kw = 0
            grid_sell_kw = 0

            if net_load_kw > 0:
                # 电力不足，需要从电池放电或从电网购电
                # 优先使用电池
                max_discharge = min(
                    battery_power_kw,  # 电池功率限制
                    battery_soc_kwh,   # 电池可用电量限制
                    net_load_kw        # 实际需求限制
                )

                battery_discharge_kw = max_discharge
                battery_soc_kwh -= battery_discharge_kw

                # 剩余不足部分从电网购买
                remaining_deficit = net_load_kw - battery_discharge_kw
                if remaining_deficit > 0:
                    grid_buy_kw = remaining_deficit

            else:
                # 电力过剩，可以给电池充电或向电网售电
                excess_power_kw = -net_load_kw

                # 优先给电池充电
                max_charge = min(
                    battery_power_kw,  # 电池功率限制
                    (battery_capacity_kwh - battery_soc_kwh) / round_trip_efficiency,  # 电池容量限制
                    excess_power_kw    # 可用过剩电量限制
                )

                battery_charge_kw = max_charge
                battery_soc_kwh += battery_charge_kw * round_trip_efficiency

                # 剩余过剩电量向电网售电
                remaining_excess = excess_power_kw - battery_charge_kw
                if remaining_excess > 0:
                    grid_sell_kw = remaining_excess

            # 计算经济指标
            grid_cost_usd = grid_buy_kw * grid_purchase_price / 1000  # kW -> MW, $/MWh
            grid_revenue_usd = grid_sell_kw * grid_sell_price / 1000

            # 计算电池SOC百分比
            battery_soc_percent = (battery_soc_kwh / battery_capacity_kwh) * 100

            # 记录本时刻结果
            hour_result = {
                'timestamp': mine_load.index[i],
                'mine_load_kw': load_kw,
                'solar_power_kw': solar_kw,
                'wind_power_kw': wind_kw,
                'renewable_total_kw': renewable_generation_kw,
                'net_load_kw': net_load_kw,
                'battery_charge_kw': battery_charge_kw,
                'battery_discharge_kw': battery_discharge_kw,
                'battery_soc_kwh': battery_soc_kwh,
                'battery_soc_percent': battery_soc_percent,
                'grid_buy_kw': grid_buy_kw,
                'grid_sell_kw': grid_sell_kw,
                'grid_cost_usd': grid_cost_usd,
                'grid_revenue_usd': grid_revenue_usd,
                'net_grid_cost_usd': grid_cost_usd - grid_revenue_usd
            }

            results.append(hour_result)

        # 转换为DataFrame
        results_df = pd.DataFrame(results)
        results_df.set_index('timestamp', inplace=True)

        return results_df

    except Exception as e:
        st.error(f"微电网调度模拟失败: {str(e)}")
        return None
