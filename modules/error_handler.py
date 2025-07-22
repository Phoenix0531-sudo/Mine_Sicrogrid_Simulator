# -*- coding: utf-8 -*-
"""
错误处理和恢复机制模块 - 提高系统稳定性
包含错误分类、自动恢复、用户友好的错误提示等功能
"""

import functools
import traceback
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Type
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import streamlit as st

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"           # 轻微错误，不影响主要功能
    MEDIUM = "medium"     # 中等错误，影响部分功能
    HIGH = "high"         # 严重错误，影响核心功能
    CRITICAL = "critical" # 致命错误，系统无法继续

class ErrorCategory(Enum):
    """错误分类"""
    VALIDATION = "validation"     # 输入验证错误
    COMPUTATION = "computation"   # 计算错误
    DATA = "data"                # 数据错误
    NETWORK = "network"          # 网络错误
    SYSTEM = "system"            # 系统错误
    USER = "user"                # 用户操作错误

@dataclass
class ErrorInfo:
    """错误信息数据类"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    technical_details: str
    timestamp: datetime
    function_name: str
    recovery_suggestions: List[str]
    auto_recoverable: bool = False

class ErrorRegistry:
    """错误注册表 - 管理已知错误类型"""
    
    def __init__(self):
        self.known_errors: Dict[Type[Exception], ErrorInfo] = {}
        self._register_common_errors()
    
    def _register_common_errors(self):
        """注册常见错误类型"""
        
        # 验证错误
        self.register_error(
            ValueError,
            ErrorCategory.VALIDATION,
            ErrorSeverity.MEDIUM,
            "输入参数不符合要求",
            ["检查输入参数的格式和范围", "参考帮助文档中的参数说明"],
            auto_recoverable=False
        )
        
        # 网络错误
        self.register_error(
            ConnectionError,
            ErrorCategory.NETWORK,
            ErrorSeverity.HIGH,
            "网络连接失败",
            ["检查网络连接", "稍后重试", "联系系统管理员"],
            auto_recoverable=True
        )
        
        # 数据错误
        self.register_error(
            KeyError,
            ErrorCategory.DATA,
            ErrorSeverity.MEDIUM,
            "数据格式错误或缺少必要字段",
            ["检查数据文件格式", "确保包含所有必要字段", "重新加载数据"],
            auto_recoverable=False
        )
        
        # 内存错误
        self.register_error(
            MemoryError,
            ErrorCategory.SYSTEM,
            ErrorSeverity.CRITICAL,
            "内存不足",
            ["减少数据集大小", "关闭其他应用程序", "重启应用"],
            auto_recoverable=False
        )
    
    def register_error(self, 
                      exception_type: Type[Exception],
                      category: ErrorCategory,
                      severity: ErrorSeverity,
                      user_message: str,
                      recovery_suggestions: List[str],
                      auto_recoverable: bool = False):
        """注册错误类型"""
        
        error_info = ErrorInfo(
            error_id=f"{category.value}_{exception_type.__name__}",
            category=category,
            severity=severity,
            message=user_message,
            technical_details="",
            timestamp=datetime.now(),
            function_name="",
            recovery_suggestions=recovery_suggestions,
            auto_recoverable=auto_recoverable
        )
        
        self.known_errors[exception_type] = error_info
    
    def get_error_info(self, exception: Exception) -> ErrorInfo:
        """获取错误信息"""
        exception_type = type(exception)
        
        if exception_type in self.known_errors:
            error_info = self.known_errors[exception_type]
            # 创建新实例以避免修改原始数据
            return ErrorInfo(
                error_id=error_info.error_id,
                category=error_info.category,
                severity=error_info.severity,
                message=error_info.message,
                technical_details=str(exception),
                timestamp=datetime.now(),
                function_name="",
                recovery_suggestions=error_info.recovery_suggestions,
                auto_recoverable=error_info.auto_recoverable
            )
        else:
            # 未知错误
            return ErrorInfo(
                error_id=f"unknown_{exception_type.__name__}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.HIGH,
                message="发生未知错误",
                technical_details=str(exception),
                timestamp=datetime.now(),
                function_name="",
                recovery_suggestions=["重试操作", "重启应用", "联系技术支持"],
                auto_recoverable=False
            )

# 全局错误注册表
error_registry = ErrorRegistry()

class RetryConfig:
    """重试配置"""
    
    def __init__(self, 
                 max_attempts: int = 3,
                 delay: float = 1.0,
                 backoff_factor: float = 2.0,
                 max_delay: float = 60.0):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay

def with_error_handling(retry_config: Optional[RetryConfig] = None,
                       show_user_message: bool = True,
                       fallback_result: Any = None):
    """
    错误处理装饰器
    
    参数:
    - retry_config: 重试配置
    - show_user_message: 是否显示用户友好的错误消息
    - fallback_result: 失败时的备用结果
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            attempts = 1
            
            if retry_config:
                max_attempts = retry_config.max_attempts
                delay = retry_config.delay
            else:
                max_attempts = 1
                delay = 0
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    error_info = error_registry.get_error_info(e)
                    error_info.function_name = func.__name__
                    
                    logger.error(f"函数 {func.__name__} 执行失败 (尝试 {attempt + 1}/{max_attempts}): {e}")
                    
                    # 如果是最后一次尝试或不可重试的错误
                    if (attempt == max_attempts - 1 or 
                        not error_info.auto_recoverable):
                        
                        if show_user_message:
                            display_error_message(error_info)
                        
                        if fallback_result is not None:
                            logger.info(f"返回备用结果: {fallback_result}")
                            return fallback_result
                        else:
                            raise e
                    
                    # 等待后重试
                    if attempt < max_attempts - 1:
                        wait_time = min(delay * (retry_config.backoff_factor ** attempt), 
                                      retry_config.max_delay)
                        logger.info(f"等待 {wait_time:.1f} 秒后重试...")
                        time.sleep(wait_time)
            
            # 如果所有重试都失败了
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator

def display_error_message(error_info: ErrorInfo):
    """显示用户友好的错误消息"""
    
    # 根据严重程度选择显示方式
    if error_info.severity == ErrorSeverity.CRITICAL:
        st.error(f"🚨 严重错误: {error_info.message}")
    elif error_info.severity == ErrorSeverity.HIGH:
        st.error(f"❌ 错误: {error_info.message}")
    elif error_info.severity == ErrorSeverity.MEDIUM:
        st.warning(f"⚠️ 警告: {error_info.message}")
    else:
        st.info(f"ℹ️ 提示: {error_info.message}")
    
    # 显示恢复建议
    if error_info.recovery_suggestions:
        with st.expander("💡 解决建议", expanded=True):
            for i, suggestion in enumerate(error_info.recovery_suggestions, 1):
                st.write(f"{i}. {suggestion}")
    
    # 显示技术详情（可折叠）
    if error_info.technical_details:
        with st.expander("🔧 技术详情", expanded=False):
            st.code(error_info.technical_details)
            st.caption(f"错误ID: {error_info.error_id}")
            st.caption(f"时间: {error_info.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

class CircuitBreaker:
    """熔断器 - 防止级联故障"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: Type[Exception] = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("熔断器开启，服务暂时不可用")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
                
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """判断是否应该尝试重置"""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """成功时的处理"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """失败时的处理"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"熔断器开启，失败次数: {self.failure_count}")

def safe_execute(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """
    安全执行函数
    
    返回:
    - tuple: (是否成功, 结果或错误信息)
    """
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        error_info = error_registry.get_error_info(e)
        logger.error(f"安全执行失败: {e}")
        return False, error_info

def create_error_recovery_ui():
    """创建错误恢复UI"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ 错误恢复")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 重试", help="重试上次失败的操作"):
            st.sidebar.info("重试功能已触发")
            # 这里可以添加重试逻辑
    
    with col2:
        if st.button("🏠 重置", help="重置应用状态"):
            # 清理session state
            for key in list(st.session_state.keys()):
                if key.startswith('error_') or key.startswith('failed_'):
                    del st.session_state[key]
            st.sidebar.success("应用状态已重置")
    
    # 错误历史
    if st.sidebar.button("📋 错误历史"):
        show_error_history()

def show_error_history():
    """显示错误历史"""
    if 'error_history' not in st.session_state:
        st.session_state.error_history = []
    
    if st.session_state.error_history:
        st.sidebar.markdown("**最近错误:**")
        for error in st.session_state.error_history[-3:]:  # 显示最近3个错误
            st.sidebar.caption(f"• {error['time']}: {error['message']}")
    else:
        st.sidebar.info("暂无错误记录")

def log_error_to_history(error_info: ErrorInfo):
    """记录错误到历史"""
    if 'error_history' not in st.session_state:
        st.session_state.error_history = []
    
    error_record = {
        'time': error_info.timestamp.strftime('%H:%M:%S'),
        'message': error_info.message,
        'severity': error_info.severity.value
    }
    
    st.session_state.error_history.append(error_record)
    
    # 保持历史记录在合理范围内
    if len(st.session_state.error_history) > 10:
        st.session_state.error_history = st.session_state.error_history[-10:]
