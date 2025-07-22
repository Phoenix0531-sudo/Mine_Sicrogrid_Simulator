# -*- coding: utf-8 -*-
"""
高级可视化模块 - 现代化图表和交互式可视化
包含3D图表、动画效果、高级交互等
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def validate_and_fix_data(simulation_results):
    """验证和修复模拟结果数据字段"""
    try:
        # 检查必需字段是否存在
        required_fields = [
            'mine_load_kw', 'solar_power_kw', 'wind_power_kw',
            'renewable_total_kw', 'grid_buy_kw', 'grid_sell_kw',
            'battery_charge_kw', 'battery_discharge_kw',
            'grid_cost_usd', 'grid_revenue_usd'
        ]

        # 添加缺失字段的默认值
        for field in required_fields:
            if field not in simulation_results.columns:
                if 'battery' in field:
                    simulation_results[field] = 0.0
                elif 'grid' in field and 'cost' in field:
                    simulation_results[field] = 0.0
                elif 'grid' in field and 'revenue' in field:
                    simulation_results[field] = 0.0
                else:
                    simulation_results[field] = 0.0
                st.warning(f"添加缺失字段 {field}，使用默认值")

        # 计算组合字段
        if 'battery_power_kw' not in simulation_results.columns:
            # 计算净电池功率（充电为负，放电为正）
            simulation_results['battery_power_kw'] = (
                simulation_results['battery_discharge_kw'] -
                simulation_results['battery_charge_kw']
            )

        return simulation_results

    except Exception as e:
        st.error(f"数据验证失败: {e}")
        return simulation_results

def create_3d_energy_flow_chart(simulation_results):
    """创建3D能量流动图表"""
    try:
        # 验证和修复数据
        simulation_results = validate_and_fix_data(simulation_results)
        # 准备数据
        hours = len(simulation_results)
        time_range = pd.date_range(start='2023-01-01', periods=hours, freq='h')
        
        # 采样数据以提高性能（显示每天的数据）
        sample_indices = range(0, hours, 24)  # 每天一个点
        sampled_data = simulation_results.iloc[sample_indices].copy()
        sampled_time = [time_range[i] for i in sample_indices]
        
        # 创建3D散点图
        fig = go.Figure()
        
        # 添加光伏发电轨迹
        fig.add_trace(go.Scatter3d(
            x=list(range(len(sampled_data))),
            y=sampled_data['solar_power_kw'],
            z=sampled_data['mine_load_kw'],
            mode='markers+lines',
            marker=dict(
                size=5,
                color=sampled_data['solar_power_kw'],
                colorscale='Viridis',
                opacity=0.8
            ),
            line=dict(color='orange', width=3),
            name='光伏发电轨迹',
            text=[f"日期: {t.strftime('%Y-%m-%d')}<br>光伏: {s:.0f}kW<br>负荷: {l:.0f}kW" 
                  for t, s, l in zip(sampled_time, sampled_data['solar_power_kw'], sampled_data['mine_load_kw'])],
            hovertemplate='%{text}<extra></extra>'
        ))
        
        # 添加风电轨迹
        fig.add_trace(go.Scatter3d(
            x=list(range(len(sampled_data))),
            y=sampled_data['wind_power_kw'],
            z=sampled_data['mine_load_kw'],
            mode='markers+lines',
            marker=dict(
                size=5,
                color=sampled_data['wind_power_kw'],
                colorscale='Blues',
                opacity=0.8
            ),
            line=dict(color='skyblue', width=3),
            name='风电轨迹',
            text=[f"日期: {t.strftime('%Y-%m-%d')}<br>风电: {w:.0f}kW<br>负荷: {l:.0f}kW" 
                  for t, w, l in zip(sampled_time, sampled_data['wind_power_kw'], sampled_data['mine_load_kw'])],
            hovertemplate='%{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title="🌐 3D能量流动轨迹分析",
            scene=dict(
                xaxis_title="时间轴 (天)",
                yaxis_title="发电功率 (kW)",
                zaxis_title="负荷功率 (kW)",
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig
        
    except Exception as e:
        st.error(f"3D图表创建失败: {e}")
        return None

def create_animated_daily_profile(simulation_results):
    """创建动画日负荷曲线"""
    try:
        # 验证和修复数据
        simulation_results = validate_and_fix_data(simulation_results)
        # 选择几个典型日期
        hours = len(simulation_results)
        days_to_show = min(30, hours // 24)  # 最多显示30天
        
        frames = []
        for day in range(days_to_show):
            start_idx = day * 24
            end_idx = start_idx + 24
            
            if end_idx <= hours:
                daily_data = simulation_results.iloc[start_idx:end_idx].copy()
                daily_data['hour'] = range(24)
                
                frame = go.Frame(
                    data=[
                        go.Scatter(
                            x=daily_data['hour'],
                            y=daily_data['mine_load_kw'],
                            mode='lines+markers',
                            name='矿区负荷',
                            line=dict(color='red', width=3),
                            marker=dict(size=8)
                        ),
                        go.Scatter(
                            x=daily_data['hour'],
                            y=daily_data['solar_power_kw'],
                            mode='lines+markers',
                            name='光伏发电',
                            line=dict(color='orange', width=3),
                            marker=dict(size=8)
                        ),
                        go.Scatter(
                            x=daily_data['hour'],
                            y=daily_data['wind_power_kw'],
                            mode='lines+markers',
                            name='风力发电',
                            line=dict(color='skyblue', width=3),
                            marker=dict(size=8)
                        )
                    ],
                    name=f"第{day+1}天"
                )
                frames.append(frame)
        
        # 创建初始图表
        initial_data = simulation_results.iloc[:24].copy()
        initial_data['hour'] = range(24)
        
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=initial_data['hour'],
                    y=initial_data['mine_load_kw'],
                    mode='lines+markers',
                    name='矿区负荷',
                    line=dict(color='red', width=3)
                ),
                go.Scatter(
                    x=initial_data['hour'],
                    y=initial_data['solar_power_kw'],
                    mode='lines+markers',
                    name='光伏发电',
                    line=dict(color='orange', width=3)
                ),
                go.Scatter(
                    x=initial_data['hour'],
                    y=initial_data['wind_power_kw'],
                    mode='lines+markers',
                    name='风力发电',
                    line=dict(color='skyblue', width=3)
                )
            ],
            frames=frames
        )
        
        # 添加播放控制
        fig.update_layout(
            title="📅 动画日负荷曲线分析",
            xaxis_title="小时",
            yaxis_title="功率 (kW)",
            height=500,
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 500, "redraw": True},
                                      "fromcurrent": True, "transition": {"duration": 300}}],
                        "label": "播放",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                        "mode": "immediate", "transition": {"duration": 0}}],
                        "label": "暂停",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }],
            sliders=[{
                "active": 0,
                "yanchor": "top",
                "xanchor": "left",
                "currentvalue": {
                    "font": {"size": 20},
                    "prefix": "天数:",
                    "visible": True,
                    "xanchor": "right"
                },
                "transition": {"duration": 300, "easing": "cubic-in-out"},
                "pad": {"b": 10, "t": 50},
                "len": 0.9,
                "x": 0.1,
                "y": 0,
                "steps": [
                    {
                        "args": [[f"第{i+1}天"], {
                            "frame": {"duration": 300, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 300}
                        }],
                        "label": f"第{i+1}天",
                        "method": "animate"
                    } for i in range(len(frames))
                ]
            }]
        )
        
        return fig
        
    except Exception as e:
        st.error(f"动画图表创建失败: {e}")
        return None

def create_heatmap_analysis(simulation_results):
    """创建热力图分析"""
    try:
        # 验证和修复数据
        simulation_results = validate_and_fix_data(simulation_results)
        # 重塑数据为24小时 x 365天的矩阵
        hours = len(simulation_results)
        days = hours // 24
        
        # 创建负荷热力图数据
        load_matrix = simulation_results['mine_load_kw'].values[:days*24].reshape(days, 24)
        solar_matrix = simulation_results['solar_power_kw'].values[:days*24].reshape(days, 24)
        wind_matrix = simulation_results['wind_power_kw'].values[:days*24].reshape(days, 24)
        
        # 创建子图
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('矿区负荷热力图', '光伏发电热力图', '风力发电热力图'),
            vertical_spacing=0.1
        )
        
        # 负荷热力图
        fig.add_trace(
            go.Heatmap(
                z=load_matrix,
                x=list(range(24)),
                y=list(range(days)),
                colorscale='Reds',
                name='负荷',
                hovertemplate='小时: %{x}<br>天数: %{y}<br>负荷: %{z:.0f}kW<extra></extra>'
            ),
            row=1, col=1
        )
        
        # 光伏热力图
        fig.add_trace(
            go.Heatmap(
                z=solar_matrix,
                x=list(range(24)),
                y=list(range(days)),
                colorscale='YlOrRd',
                name='光伏',
                hovertemplate='小时: %{x}<br>天数: %{y}<br>光伏: %{z:.0f}kW<extra></extra>'
            ),
            row=2, col=1
        )
        
        # 风电热力图
        fig.add_trace(
            go.Heatmap(
                z=wind_matrix,
                x=list(range(24)),
                y=list(range(days)),
                colorscale='Blues',
                name='风电',
                hovertemplate='小时: %{x}<br>天数: %{y}<br>风电: %{z:.0f}kW<extra></extra>'
            ),
            row=3, col=1
        )
        
        fig.update_layout(
            title="🔥 年度运行热力图分析",
            height=800,
            showlegend=False
        )
        
        # 更新x轴标签
        for i in range(1, 4):
            fig.update_xaxes(title_text="小时", row=i, col=1)
            fig.update_yaxes(title_text="天数", row=i, col=1)
        
        return fig
        
    except Exception as e:
        st.error(f"热力图创建失败: {e}")
        return None

def create_radar_chart_comparison(simulation_results):
    """创建雷达图对比分析"""
    try:
        # 验证和修复数据
        simulation_results = validate_and_fix_data(simulation_results)
        # 计算各项指标
        total_load = simulation_results['mine_load_kw'].sum()
        renewable_gen = simulation_results['renewable_total_kw'].sum()
        grid_purchase = simulation_results['grid_buy_kw'].sum()
        # 计算电池活跃周期（充电或放电时）
        battery_active = (simulation_results['battery_charge_kw'] != 0) | (simulation_results['battery_discharge_kw'] != 0)
        battery_cycles = len(simulation_results[battery_active])
        
        # 标准化指标（0-100分）
        renewable_score = min(100, (renewable_gen / total_load) * 100) if total_load > 0 else 0
        efficiency_score = min(100, ((total_load - grid_purchase) / total_load) * 100) if total_load > 0 else 0

        # 稳定性计算（避免除零错误）
        grid_buy_mean = simulation_results['grid_buy_kw'].mean()
        if grid_buy_mean > 0:
            stability_score = min(100, 100 - (simulation_results['grid_buy_kw'].std() / grid_buy_mean) * 10)
        else:
            stability_score = 100  # 如果没有购电，稳定性满分

        economics_score = max(0, 100 - (simulation_results['grid_cost_usd'].sum() / 1000))  # 简化计算
        sustainability_score = renewable_score * 0.8 + efficiency_score * 0.2
        
        categories = ['可再生能源', '能源效率', '系统稳定性', '经济性', '可持续性']
        values = [renewable_score, efficiency_score, stability_score, economics_score, sustainability_score]
        
        # 创建雷达图
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='系统性能',
            line_color='rgba(102, 126, 234, 0.8)',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        
        # 添加基准线
        benchmark_values = [70, 75, 80, 60, 70]  # 行业基准
        fig.add_trace(go.Scatterpolar(
            r=benchmark_values,
            theta=categories,
            fill='toself',
            name='行业基准',
            line_color='rgba(255, 99, 132, 0.8)',
            fillcolor='rgba(255, 99, 132, 0.1)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="📊 系统性能雷达图分析",
            height=500
        )
        
        return fig
        
    except Exception as e:
        st.error(f"雷达图创建失败: {e}")
        return None

def create_waterfall_chart(simulation_results):
    """创建瀑布图显示能量平衡"""
    try:
        # 验证和修复数据
        simulation_results = validate_and_fix_data(simulation_results)
        # 计算年度能量数据 (MWh)
        total_load = simulation_results['mine_load_kw'].sum() / 1000
        solar_gen = simulation_results['solar_power_kw'].sum() / 1000
        wind_gen = simulation_results['wind_power_kw'].sum() / 1000
        grid_purchase = simulation_results['grid_buy_kw'].sum() / 1000
        grid_sell = -simulation_results['grid_sell_kw'].sum() / 1000  # 负值表示输出
        # 计算电池损失（充放电损失）
        battery_charge_total = simulation_results['battery_charge_kw'].sum() / 1000
        battery_discharge_total = simulation_results['battery_discharge_kw'].sum() / 1000
        # 电池损失 = 充电量 * 损失率
        battery_loss = battery_charge_total * 0.15 if battery_charge_total > 0 else 0
        
        # 创建瀑布图数据
        x = ['矿区负荷', '光伏发电', '风力发电', '电网购电', '电网售电', '储能损失', '能量平衡']
        y = [total_load, -solar_gen, -wind_gen, -grid_purchase, grid_sell, battery_loss, 0]
        
        # 计算累积值
        cumulative = [total_load]
        for i in range(1, len(y)-1):
            cumulative.append(cumulative[-1] + y[i])
        cumulative.append(0)  # 最终平衡应该接近0
        
        # 创建瀑布图
        fig = go.Figure(go.Waterfall(
            name="能量平衡",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
            x=x,
            textposition="outside",
            text=[f"{abs(val):.1f} MWh" for val in y],
            y=y,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            increasing={"marker": {"color": "green"}},
            decreasing={"marker": {"color": "red"}},
            totals={"marker": {"color": "blue"}}
        ))
        
        fig.update_layout(
            title="💧 年度能量平衡瀑布图",
            showlegend=False,
            height=500,
            yaxis_title="能量 (MWh)"
        )
        
        return fig
        
    except Exception as e:
        st.error(f"瀑布图创建失败: {e}")
        return None
