# ⚡ 智能微电网规划分析平台

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)

**专业级微电网规划分析工具 | 现代化UI | 高级可视化**

</div>

## 🎯 项目简介

专业级微电网规划分析平台，集成现代化UI设计、高级可视化、异步处理等企业级功能，为矿区可再生能源系统提供全方位的设计、优化和经济性分析解决方案。

### ✨ 核心特性

- **🔋 智能系统建模** - 8760小时精确仿真，支持光伏、风电、储能系统
- **📊 高级数据分析** - 多维度KPI分析，经济性深度评估
- **🎨 现代化界面** - 企业级设计，响应式布局，智能配置向导
- **📈 专业级可视化** - 3D图表、动画分析、热力图、雷达图、瀑布图
- **🚀 高级技术特性** - 异步计算、智能错误处理、内存优化

## 🚀 快速开始

### **环境要求**
- Python 3.8+
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

### **一键启动**

#### Windows用户
```cmd
.\start.bat
```

#### 所有平台
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

### **访问应用**
启动后在浏览器访问: http://localhost:8501

## 📁 项目结构

```
智能微电网规划分析平台/
├── app.py                          # 🚀 主应用入口
├── start.bat                       # 🖱️ Windows一键启动
├── requirements.txt                # 📦 依赖包列表
├── README.md                       # 📖 项目说明
└── modules/                        # 📂 核心功能模块
    ├── config.py                   # ⚙️ 配置管理
    ├── validation.py               # ✅ 输入验证
    ├── data_handler.py             # 📊 数据处理
    ├── simulation_engine.py        # 🔬 仿真引擎
    ├── results_analyzer.py         # 📈 结果分析
    ├── ui_components.py            # 🎨 基础UI组件
    ├── advanced_ui.py              # 🎭 高级UI组件
    ├── advanced_visualization.py   # 📊 高级可视化
    ├── async_processor.py          # ⚡ 异步处理
    ├── error_handler.py            # 🛡️ 错误处理
    ├── memory_optimizer.py         # 💾 内存优化
    ├── performance.py              # 📊 性能监控
    └── utils.py                    # 🔧 通用工具
```

## 📊 使用流程

1. **📍 配置参数** - 在左侧面板设置地理位置、负荷、可再生能源、储能系统参数
2. **🚀 运行计算** - 点击"开始模拟"按钮启动8760小时精确仿真
3. **📈 查看结果** - 在多个标签页中查看KPI仪表板、3D图表、热力图等分析结果

## 🎯 核心优势

- **🔋 精确建模** - 8760小时逐时仿真，基于真实气象数据
- **🎨 现代界面** - 企业级设计，3D可视化，动画效果
- **⚡ 高性能** - 异步计算，智能缓存，内存优化
- **📊 专业分析** - 多维度KPI，经济性评估，优化建议

## 📄 许可证

MIT License
