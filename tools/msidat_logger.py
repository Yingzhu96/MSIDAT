import os
import sys
from loguru import logger

def setup_msidat_logger():
    """Setup msidat logger configuration"""
    try:
        # 移除所有已存在的处理器
        logger.configure(handlers=[], extra={})
        
        # 确定日志文件夹路径
        if getattr(sys, 'frozen', False):
            # 在打包环境中使用相对于exe的路径
            base_path = os.path.dirname(sys.executable)
        else:
            # 在开发环境中使用相对于脚本的路径
            base_path = os.path.dirname(os.path.dirname(__file__))
        
        folder_ = os.path.join(base_path, 'log')
        os.makedirs(folder_, exist_ok=True)
        
        # 日志配置
        prefix_ = os.path.sep  # 使用系统路径分隔符
        rotation_ = "1 days"
        retention_ = "30 days"
        encoding_ = "utf-8"
        backtrace_ = True
        diagnose_ = True
        
        # 日志格式
        format_ = '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> ' \
                 '| <cyan>{name}</cyan>:<cyan>{function}</cyan>:<yellow>{line}</yellow> - <level>{message}</level>'
        
        # 只在开发环境中添加控制台输出
        if not getattr(sys, 'frozen', False):
            logger.add(sys.stderr, level="INFO", format=format_, colorize=True)
        
        # 添加文件处理器
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in log_levels:
            log_file = os.path.join(folder_, f"{level.lower()}.log")
            logger.add(
                log_file,
                level=level,
                format=format_,
                colorize=False,
                rotation=rotation_,
                retention=retention_,
                encoding=encoding_,
                backtrace=backtrace_,
                diagnose=diagnose_,
                filter=lambda record, level=level: record["level"].no >= logger.level(level).no
            )
        
        logger.info("MSIDAT日志系统初始化成功")
        return True
        
    except Exception as e:
        print(f"MSIDAT日志系统初始化失败: {str(e)}")
        return False

# 初始化日志系统
setup_msidat_logger()