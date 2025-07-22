# -*- coding: utf-8 -*-
"""
结果分析模块 - 负责结果分析和可视化
包含KPI计算、图表生成和分析报告功能
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def calculate_kpis(results_df, economic_params):
    """
    计算关键绩效指标 (KPIs)
    
    参数:
    - results_df: pandas.DataFrame, 模拟结果数据
    - economic_params: dict, 经济参数
    
    返回:
    - dict: 包含所有KPI的字典
    """
    try:
        # 基础统计
        total_consumption_gwh = results_df['mine_load_kw'].sum() / 1_000_000  # kWh -> GWh
        total_solar_generation_gwh = results_df['solar_power_kw'].sum() / 1_000_000
        total_wind_generation_gwh = results_df['wind_power_kw'].sum() / 1_000_000
        total_renewable_generation_gwh = total_solar_generation_gwh + total_wind_generation_gwh
        
        total_grid_purchase_gwh = results_df['grid_buy_kw'].sum() / 1_000_000
        total_grid_sell_gwh = results_df['grid_sell_kw'].sum() / 1_000_000
        
        total_battery_charge_gwh = results_df['battery_charge_kw'].sum() / 1_000_000
        total_battery_discharge_gwh = results_df['battery_discharge_kw'].sum() / 1_000_000
        
        # 经济指标
        total_grid_cost = results_df['grid_cost_usd'].sum()
        total_grid_revenue = results_df['grid_revenue_usd'].sum()
        net_grid_cost = total_grid_cost - total_grid_revenue
        
        # 可再生能源渗透率
        renewable_penetration = (total_renewable_generation_gwh / total_consumption_gwh) * 100 if total_consumption_gwh > 0 else 0
        
        # 自消纳率（可再生能源直接被负荷消耗的比例）
        renewable_self_consumption = ((total_renewable_generation_gwh - total_grid_sell_gwh) / total_renewable_generation_gwh) * 100 if total_renewable_generation_gwh > 0 else 0
        
        # 电网依赖度
        grid_dependency = (total_grid_purchase_gwh / total_consumption_gwh) * 100 if total_consumption_gwh > 0 else 0
        
        # 电池效率
        battery_efficiency = (total_battery_discharge_gwh / total_battery_charge_gwh) * 100 if total_battery_charge_gwh > 0 else 0
        
        # 平均电池SOC
        avg_battery_soc = results_df['battery_soc_percent'].mean()
        
        # 电池循环次数（简化计算）
        battery_cycles = total_battery_charge_gwh / (results_df['battery_soc_kwh'].max() / 1_000_000) if results_df['battery_soc_kwh'].max() > 0 else 0
        
        # 碳排放减少（假设电网碳排放因子为0.58 kg CO2/kWh）
        carbon_emission_factor = 0.58  # kg CO2/kWh
        co2_reduction_tons = (total_renewable_generation_gwh * 1_000_000 * carbon_emission_factor) / 1000  # 转换为吨
        
        # 组装KPI字典
        kpis = {
            # 能源统计
            'total_consumption_gwh': total_consumption_gwh,
            'total_solar_generation_gwh': total_solar_generation_gwh,
            'total_wind_generation_gwh': total_wind_generation_gwh,
            'total_renewable_generation_gwh': total_renewable_generation_gwh,
            'total_grid_purchase_gwh': total_grid_purchase_gwh,
            'total_grid_sell_gwh': total_grid_sell_gwh,
            'total_battery_charge_gwh': total_battery_charge_gwh,
            'total_battery_discharge_gwh': total_battery_discharge_gwh,
            
            # 经济指标
            'total_grid_cost': total_grid_cost,
            'total_grid_revenue': total_grid_revenue,
            'net_grid_cost': net_grid_cost,
            
            # 性能指标
            'renewable_penetration': renewable_penetration,
            'renewable_self_consumption': renewable_self_consumption,
            'grid_dependency': grid_dependency,
            'battery_efficiency': battery_efficiency,
            'avg_battery_soc': avg_battery_soc,
            'battery_cycles': battery_cycles,
            
            # 环境指标
            'co2_reduction_tons': co2_reduction_tons
        }
        
        return kpis
        
    except Exception as e:
        st.error(f"KPI计算失败: {str(e)}")
        return {}

def create_kpi_dashboard(kpis):
    """
    创建KPI仪表板
    
    参数:
    - kpis: dict, KPI数据
    """
    st.subheader("📊 关键绩效指标 (KPIs)")
    
    # 创建四列布局
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="可再生能源渗透率",
            value=f"{kpis.get('renewable_penetration', 0):.1f}%",
            help="可再生能源发电量占总用电量的比例"
        )
        st.metric(
            label="年总用电量",
            value=f"{kpis.get('total_consumption_gwh', 0):.1f} GWh",
            help="矿区年度总用电量"
        )
    
    with col2:
        st.metric(
            label="自消纳率",
            value=f"{kpis.get('renewable_self_consumption', 0):.1f}%",
            help="可再生能源直接被负荷消耗的比例"
        )
        st.metric(
            label="可再生能源发电量",
            value=f"{kpis.get('total_renewable_generation_gwh', 0):.1f} GWh",
            help="光伏和风电年度总发电量"
        )
    
    with col3:
        st.metric(
            label="电网依赖度",
            value=f"{kpis.get('grid_dependency', 0):.1f}%",
            help="从电网购电量占总用电量的比例"
        )
        st.metric(
            label="电池平均SOC",
            value=f"{kpis.get('avg_battery_soc', 0):.1f}%",
            help="电池年度平均荷电状态"
        )
    
    with col4:
        st.metric(
            label="CO₂减排量",
            value=f"{kpis.get('co2_reduction_tons', 0):.0f} 吨",
            help="通过可再生能源减少的二氧化碳排放量"
        )
        st.metric(
            label="年度电网净成本",
            value=f"${kpis.get('net_grid_cost', 0):,.0f}",
            help="电网购电成本减去售电收入"
        )

def create_sankey_chart(simulation_results_df, kpi_results):
    """
    生成能源流桑基图 (Sankey Diagram)

    参数:
    - simulation_results_df: pandas.DataFrame, 包含逐时模拟结果的DataFrame
    - kpi_results: dict, 包含年度汇总值的字典

    返回:
    - plotly.graph_objects.Figure: Plotly图表对象
    """
    try:
        # 定义节点 (Nodes)
        labels = [
            "太阳能发电",    # 0
            "风力发电",      # 1
            "电网购电",      # 2
            "本地负荷",      # 3
            "储能充电",      # 4
            "电网售电"       # 5
        ]

        # 节点颜色配置
        node_colors = [
            "#FFA500",  # 太阳能发电 - 橙色
            "#87CEEB",  # 风力发电 - 天蓝色
            "#FF6B6B",  # 电网购电 - 红色
            "#4ECDC4",  # 本地负荷 - 青色
            "#45B7D1",  # 储能充电 - 蓝色
            "#96CEB4"   # 电网售电 - 绿色
        ]

        # 从模拟结果中计算年度总电量 (kWh -> GWh)
        total_solar_generation_gwh = simulation_results_df['solar_power_kw'].sum() / 1_000_000
        total_wind_generation_gwh = simulation_results_df['wind_power_kw'].sum() / 1_000_000
        total_grid_purchase_gwh = simulation_results_df['grid_buy_kw'].sum() / 1_000_000
        total_load_consumption_gwh = simulation_results_df['mine_load_kw'].sum() / 1_000_000
        total_battery_charge_gwh = simulation_results_df['battery_charge_kw'].sum() / 1_000_000
        total_grid_sell_gwh = simulation_results_df['grid_sell_kw'].sum() / 1_000_000
        total_battery_discharge_gwh = simulation_results_df['battery_discharge_kw'].sum() / 1_000_000

        # 计算详细的能量流向
        # 为了准确计算流向，我们需要逐时分析能量分配

        # 初始化流量统计
        solar_to_load = 0
        solar_to_battery = 0
        solar_to_grid = 0
        wind_to_load = 0
        wind_to_battery = 0
        wind_to_grid = 0
        grid_to_load = 0
        battery_to_load = 0

        # 逐时分析能量流向
        for i in range(len(simulation_results_df)):
            hour_data = simulation_results_df.iloc[i]

            load_kw = hour_data['mine_load_kw']
            solar_kw = hour_data['solar_power_kw']
            wind_kw = hour_data['wind_power_kw']
            battery_charge_kw = hour_data['battery_charge_kw']
            battery_discharge_kw = hour_data['battery_discharge_kw']
            grid_buy_kw = hour_data['grid_buy_kw']
            grid_sell_kw = hour_data['grid_sell_kw']

            renewable_total = solar_kw + wind_kw

            # 计算本小时的能量分配
            if renewable_total > 0:
                # 可再生能源优先满足负荷
                renewable_to_load = min(renewable_total, load_kw)

                # 按比例分配给太阳能和风能
                if renewable_total > 0:
                    solar_ratio = solar_kw / renewable_total
                    wind_ratio = wind_kw / renewable_total

                    solar_to_load += renewable_to_load * solar_ratio
                    wind_to_load += renewable_to_load * wind_ratio

                # 剩余可再生能源用于充电和售电
                remaining_renewable = renewable_total - renewable_to_load

                if remaining_renewable > 0:
                    # 充电部分
                    if battery_charge_kw > 0:
                        charge_from_renewable = min(battery_charge_kw, remaining_renewable)
                        solar_to_battery += charge_from_renewable * solar_ratio
                        wind_to_battery += charge_from_renewable * wind_ratio
                        remaining_renewable -= charge_from_renewable

                    # 售电部分
                    if remaining_renewable > 0 and grid_sell_kw > 0:
                        sell_from_renewable = min(grid_sell_kw, remaining_renewable)
                        solar_to_grid += sell_from_renewable * solar_ratio
                        wind_to_grid += sell_from_renewable * wind_ratio

            # 电网购电直接供应负荷
            grid_to_load += grid_buy_kw

            # 电池放电供应负荷
            battery_to_load += battery_discharge_kw

        # 转换为GWh
        solar_to_load /= 1_000_000
        solar_to_battery /= 1_000_000
        solar_to_grid /= 1_000_000
        wind_to_load /= 1_000_000
        wind_to_battery /= 1_000_000
        wind_to_grid /= 1_000_000
        grid_to_load /= 1_000_000
        battery_to_load /= 1_000_000

        # 定义链接 (Links)
        source = []
        target = []
        value = []

        # 太阳能发电的流向
        if solar_to_load > 0.01:  # 阈值过滤小值
            source.append(0)  # 太阳能发电
            target.append(3)  # 本地负荷
            value.append(solar_to_load)

        if solar_to_battery > 0.01:
            source.append(0)  # 太阳能发电
            target.append(4)  # 储能充电
            value.append(solar_to_battery)

        if solar_to_grid > 0.01:
            source.append(0)  # 太阳能发电
            target.append(5)  # 电网售电
            value.append(solar_to_grid)

        # 风力发电的流向
        if wind_to_load > 0.01:
            source.append(1)  # 风力发电
            target.append(3)  # 本地负荷
            value.append(wind_to_load)

        if wind_to_battery > 0.01:
            source.append(1)  # 风力发电
            target.append(4)  # 储能充电
            value.append(wind_to_battery)

        if wind_to_grid > 0.01:
            source.append(1)  # 风力发电
            target.append(5)  # 电网售电
            value.append(wind_to_grid)

        # 电网购电到本地负荷
        if grid_to_load > 0.01:
            source.append(2)  # 电网购电
            target.append(3)  # 本地负荷
            value.append(grid_to_load)

        # 储能放电到本地负荷（需要添加储能放电节点）
        if battery_to_load > 0.01:
            # 扩展节点列表以包含储能放电
            if "储能放电" not in labels:
                labels.append("储能放电")  # 6
                node_colors.append("#9B59B6")  # 紫色

            # 储能充电到储能放电的内部流动
            if total_battery_discharge_gwh > 0.01:
                source.append(4)  # 储能充电
                target.append(6)  # 储能放电
                value.append(total_battery_discharge_gwh)

            # 储能放电到本地负荷
            source.append(6)  # 储能放电
            target.append(3)  # 本地负荷
            value.append(battery_to_load)

        # 创建桑基图
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=node_colors
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=[f"rgba({int(node_colors[s][1:3], 16)}, {int(node_colors[s][3:5], 16)}, {int(node_colors[s][5:7], 16)}, 0.3)" for s in source]
            )
        )])

        # 配置图表标题和布局
        fig.update_layout(
            title_text="年度能源流向分析",
            title_x=0.5,
            title_font_size=16,
            font_size=12,
            height=500,
            margin=dict(l=0, r=0, t=50, b=0)
        )

        return fig

    except Exception as e:
        st.error(f"桑基图创建失败: {str(e)}")
        # 返回空图表
        fig = go.Figure()
        fig.update_layout(
            title_text="桑基图创建失败",
            annotations=[
                dict(
                    text=f"错误: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font_size=14
                )
            ]
        )
        return fig

def create_interactive_dispatch_curve(simulation_results_df):
    """
    创建交互式调度曲线图

    参数:
    - simulation_results_df: pandas.DataFrame, 包含逐时模拟结果的DataFrame

    返回:
    - plotly.graph_objects.Figure: Plotly图表对象
    """
    try:
        # 创建双Y轴子图
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=1, cols=1,
            specs=[[{"secondary_y": True}]],
            subplot_titles=["微电网年度调度曲线"]
        )

        # 获取时间索引
        time_index = simulation_results_df.index

        # 主Y轴 - 功率曲线 (kW)

        # 1. 矿区用电负荷
        fig.add_trace(
            go.Scatter(
                x=time_index,
                y=simulation_results_df['mine_load_kw'],
                mode='lines',
                name='矿区用电负荷',
                line=dict(color='#FF6B6B', width=2),
                hovertemplate='<b>矿区负荷</b><br>' +
                             '时间: %{x}<br>' +
                             '功率: %{y:,.0f} kW<br>' +
                             '<extra></extra>'
            ),
            secondary_y=False
        )

        # 2. 光伏发电
        fig.add_trace(
            go.Scatter(
                x=time_index,
                y=simulation_results_df['solar_power_kw'],
                mode='lines',
                name='光伏发电',
                line=dict(color='#FFA500', width=2),
                hovertemplate='<b>光伏发电</b><br>' +
                             '时间: %{x}<br>' +
                             '功率: %{y:,.0f} kW<br>' +
                             '<extra></extra>'
            ),
            secondary_y=False
        )

        # 3. 风力发电
        fig.add_trace(
            go.Scatter(
                x=time_index,
                y=simulation_results_df['wind_power_kw'],
                mode='lines',
                name='风力发电',
                line=dict(color='#87CEEB', width=2),
                hovertemplate='<b>风力发电</b><br>' +
                             '时间: %{x}<br>' +
                             '功率: %{y:,.0f} kW<br>' +
                             '<extra></extra>'
            ),
            secondary_y=False
        )

        # 4. 电网交互功率 (正数购电，负数售电)
        grid_power = simulation_results_df['grid_buy_kw'] - simulation_results_df['grid_sell_kw']
        fig.add_trace(
            go.Scatter(
                x=time_index,
                y=grid_power,
                mode='lines',
                name='电网交互功率',
                line=dict(color='#9B59B6', width=2),
                hovertemplate='<b>电网交互</b><br>' +
                             '时间: %{x}<br>' +
                             '功率: %{y:,.0f} kW<br>' +
                             '(正数=购电, 负数=售电)<br>' +
                             '<extra></extra>'
            ),
            secondary_y=False
        )

        # 5. 电池充放电功率 (正数充电，负数放电)
        battery_power = simulation_results_df['battery_charge_kw'] - simulation_results_df['battery_discharge_kw']
        fig.add_trace(
            go.Scatter(
                x=time_index,
                y=battery_power,
                mode='lines',
                name='电池充放电功率',
                line=dict(color='#45B7D1', width=2),
                hovertemplate='<b>电池功率</b><br>' +
                             '时间: %{x}<br>' +
                             '功率: %{y:,.0f} kW<br>' +
                             '(正数=充电, 负数=放电)<br>' +
                             '<extra></extra>'
            ),
            secondary_y=False
        )

        # 次Y轴 - 储能状态 (SOC %)
        fig.add_trace(
            go.Scatter(
                x=time_index,
                y=simulation_results_df['battery_soc_percent'],
                mode='lines',
                name='储能状态 (SOC)',
                line=dict(color='#2ECC71', width=3, dash='dot'),
                hovertemplate='<b>储能状态</b><br>' +
                             '时间: %{x}<br>' +
                             'SOC: %{y:.1f}%<br>' +
                             '<extra></extra>'
            ),
            secondary_y=True
        )

        # 设置X轴
        fig.update_xaxes(
            title_text="时间",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        )

        # 设置主Y轴 (功率)
        fig.update_yaxes(
            title_text="功率 (kW)",
            secondary_y=False,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(128,128,128,0.2)'
        )

        # 设置次Y轴 (SOC)
        fig.update_yaxes(
            title_text="储能状态 SOC (%)",
            secondary_y=True,
            range=[0, 100],
            showgrid=False
        )

        # 设置图表布局
        fig.update_layout(
            title={
                'text': "微电网年度调度曲线 - 交互式分析",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            height=600,
            hovermode='x unified',  # 统一悬停模式
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1
            ),
            margin=dict(l=60, r=60, t=80, b=60),
            plot_bgcolor='rgba(248,249,250,0.8)',
            paper_bgcolor='white'
        )

        # 启用交互特性
        fig.update_layout(
            # 启用缩放和平移
            dragmode='zoom',  # 默认为缩放模式
            # 显示工具栏
            showlegend=True,
            # 启用悬停
            hovermode='x unified'
        )

        # 添加范围选择器
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=7*24, label="7天", step="hour", stepmode="backward"),
                        dict(count=30*24, label="30天", step="hour", stepmode="backward"),
                        dict(count=90*24, label="90天", step="hour", stepmode="backward"),
                        dict(step="all", label="全年")
                    ])
                ),
                rangeslider=dict(visible=True, thickness=0.05),
                type="date"
            )
        )

        return fig

    except Exception as e:
        st.error(f"交互式调度曲线创建失败: {str(e)}")
        # 返回空图表
        fig = go.Figure()
        fig.update_layout(
            title_text="交互式调度曲线创建失败",
            annotations=[
                dict(
                    text=f"错误: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font_size=14
                )
            ]
        )
        return fig

def create_energy_flow_chart(kpis):
    """
    创建能量流向桑基图
    
    参数:
    - kpis: dict, KPI数据
    """
    try:
        # 桑基图数据
        labels = [
            "光伏发电", "风力发电", "电网购电",  # 源头 0,1,2
            "矿区负荷", "电池充电", "电网售电"   # 终点 3,4,5
        ]
        
        source = []
        target = []
        value = []
        
        # 光伏 -> 负荷/电池/电网
        solar_gen = kpis.get('total_solar_generation_gwh', 0)
        if solar_gen > 0:
            source.extend([0, 0, 0])
            target.extend([3, 4, 5])
            # 简化分配（实际应该根据详细数据计算）
            solar_to_load = solar_gen * 0.7
            solar_to_battery = solar_gen * 0.2
            solar_to_grid = solar_gen * 0.1
            value.extend([solar_to_load, solar_to_battery, solar_to_grid])
        
        # 风电 -> 负荷/电池/电网
        wind_gen = kpis.get('total_wind_generation_gwh', 0)
        if wind_gen > 0:
            source.extend([1, 1, 1])
            target.extend([3, 4, 5])
            wind_to_load = wind_gen * 0.7
            wind_to_battery = wind_gen * 0.2
            wind_to_grid = wind_gen * 0.1
            value.extend([wind_to_load, wind_to_battery, wind_to_grid])
        
        # 电网购电 -> 负荷
        grid_purchase = kpis.get('total_grid_purchase_gwh', 0)
        if grid_purchase > 0:
            source.append(2)
            target.append(3)
            value.append(grid_purchase)
        
        # 创建桑基图
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color=["#FFA500", "#87CEEB", "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=["rgba(255,165,0,0.3)", "rgba(135,206,235,0.3)", "rgba(255,107,107,0.3)"] * len(source)
            )
        )])
        
        fig.update_layout(
            title_text="年度能量流向分析 (GWh)",
            font_size=12,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"桑基图创建失败: {str(e)}")

def create_time_series_chart(results_df, period="week"):
    """
    创建时间序列图表
    
    参数:
    - results_df: pandas.DataFrame, 模拟结果数据
    - period: str, 显示周期 ("week", "month")
    """
    try:
        if period == "week":
            # 显示典型周（第20周）
            start_idx = 20 * 7 * 24
            end_idx = start_idx + 7 * 24
            data_subset = results_df.iloc[start_idx:end_idx]
            title = "典型周运行状态"
        else:
            # 显示典型月（6月）
            start_idx = 5 * 30 * 24
            end_idx = start_idx + 30 * 24
            data_subset = results_df.iloc[start_idx:end_idx]
            title = "典型月运行状态"
        
        # 创建子图
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('发电与负荷 (kW)', '电池状态', '电网交互 (kW)'),
            vertical_spacing=0.08
        )
        
        # 第一个子图：发电与负荷
        fig.add_trace(
            go.Scatter(x=data_subset.index, y=data_subset['mine_load_kw'], 
                      name='矿区负荷', line=dict(color='red')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=data_subset.index, y=data_subset['solar_power_kw'], 
                      name='光伏发电', line=dict(color='orange')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=data_subset.index, y=data_subset['wind_power_kw'], 
                      name='风力发电', line=dict(color='blue')),
            row=1, col=1
        )
        
        # 第二个子图：电池状态
        fig.add_trace(
            go.Scatter(x=data_subset.index, y=data_subset['battery_soc_percent'], 
                      name='电池SOC (%)', line=dict(color='green')),
            row=2, col=1
        )
        
        # 第三个子图：电网交互
        fig.add_trace(
            go.Scatter(x=data_subset.index, y=data_subset['grid_buy_kw'], 
                      name='电网购电', line=dict(color='purple')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=data_subset.index, y=-data_subset['grid_sell_kw'], 
                      name='电网售电', line=dict(color='cyan')),
            row=3, col=1
        )
        
        fig.update_layout(
            title_text=title,
            height=800,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"时间序列图表创建失败: {str(e)}")

def display_results(results_df, economic_params):
    """
    生成专业的可视化分析报告，计算KPI并创建交互式图表
    
    参数:
    - results_df: pandas.DataFrame, 模拟结果数据
    - economic_params: dict, 经济参数
    """
    try:
        st.success("✅ 模拟计算完成！以下是详细的分析结果：")
        
        # 计算KPIs
        kpis = calculate_kpis(results_df, economic_params)
        
        # 显示KPI仪表板
        create_kpi_dashboard(kpis)
        
        st.markdown("---")
        
        # 创建标签页
        tab1, tab2, tab3 = st.tabs(["📊 能量流向分析", "📈 运行状态分析", "📋 详细数据"])
        
        with tab1:
            st.subheader("🔄 年度能量流向")

            # 使用新的详细桑基图
            sankey_fig = create_sankey_chart(results_df, kpis)
            st.plotly_chart(sankey_fig, use_container_width=True)

            # 可选：也显示简化版本作为对比
            st.subheader("📊 简化能量流向")
            create_energy_flow_chart(kpis)
        
        with tab2:
            st.subheader("📈 系统运行状态")

            # 创建子标签页
            subtab1, subtab2 = st.tabs(["🔄 交互式调度曲线", "📊 典型周期分析"])

            with subtab1:
                st.subheader("🔄 年度调度曲线 - 交互式分析")
                st.info("💡 提示：使用鼠标滚轮缩放，拖拽平移，悬停查看详细数据。可使用下方时间选择器快速跳转到特定时期。")

                # 创建交互式调度曲线
                dispatch_fig = create_interactive_dispatch_curve(results_df)
                st.plotly_chart(dispatch_fig, use_container_width=True)

            with subtab2:
                st.subheader("📊 典型周期运行分析")

                # 周期选择
                period = st.selectbox("选择显示周期", ["week", "month"],
                                    format_func=lambda x: "典型周" if x == "week" else "典型月")

                create_time_series_chart(results_df, period)
        
        with tab3:
            st.subheader("📋 模拟结果详细数据")
            
            # 数据统计摘要
            st.write("**数据统计摘要：**")
            st.dataframe(results_df.describe())
            
            # 可下载的详细数据
            st.write("**详细数据预览：**")
            st.dataframe(results_df.head(100))
            
            # 数据下载
            csv = results_df.to_csv(index=True)
            st.download_button(
                label="📥 下载完整模拟数据 (CSV)",
                data=csv,
                file_name="microgrid_simulation_results.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"结果分析显示失败: {str(e)}")
